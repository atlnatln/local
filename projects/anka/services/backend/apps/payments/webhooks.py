"""
Webhook handlers for Iyzico payment notifications.
"""

import logging
import json
import base64
import hashlib
import hmac
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from .models import PaymentIntent, PaymentTransaction, PaymentWebhook

logger = logging.getLogger(__name__)


def _get_first_header(request, header_names: list[str]) -> str:
    for header_name in header_names:
        value = request.headers.get(header_name)
        if value:
            return value.strip()
    return ''


def _normalize_signature(value: str) -> str:
    if not value:
        return ''
    normalized = value.strip()
    if '=' in normalized:
        normalized = normalized.split('=', 1)[1].strip()
    return normalized


def _verify_webhook_signature(request) -> bool:
    secret = getattr(settings, 'IYZICO_WEBHOOK_SECRET', '')
    if not secret:
        return True

    signature = _normalize_signature(
        _get_first_header(
            request,
            [
                'X-IYZICO-SIGNATURE',
                'X-IYZICO-SIGNATURE-V2',
                'X-IYZI-SIGNATURE',
                'X-IYZI-SIGNATURE-V2',
            ],
        )
    )
    if not signature:
        return False

    timestamp = _get_first_header(
        request,
        [
            'X-IYZICO-TIMESTAMP',
            'X-IYZI-TIMESTAMP',
            'X-TIMESTAMP',
        ],
    )

    body = request.body or b''
    candidates = [body]
    if timestamp:
        timestamp_bytes = timestamp.encode('utf-8')
        candidates.append(timestamp_bytes + b'.' + body)
        candidates.append(timestamp_bytes + body)

    secret_bytes = str(secret).encode('utf-8')
    expected_values = set()
    for candidate in candidates:
        digest = hmac.new(secret_bytes, candidate, hashlib.sha256).digest()
        expected_values.add(digest.hex())
        expected_values.add(base64.b64encode(digest).decode('ascii'))

    return any(hmac.compare_digest(signature, expected) for expected in expected_values)


@csrf_exempt
def iyzico_webhook_handler(request):
    """
    Handle webhook notifications from Iyzico.
    
    Webhook structure from Iyzico:
    {
        "id": "webhook_id",
        "eventType": "payment.completed",
        "eventTime": 1640000000,
        "data": {
            "paymentId": "123456",
            "conversationId": "conv123",
            "status": "SUCCESS",
            ...
        }
    }
    """
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if not _verify_webhook_signature(request):
        logger.warning('Rejected Iyzico webhook due to invalid or missing signature')
        return JsonResponse({'error': 'Invalid webhook signature'}, status=401)
    
    try:
        # Parse request body
        payload = json.loads(request.body)
        
        event_type = payload.get('eventType', '')
        conversation_id = payload.get('data', {}).get('conversationId', '')
        
        # Store webhook for audit trail
        webhook = PaymentWebhook.objects.create(
            event_type=event_type,
            conversation_id=conversation_id,
            payload=payload,
            processed=False,
        )
        
        # Process different webhook events
        if event_type == 'payment.completed':
            _handle_payment_completed(payload, webhook)
        elif event_type == 'payment.failed':
            _handle_payment_failed(payload, webhook)
        elif event_type == 'payment.refunded':
            _handle_payment_refunded(payload, webhook)
        else:
            logger.warning(f"Unknown webhook event type: {event_type}")
        
        # Mark webhook as processed
        webhook.mark_processed()
        
        # Return success to Iyzico
        return JsonResponse({'status': 'success'}, status=200)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook request")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.exception(f"Webhook processing error: {str(e)}")
        # Mark as failed
        if 'webhook' in locals():
            webhook.processing_error = str(e)
            webhook.save()
        return JsonResponse({'status': 'error'}, status=500)


def _handle_payment_completed(payload: dict, webhook: PaymentWebhook):
    """Handle payment.completed webhook."""
    
    try:
        data = payload.get('data', {})
        conversation_id = data.get('conversationId')
        payment_id = data.get('paymentId')
        status = data.get('status')
        
        # Find payment intent
        payment_intent = PaymentIntent.objects.get(conversation_id=conversation_id)
        
        # Only process if status is SUCCESS
        if status == 'SUCCESS':
            with transaction.atomic():
                # Update intent
                payment_intent.payment_id = payment_id
                payment_intent.status = 'completed'
                payment_intent.mark_completed()
                
                # Create transaction record if not exists
                if not PaymentTransaction.objects.filter(
                    iyzico_payment_id=payment_id
                ).exists():
                    PaymentTransaction.objects.create(
                        intent=payment_intent,
                        iyzico_payment_id=payment_id,
                        iyzico_conversation_id=conversation_id,
                        iyzico_transaction_id=data.get('transactionId', ''),
                        card_last_four=data.get('cardLastFour'),
                        card_bin=data.get('cardBin'),
                        status='success',
                        amount=payment_intent.amount,
                        fees=data.get('fee', 0),
                    )
                
                # Credits will be granted via signal
                logger.info(
                    f"Payment completed via webhook: user={payment_intent.user.id}, "
                    f"credits={payment_intent.credits}"
                )
        else:
            # Mark as failed
            payment_intent.status = 'failed'
            payment_intent.error_message = f"Webhook status: {status}"
            payment_intent.save()
            logger.warning(f"Payment failed via webhook: {conversation_id}")
    
    except PaymentIntent.DoesNotExist:
        logger.error(f"Payment intent not found for conversation: {conversation_id}")
    except Exception as e:
        logger.exception(f"Error handling payment completed: {str(e)}")
        raise


def _handle_payment_failed(payload: dict, webhook: PaymentWebhook):
    """Handle payment.failed webhook."""
    
    try:
        data = payload.get('data', {})
        conversation_id = data.get('conversationId')
        error_message = data.get('errorMessage', 'Unknown error')
        
        # Find and update payment intent
        payment_intent = PaymentIntent.objects.get(conversation_id=conversation_id)
        payment_intent.status = 'failed'
        payment_intent.error_message = error_message
        payment_intent.error_code = data.get('errorCode')
        payment_intent.save()
        
        logger.warning(f"Payment failed via webhook: {conversation_id} - {error_message}")
    
    except PaymentIntent.DoesNotExist:
        logger.error(f"Payment intent not found for conversation: {conversation_id}")
    except Exception as e:
        logger.exception(f"Error handling payment failed: {str(e)}")
        raise


def _handle_payment_refunded(payload: dict, webhook: PaymentWebhook):
    """Handle payment.refunded webhook."""
    
    try:
        data = payload.get('data', {})
        payment_id = data.get('paymentId')
        
        # Find transaction
        transaction_obj = PaymentTransaction.objects.get(iyzico_payment_id=payment_id)
        transaction_obj.status = 'REFUNDED'
        transaction_obj.save()
        
        # Update intent
        intent = transaction_obj.payment_intent
        intent.status = 'REFUNDED'
        intent.save()
        
        logger.info(f"Payment refunded via webhook: {payment_id}")
    
    except PaymentTransaction.DoesNotExist:
        logger.error(f"Payment transaction not found for payment_id: {payment_id}")
    except Exception as e:
        logger.exception(f"Error handling payment refunded: {str(e)}")
        raise
