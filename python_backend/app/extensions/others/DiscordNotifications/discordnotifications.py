"""
Discord Notifications extension for Paymenter Python backend.
"""
from typing import Dict, Any, List
import httpx
from app.extensions.base import OtherExtension


class DiscordNotifications(OtherExtension):
    """Discord notifications integration"""
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get extension metadata"""
        return {
            'name': 'Discord Notifications',
            'description': 'Send notifications to Discord via webhooks',
            'version': '1.0.0',
            'author': 'Paymenter',
            'type': 'notification'
        }
    
    def get_config(self, values: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get configuration schema"""
        return [
            {
                'name': 'webhook_url',
                'type': 'text',
                'label': 'Webhook URL',
                'description': 'Discord webhook URL',
                'required': True
            },
            {
                'name': 'username',
                'type': 'text',
                'label': 'Bot Username',
                'description': 'Username to display for the bot',
                'default': 'Paymenter',
                'required': False
            },
            {
                'name': 'avatar_url',
                'type': 'text',
                'label': 'Avatar URL',
                'description': 'URL of the avatar image',
                'required': False
            },
            {
                'name': 'notify_new_user',
                'type': 'boolean',
                'label': 'Notify on New User',
                'description': 'Send notification when a new user registers',
                'default': True
            },
            {
                'name': 'notify_new_order',
                'type': 'boolean',
                'label': 'Notify on New Order',
                'description': 'Send notification when a new order is placed',
                'default': True
            },
            {
                'name': 'notify_payment',
                'type': 'boolean',
                'label': 'Notify on Payment',
                'description': 'Send notification when a payment is received',
                'default': True
            },
            {
                'name': 'notify_ticket',
                'type': 'boolean',
                'label': 'Notify on New Ticket',
                'description': 'Send notification when a new ticket is created',
                'default': True
            }
        ]
    
    def send_webhook(self, content: str = None, embeds: List[Dict] = None) -> Dict[str, Any]:
        """
        Send a Discord webhook.
        
        Args:
            content: Message content
            embeds: List of embed objects
            
        Returns:
            Send result
        """
        webhook_url = self.config('webhook_url')
        
        if not webhook_url:
            raise Exception("Webhook URL not configured")
        
        data = {
            'username': self.config('username', 'Paymenter'),
        }
        
        if self.config('avatar_url'):
            data['avatar_url'] = self.config('avatar_url')
        
        if content:
            data['content'] = content
        
        if embeds:
            data['embeds'] = embeds
        
        with httpx.Client() as client:
            response = client.post(webhook_url, json=data)
            
            if not response.is_success:
                raise Exception(f"Discord webhook error: {response.text}")
        
        return {
            'success': True,
            'message': 'Notification sent successfully'
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the notification.
        
        Args:
            event: Event type (new_user, new_order, payment, ticket)
            data: Event data
            
        Returns:
            Execution result
        """
        event = kwargs.get('event')
        data = kwargs.get('data', {})
        
        # Check if this event type should trigger a notification
        notify_key = f"notify_{event}"
        if not self.config(notify_key, True):
            return {'success': True, 'message': 'Notification disabled for this event type'}
        
        # Build embed based on event type
        embed = self._build_embed(event, data)
        
        if embed:
            return self.send_webhook(embeds=[embed])
        
        return {'success': True, 'message': 'No notification sent'}
    
    def _build_embed(self, event: str, data: Dict) -> Dict:
        """Build Discord embed for the event"""
        if event == 'new_user':
            return {
                'title': '🆕 New User Registration',
                'description': f"User **{data.get('name')}** has registered",
                'color': 0x00FF00,  # Green
                'fields': [
                    {
                        'name': 'Email',
                        'value': data.get('email', 'N/A'),
                        'inline': True
                    },
                    {
                        'name': 'User ID',
                        'value': str(data.get('id', 'N/A')),
                        'inline': True
                    }
                ],
                'timestamp': data.get('created_at')
            }
        
        elif event == 'new_order':
            return {
                'title': '🛒 New Order',
                'description': f"Order **#{data.get('id')}** has been placed",
                'color': 0x0099FF,  # Blue
                'fields': [
                    {
                        'name': 'Customer',
                        'value': data.get('customer_name', 'N/A'),
                        'inline': True
                    },
                    {
                        'name': 'Total',
                        'value': f"{data.get('currency', 'USD')} {data.get('total', 0)}",
                        'inline': True
                    }
                ],
                'timestamp': data.get('created_at')
            }
        
        elif event == 'payment':
            return {
                'title': '💰 Payment Received',
                'description': f"Payment for invoice **#{data.get('invoice_id')}**",
                'color': 0x00FF00,  # Green
                'fields': [
                    {
                        'name': 'Amount',
                        'value': f"{data.get('currency', 'USD')} {data.get('amount', 0)}",
                        'inline': True
                    },
                    {
                        'name': 'Customer',
                        'value': data.get('customer_name', 'N/A'),
                        'inline': True
                    }
                ],
                'timestamp': data.get('paid_at')
            }
        
        elif event == 'ticket':
            return {
                'title': '🎫 New Support Ticket',
                'description': f"Ticket **#{data.get('id')}**: {data.get('subject')}",
                'color': 0xFF9900,  # Orange
                'fields': [
                    {
                        'name': 'User',
                        'value': data.get('user_name', 'N/A'),
                        'inline': True
                    },
                    {
                        'name': 'Priority',
                        'value': data.get('priority', 'normal').title(),
                        'inline': True
                    }
                ],
                'timestamp': data.get('created_at')
            }
        
        return None
