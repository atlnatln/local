"""
Views for payment operations.
Handles payment intent creation, confirmation, and status checking.
"""

import logging
import uuid
from decimal import Decimal
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import PaymentIntent, PaymentTransaction
from .serializers import (
    PaymentIntentSerializer,
    PaymentIntentCreateSerializer,
    PaymentIntentConfirmSerializer,
    PaymentTransactionSerializer,
    PaymentListSerializer,
)
from .iyzico import IyzicoClient, IyzicoError

logger = logging.getLogger(__name__)


class PaymentIntentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment intents.
    
    Endpoints:
    - POST /api/payments/intents/ - Create new payment intent
    - GET /api/payments/intents/ - List user's payment intents
    - GET /api/payments/intents/{id}/ - Get payment intent details
    - POST /api/payments/intents/{id}/confirm/ - Confirm payment
    - POST /api/payments/intents/{id}/status/ - Check payment status
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return payment intents for current user only."""
        user = getattr(self.request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return PaymentIntent.objects.none()
        return PaymentIntent.objects.filter(user=user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PaymentIntentCreateSerializer
        elif self.action == 'confirm':
            return PaymentIntentConfirmSerializer
        elif self.action == 'list':
            return PaymentListSerializer
        return PaymentIntentSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new payment intent and return Iyzico checkout form.
        
        Request body:
        {
            "amount": "99.00",
            "credits": 1000,
            "package_type": "starter" (optional)
        }
        
        Response:
        {
            "id": "uuid",
            "checkoutFormContent": "<html>...</html>",
            "token": "token",
            "status": "PENDING"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        credits = serializer.validated_data['credits']
        
        try:
            with transaction.atomic():
                # Create payment intent
                conversation_id = str(uuid.uuid4())
                payment_intent = PaymentIntent.objects.create(
                    user=request.user,
                    amount=amount,
                    credits=credits,
                    conversation_id=conversation_id,
                    status='PENDING',
                )
                
                # Initialize Iyzico client
                iyzico_client = IyzicoClient()
                
                # Create payment on Iyzico
                iyzico_response = iyzico_client.create_payment(
                    conversation_id=conversation_id,
                    amount=amount,
                    user_id=request.user.id,
                    user_email=request.user.email,
                    user_name=f"{request.user.first_name} {request.user.last_name}",
                )
                
                if not iyzico_response['success']:
                    raise IyzicoError("Failed to create payment on Iyzico")
                
                # Return response
                return Response({
                    'id': str(payment_intent.id),
                    'checkoutFormContent': iyzico_response['checkoutFormContent'],
                    'token': iyzico_response['token'],
                    'status': 'PENDING',
                    'amount': str(amount),
                    'credits': credits,
                }, status=status.HTTP_201_CREATED)
        
        except IyzicoError as e:
            logger.error(f"Iyzico error for user {request.user.id}: {str(e)}")
            return Response(
                {'error': 'Payment initialization failed. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Payment creation error: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        """
        Confirm a payment after user completes Iyzico form.
        
        Request body:
        {
            "token": "iyzico_token",
            "conversation_id": "conversation_id"
        }
        
        Response:
        {
            "id": "uuid",
            "status": "COMPLETED",
            "credits_added": 1000,
            "message": "Payment successful"
        }
        """
        payment_intent = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        conversation_id = serializer.validated_data['conversation_id']
        
        try:
            with transaction.atomic():
                # Verify conversation_id matches
                if payment_intent.conversation_id != conversation_id:
                    return Response(
                        {'error': 'Conversation ID mismatch'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Initialize Iyzico client
                iyzico_client = IyzicoClient()
                
                # Confirm payment on Iyzico
                iyzico_response = iyzico_client.confirm_payment(
                    conversation_id=conversation_id,
                    token=token,
                )
                
                if not iyzico_response['success']:
                    # Mark intent as failed
                    payment_intent.status = 'FAILED'
                    payment_intent.error_message = 'Payment confirmation failed'
                    payment_intent.save()
                    
                    return Response(
                        {'error': 'Payment confirmation failed'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create transaction record
                transaction_obj = PaymentTransaction.objects.create(
                    intent=payment_intent,
                    iyzico_transaction_id=iyzico_response['transactionId'],
                    iyzico_payment_id=iyzico_response['paymentId'],
                    iyzico_conversation_id=conversation_id,
                    card_last_four=iyzico_response.get('cardLastFour'),
                    card_bin=iyzico_response.get('cardBin'),
                    status='success',
                    amount=iyzico_response['amount'],
                    fees=iyzico_response.get('fee', 0),
                )
                
                # Mark intent as completed
                # First save payment_id, then mark_completed() saves status + completed_at
                payment_intent.payment_id = iyzico_response['paymentId']
                payment_intent.save(update_fields=['payment_id', 'updated_at'])
                payment_intent.mark_completed()
                
                # Credits are granted via post_save signal (grant_credits_on_payment_completion)
                # which is triggered by mark_completed()'s save(update_fields=['status', ...])
                logger.info(
                    f"Payment confirmed: user={request.user.id}, "
                    f"amount={payment_intent.amount}, credits={payment_intent.credits}"
                )
                
                return Response({
                    'id': str(payment_intent.id),
                    'status': 'COMPLETED',
                    'credits_added': payment_intent.credits,
                    'message': 'Payment successful. Credits have been added to your account.',
                }, status=status.HTTP_200_OK)
        
        except IyzicoError as e:
            logger.error(f"Iyzico confirmation error: {str(e)}")
            payment_intent.status = 'FAILED'
            payment_intent.error_message = str(e)
            payment_intent.save()
            
            return Response(
                {'error': 'Payment confirmation failed. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Payment confirmation error: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='status')
    def status(self, request, pk=None):
        """
        Check the status of a payment intent.
        
        Response:
        {
            "id": "uuid",
            "status": "COMPLETED|PENDING|FAILED",
            "created_at": "2024-01-01T12:00:00Z",
            "completed_at": "2024-01-01T12:05:00Z"
        }
        """
        payment_intent = self.get_object()
        
        return Response({
            'id': str(payment_intent.id),
            'status': payment_intent.status,
            'created_at': payment_intent.created_at,
            'completed_at': payment_intent.completed_at,
            'amount': str(payment_intent.amount),
            'credits': payment_intent.credits,
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """
        Get payment history for the current user.
        
        Query params:
        - status: Filter by status (PENDING, COMPLETED, FAILED, CANCELLED)
        - limit: Number of results to return (default: 10)
        - offset: Pagination offset (default: 0)
        
        Response:
        {
            "count": 5,
            "results": [
                {
                    "id": "uuid",
                    "amount": "99.00",
                    "credits": 1000,
                    "status": "COMPLETED",
                    "created_at": "2024-01-01T12:00:00Z"
                }
            ]
        }
        """
        queryset = self.get_queryset()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Pagination
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))
        
        total_count = queryset.count()
        payments = queryset[offset:offset + limit]
        
        serializer = PaymentListSerializer(payments, many=True)
        
        return Response({
            'count': total_count,
            'results': serializer.data,
        }, status=status.HTTP_200_OK)
