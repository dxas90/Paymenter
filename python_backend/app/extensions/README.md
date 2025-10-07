# Paymenter Python Backend - Extensions System

## Overview

The Python backend includes a comprehensive extension system that mirrors the PHP Laravel backend's extension functionality. Extensions allow you to integrate third-party services for server provisioning, payment processing, and other features.

## Extension Categories

### 1. Server Extensions (`servers/`)
Server extensions handle automated service provisioning with hosting control panels and virtualization platforms.

**Implemented:**
- **Proxmox** - Proxmox Virtual Environment integration

**Planned (from PHP backend):**
- Pterodactyl - Game server management
- CPanel - Web hosting control panel
- Plesk - Web hosting control panel
- DirectAdmin - Web hosting control panel
- Virtualizor - VPS management
- Convoy - Docker container management
- Virtfusion - VPS management
- Enhance - Web hosting control panel

### 2. Gateway Extensions (`gateways/`)
Gateway extensions handle payment processing integration.

**Implemented:**
- **Stripe** - Stripe payment processing with checkout sessions

**Planned (from PHP backend):**
- PayPal - PayPal payments
- PayPal IPN - PayPal instant payment notifications
- Mollie - Mollie payment gateway

### 3. Other Extensions (`others/`)
Other extensions provide additional functionality like notifications and integrations.

**Implemented:**
- **Discord Notifications** - Send notifications to Discord via webhooks

**Planned (from PHP backend):**
- Affiliates - Affiliate system
- Announcements - Announcement system

## Architecture

### Base Classes

All extensions inherit from base classes that define the interface:

```python
from app.extensions.base import ServerExtension, GatewayExtension, OtherExtension

class MyServer(ServerExtension):
    def create(self, service):
        # Provision a new service
        pass
    
    def suspend(self, service):
        # Suspend a service
        pass
    
    def terminate(self, service):
        # Terminate a service
        pass
```

### Extension Loader

The `ExtensionManager` class automatically discovers and loads extensions:

```python
from app.extensions.loader import extension_manager

# Get an extension instance
proxmox = extension_manager.get_extension('servers', 'proxmox', config={
    'host': 'proxmox.example.com',
    'port': 8006,
    'username': 'api_token',
    'password': 'secret'
})

# Use the extension
result = proxmox.create(service)
```

## API Endpoints

### List All Extensions
```
GET /api/v1/admin/extensions
```

Response:
```json
{
  "servers": ["proxmox"],
  "gateways": ["stripe"],
  "others": ["discordnotifications"]
}
```

### List Extensions by Category
```
GET /api/v1/admin/extensions/{category}
```

Example: `GET /api/v1/admin/extensions/servers`

### Get Extension Metadata
```
GET /api/v1/admin/extensions/{category}/{name}/metadata
```

Example: `GET /api/v1/admin/extensions/servers/proxmox/metadata`

Response:
```json
{
  "name": "Proxmox VE",
  "description": "Proxmox Virtual Environment server integration",
  "version": "1.0.0",
  "author": "Paymenter",
  "type": "server"
}
```

### Get Extension Configuration Schema
```
GET /api/v1/admin/extensions/{category}/{name}/config
```

Example: `GET /api/v1/admin/extensions/servers/proxmox/config`

Response:
```json
[
  {
    "name": "host",
    "type": "text",
    "label": "Proxmox Host",
    "description": "Proxmox server hostname or IP address",
    "required": true
  },
  {
    "name": "port",
    "type": "number",
    "label": "Port",
    "description": "Proxmox API port (default: 8006)",
    "default": 8006,
    "required": true
  }
]
```

## Creating Extensions

### Directory Structure

```
python_backend/app/extensions/
├── base.py                          # Base extension classes
├── loader.py                        # Extension loader
├── servers/
│   └── Proxmox/
│       └── proxmox.py              # Proxmox extension
├── gateways/
│   └── Stripe/
│       └── stripe.py               # Stripe extension
└── others/
    └── DiscordNotifications/
        └── discordnotifications.py  # Discord extension
```

### Creating a Server Extension

1. Create a directory in `app/extensions/servers/YourServer/`
2. Create `yourserver.py` with your extension class
3. Inherit from `ServerExtension`
4. Implement required methods

Example:

```python
from typing import Dict, Any, List
from app.extensions.base import ServerExtension

class YourServer(ServerExtension):
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'Your Server',
            'description': 'Your server integration',
            'version': '1.0.0',
            'author': 'Your Name',
            'type': 'server'
        }
    
    def get_config(self, values: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'api_key',
                'type': 'password',
                'label': 'API Key',
                'required': True
            }
        ]
    
    def create(self, service) -> Dict[str, Any]:
        # Implement service creation
        return {'success': True, 'message': 'Service created'}
    
    def suspend(self, service) -> Dict[str, Any]:
        # Implement service suspension
        return {'success': True}
    
    def unsuspend(self, service) -> Dict[str, Any]:
        # Implement service unsuspension
        return {'success': True}
    
    def terminate(self, service) -> Dict[str, Any]:
        # Implement service termination
        return {'success': True}
```

### Creating a Gateway Extension

1. Create a directory in `app/extensions/gateways/YourGateway/`
2. Create `yourgateway.py` with your extension class
3. Inherit from `GatewayExtension`
4. Implement required methods

Example:

```python
from typing import Dict, Any, List
from app.extensions.base import GatewayExtension

class YourGateway(GatewayExtension):
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'Your Gateway',
            'description': 'Your payment gateway',
            'version': '1.0.0',
            'author': 'Your Name',
            'type': 'gateway'
        }
    
    def get_config(self, values: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'api_key',
                'type': 'password',
                'label': 'API Key',
                'required': True
            }
        ]
    
    def pay(self, invoice) -> Dict[str, Any]:
        # Implement payment initiation
        return {
            'success': True,
            'redirect_url': 'https://payment.url',
            'status': 'pending'
        }
    
    def webhook(self, request: Any) -> Dict[str, Any]:
        # Handle webhook from gateway
        return {'success': True, 'status': 'processed'}
```

## Extension Configuration

Extensions are configured via their `get_config()` method which returns a list of configuration fields. Supported field types:

- `text` - Text input
- `password` - Password input (hidden)
- `number` - Numeric input
- `boolean` - Checkbox
- `select` - Dropdown selection
- `textarea` - Multi-line text

Example configuration field:

```python
{
    'name': 'api_key',           # Field name
    'type': 'password',          # Field type
    'label': 'API Key',          # Display label
    'description': 'Your API key from provider',  # Help text
    'required': True,            # Is required?
    'default': None              # Default value
}
```

## Using Extensions

### In Service Creation

```python
from app.extensions.loader import extension_manager

# Get the server extension
server = extension_manager.get_extension(
    'servers',
    product.server_type,
    config=product.server_config
)

# Create the service
if server:
    result = server.create(service)
    # Handle result
```

### In Payment Processing

```python
from app.extensions.loader import extension_manager

# Get the gateway extension
gateway = extension_manager.get_extension(
    'gateways',
    invoice.gateway_name,
    config=gateway_config
)

# Initiate payment
if gateway:
    result = gateway.pay(invoice)
    # Redirect to payment URL
```

## Testing Extensions

Each extension should include tests:

```python
# tests/test_extensions.py
def test_proxmox_extension():
    from app.extensions.servers.Proxmox.proxmox import Proxmox
    
    config = {
        'host': 'test.proxmox.com',
        'port': 8006,
        'username': 'test',
        'password': 'test'
    }
    
    proxmox = Proxmox(config)
    metadata = proxmox.get_metadata()
    
    assert metadata['name'] == 'Proxmox VE'
    assert 'server' in metadata['type']
```

## Extension Status

### Implemented (3 extensions)
- ✅ Proxmox (Server)
- ✅ Stripe (Gateway)
- ✅ Discord Notifications (Other)

### From PHP Backend - To Implement

**Servers (8 remaining):**
- Pterodactyl
- CPanel
- Plesk
- DirectAdmin
- Virtualizor
- Convoy
- Virtfusion
- Enhance

**Gateways (3 remaining):**
- PayPal
- PayPal IPN
- Mollie

**Others (2 remaining):**
- Affiliates
- Announcements

## Contributing Extensions

To contribute a new extension:

1. Create the extension following the structure above
2. Ensure it implements all required methods
3. Add tests for the extension
4. Update this README with the extension details
5. Submit a pull request

## Support

For extension-related questions:
- Check the [Python Backend README](../README.md)
- Review existing extension implementations
- Open an issue on GitHub
