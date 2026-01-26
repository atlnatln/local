"""
Iyzico payment gateway integration.
Wraps the iyzipay SDK for creating and confirming payments.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional
import iyzipay
from django.conf import settings

logger = logging.getLogger(__name__)


class IyzicoError(Exception):
    """Custom exception for Iyzico integration errors."""
    pass


class IyzicoClient:
    """
    Wrapper around Iyzico payment gateway.
    Handles payment intent creation and confirmation.
    """
    
    def __init__(self):
        """Initialize Iyzico client with API credentials from settings."""
        self.api_key = settings.IYZICO_API_KEY
        self.secret_key = settings.IYZICO_SECRET_KEY
        self.base_url = settings.IYZICO_BASE_URL
        
        # Validate credentials are set
        if not all([self.api_key, self.secret_key]):
            raise IyzicoError("Iyzico API credentials not configured in settings")
        
        # Configure iyzipay SDK
        iyzipay.api_key = self.api_key
        iyzipay.secret_key = self.secret_key
        iyzipay.base_url = self.base_url
    
    def create_payment(
        self,
        conversation_id: str,
        amount: Decimal,
        user_id: int,
        user_email: str,
        user_name: str,
        basket_items: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment request on Iyzico.
        
        Args:
            conversation_id: Unique conversation ID for tracking
            amount: Payment amount in TRY (e.g., 99.00)
            user_id: Django user ID
            user_email: User email
            user_name: User full name
            basket_items: Optional list of items in basket
        
        Returns:
            Dictionary containing Iyzico response with checkoutFormContent
        
        Raises:
            IyzicoError: If payment creation fails
        """
        try:
            # Default basket item if not provided
            if not basket_items:
                basket_items = [{
                    'id': '1',
                    'name': 'Credits',
                    'category1': 'Services',
                    'itemType': 'VIRTUAL',
                    'price': str(amount),
                }]
            
            # Prepare payment request
            request = {
                'locale': 'tr',
                'conversationId': conversation_id,
                'price': str(amount),
                'paidPrice': str(amount),
                'currency': 'TRY',
                'installment': '1',
                'paymentChannel': 'WEB',
                'paymentGroup': 'PRODUCT',
                'paymentCard': {
                    'cardUserKey': str(user_id),
                },
                'buyer': {
                    'id': str(user_id),
                    'name': user_name.split()[0] if user_name else 'User',
                    'surname': user_name.split()[1] if len(user_name.split()) > 1 else 'User',
                    'gsmNumber': '',
                    'email': user_email,
                    'identityNumber': '',
                    'lastLoginDate': '',
                    'creationDate': '',
                    'creationAddress': '',
                },
                'shippingAddress': {
                    'contactName': user_name,
                    'city': '',
                    'country': 'Turkey',
                    'address': '',
                    'zipCode': '',
                },
                'billingAddress': {
                    'contactName': user_name,
                    'city': '',
                    'country': 'Turkey',
                    'address': '',
                    'zipCode': '',
                },
                'basketItems': basket_items,
                'callbackUrl': settings.IYZICO_CALLBACK_URL,
            }
            
            # Create payment request
            response = iyzipay.CheckoutFormInitialize().create(request)
            
            # Parse and validate response
            if response.get('status') == 'success':
                logger.info(f"Payment intent created: {conversation_id}")
                return {
                    'success': True,
                    'checkoutFormContent': response.get('checkoutFormContent'),
                    'token': response.get('token'),
                }
            else:
                error_msg = response.get('errorMessage', 'Unknown error')
                logger.error(f"Payment creation failed: {conversation_id} - {error_msg}")
                raise IyzicoError(error_msg)
        
        except Exception as e:
            logger.exception(f"Iyzico payment creation error: {str(e)}")
            raise IyzicoError(f"Payment creation failed: {str(e)}")
    
    def confirm_payment(
        self,
        conversation_id: str,
        token: str,
    ) -> Dict[str, Any]:
        """
        Confirm a payment after user completes Iyzico form.
        
        Args:
            conversation_id: Unique conversation ID
            token: Token from Iyzico form
        
        Returns:
            Dictionary containing payment confirmation response
        
        Raises:
            IyzicoError: If confirmation fails
        """
        try:
            request = {
                'locale': 'tr',
                'conversationId': conversation_id,
                'token': token,
            }
            
            # Confirm payment
            response = iyzipay.CheckoutForm().retrieve(request)
            
            # Parse response
            if response.get('status') == 'success':
                logger.info(f"Payment confirmed: {conversation_id}")
                return {
                    'success': True,
                    'paymentId': response.get('paymentId'),
                    'status': response.get('paymentStatus'),
                    'transactionId': response.get('paymentId'),
                    'amount': Decimal(response.get('paidPrice', 0)),
                    'cardLastFour': response.get('cardLastFour'),
                    'cardBin': response.get('cardBin'),
                }
            else:
                error_msg = response.get('errorMessage', 'Payment confirmation failed')
                logger.error(f"Payment confirmation failed: {conversation_id} - {error_msg}")
                raise IyzicoError(error_msg)
        
        except Exception as e:
            logger.exception(f"Iyzico payment confirmation error: {str(e)}")
            raise IyzicoError(f"Payment confirmation failed: {str(e)}")
    
    def refund_payment(
        self,
        conversation_id: str,
        payment_id: str,
        amount: Decimal,
    ) -> Dict[str, Any]:
        """
        Refund a completed payment.
        
        Args:
            conversation_id: Unique conversation ID
            payment_id: Iyzico payment ID
            amount: Refund amount in TRY
        
        Returns:
            Dictionary containing refund response
        
        Raises:
            IyzicoError: If refund fails
        """
        try:
            request = {
                'locale': 'tr',
                'conversationId': conversation_id,
                'paymentId': payment_id,
                'ip': '127.0.0.1',
                'price': str(amount),
                'currency': 'TRY',
            }
            
            # Create refund
            response = iyzipay.Refund().create(request)
            
            if response.get('status') == 'success':
                logger.info(f"Refund processed: {conversation_id} - {payment_id}")
                return {
                    'success': True,
                    'refundId': response.get('refundId'),
                }
            else:
                error_msg = response.get('errorMessage', 'Refund failed')
                logger.error(f"Refund failed: {conversation_id} - {error_msg}")
                raise IyzicoError(error_msg)
        
        except Exception as e:
            logger.exception(f"Iyzico refund error: {str(e)}")
            raise IyzicoError(f"Refund failed: {str(e)}")
