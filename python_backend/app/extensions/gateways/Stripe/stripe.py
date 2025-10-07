"""
Stripe payment gateway extension for Paymenter Python backend.
"""
from typing import Dict, Any, List
import httpx
from app.extensions.base import GatewayExtension


class Stripe(GatewayExtension):
    """Stripe payment gateway integration"""
    
    API_VERSION = '2025-07-30.basil'
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get extension metadata"""
        return {
            'name': 'Stripe',
            'description': 'Stripe payment gateway integration',
            'version': '1.0.0',
            'author': 'Paymenter',
            'type': 'gateway'
        }
    
    def get_config(self, values: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get configuration schema"""
        return [
            {
                'name': 'secret_key',
                'type': 'password',
                'label': 'Secret Key',
                'description': 'Stripe secret key (sk_...)',
                'required': True
            },
            {
                'name': 'publishable_key',
                'type': 'text',
                'label': 'Publishable Key',
                'description': 'Stripe publishable key (pk_...)',
                'required': True
            },
            {
                'name': 'webhook_secret',
                'type': 'password',
                'label': 'Webhook Secret',
                'description': 'Stripe webhook signing secret',
                'required': False
            },
            {
                'name': 'mode',
                'type': 'select',
                'label': 'Mode',
                'description': 'Payment or subscription mode',
                'options': [
                    {'value': 'payment', 'label': 'One-time payment'},
                    {'value': 'subscription', 'label': 'Subscription'}
                ],
                'default': 'payment',
                'required': True
            }
        ]
    
    def request(self, url: str, method: str = 'GET', data: Dict = None) -> Dict:
        """
        Make a request to Stripe API.
        
        Args:
            url: API endpoint URL
            method: HTTP method
            data: Request data
            
        Returns:
            API response dictionary
        """
        secret_key = self.config('secret_key')
        
        if not url.startswith('http'):
            url = f"https://api.stripe.com/v1{url}"
        
        headers = {
            'Authorization': f'Bearer {secret_key}',
            'Stripe-Version': self.API_VERSION,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        with httpx.Client() as client:
            if method.upper() == 'GET':
                response = client.get(url, headers=headers, params=data or {})
            elif method.upper() == 'POST':
                response = client.post(url, headers=headers, data=data or {})
            elif method.upper() == 'DELETE':
                response = client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if not response.is_success:
                error = response.json().get('error', {}).get('message', response.text)
                raise Exception(f"Stripe API Error: {error}")
            
            return response.json() or {}
    
    def pay(self, invoice) -> Dict[str, Any]:
        """
        Initiate payment for an invoice.
        
        Args:
            invoice: Invoice model instance
            
        Returns:
            Payment initiation result with checkout URL
        """
        mode = self.config('mode', 'payment')
        
        # Create line items from invoice items
        line_items = []
        for item in invoice.items:
            line_items.append({
                'price_data': {
                    'currency': invoice.currency_code.lower(),
                    'product_data': {
                        'name': item.description,
                    },
                    'unit_amount': int(item.price * 100),  # Convert to cents
                },
                'quantity': item.quantity,
            })
        
        # Create checkout session
        session_data = {
            'mode': mode,
            'line_items': line_items,
            'success_url': self.config('success_url', f'{self.config("base_url")}/invoice/{invoice.id}/success'),
            'cancel_url': self.config('cancel_url', f'{self.config("base_url")}/invoice/{invoice.id}'),
            'client_reference_id': str(invoice.id),
            'metadata': {
                'invoice_id': str(invoice.id),
                'user_id': str(invoice.user_id)
            }
        }
        
        session = self.request('/checkout/sessions', method='POST', data=session_data)
        
        return {
            'success': True,
            'redirect_url': session.get('url'),
            'session_id': session.get('id'),
            'status': 'pending'
        }
    
    def webhook(self, request: Any) -> Dict[str, Any]:
        """
        Handle webhook from Stripe.
        
        Args:
            request: HTTP request object
            
        Returns:
            Webhook processing result
        """
        import hmac
        import hashlib
        import json
        
        webhook_secret = self.config('webhook_secret')
        
        # Verify webhook signature if secret is configured
        if webhook_secret:
            signature = request.headers.get('Stripe-Signature', '')
            payload = request.body
            
            # Parse signature
            sig_parts = dict(item.split('=') for item in signature.split(','))
            timestamp = sig_parts.get('t')
            signatures = sig_parts.get('v1', '').split(',')
            
            # Verify signature
            signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
            expected_sig = hmac.new(
                webhook_secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if expected_sig not in signatures:
                raise Exception("Invalid webhook signature")
        
        # Parse event
        event = json.loads(request.body)
        event_type = event.get('type')
        
        # Handle different event types
        if event_type == 'checkout.session.completed':
            session = event.get('data', {}).get('object', {})
            invoice_id = session.get('metadata', {}).get('invoice_id')
            
            return {
                'success': True,
                'event': event_type,
                'invoice_id': invoice_id,
                'status': 'paid'
            }
        
        return {
            'success': True,
            'event': event_type,
            'status': 'processed'
        }
    
    def refund(self, transaction) -> Dict[str, Any]:
        """
        Refund a transaction.
        
        Args:
            transaction: Transaction model instance
            
        Returns:
            Refund result
        """
        charge_id = transaction.transaction_id
        amount = int(transaction.amount * 100)  # Convert to cents
        
        refund = self.request('/refunds', method='POST', data={
            'charge': charge_id,
            'amount': amount
        })
        
        return {
            'success': True,
            'refund_id': refund.get('id'),
            'status': refund.get('status'),
            'amount': transaction.amount
        }
