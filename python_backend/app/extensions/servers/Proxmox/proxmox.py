"""
Proxmox server extension for Paymenter Python backend.
"""
from typing import Dict, Any, List
import httpx
from app.extensions.base import ServerExtension


class Proxmox(ServerExtension):
    """Proxmox VE server integration"""
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get extension metadata"""
        return {
            'name': 'Proxmox VE',
            'description': 'Proxmox Virtual Environment server integration',
            'version': '1.0.0',
            'author': 'Paymenter',
            'type': 'server'
        }
    
    def get_config(self, values: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get configuration schema"""
        return [
            {
                'name': 'host',
                'type': 'text',
                'label': 'Proxmox Host',
                'description': 'Proxmox server hostname or IP address',
                'required': True
            },
            {
                'name': 'port',
                'type': 'number',
                'label': 'Port',
                'description': 'Proxmox API port (default: 8006)',
                'default': 8006,
                'required': True
            },
            {
                'name': 'username',
                'type': 'text',
                'label': 'API Token ID',
                'description': 'Proxmox API Token ID (e.g., user@pam!tokenid)',
                'required': True
            },
            {
                'name': 'password',
                'type': 'password',
                'label': 'API Token Secret',
                'description': 'Proxmox API Token Secret',
                'required': True
            },
            {
                'name': 'node',
                'type': 'text',
                'label': 'Node Name',
                'description': 'Proxmox node name to create VMs on',
                'required': True
            },
            {
                'name': 'storage',
                'type': 'text',
                'label': 'Storage',
                'description': 'Storage location for VM disks',
                'required': True
            },
            {
                'name': 'bridge',
                'type': 'text',
                'label': 'Network Bridge',
                'description': 'Network bridge name (e.g., vmbr0)',
                'default': 'vmbr0',
                'required': True
            }
        ]
    
    def request(self, url: str, method: str = 'GET', data: Dict = None) -> Dict:
        """
        Make a request to Proxmox API.
        
        Args:
            url: API endpoint URL
            method: HTTP method
            data: Request data
            
        Returns:
            API response dictionary
        """
        host = self.config('host')
        port = self.config('port', 8006)
        username = self.config('username')
        password = self.config('password')
        
        req_url = f"https://{host}:{port}/api2/json{url}"
        
        headers = {
            'Authorization': f'PVEAPIToken={username}={password}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        with httpx.Client(verify=False) as client:
            if method.upper() == 'GET':
                response = client.get(req_url, headers=headers, params=data or {})
            elif method.upper() == 'POST':
                response = client.post(req_url, headers=headers, json=data or {})
            elif method.upper() == 'PUT':
                response = client.put(req_url, headers=headers, json=data or {})
            elif method.upper() == 'DELETE':
                response = client.delete(req_url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if not response.is_success:
                error = response.json().get('errors', response.text)
                raise Exception(f"Proxmox API Error: {error}")
            
            return response.json() or {}
    
    def create(self, service) -> Dict[str, Any]:
        """
        Create a new VM in Proxmox.
        
        Args:
            service: Service model instance
            
        Returns:
            Creation result
        """
        node = self.config('node')
        storage = self.config('storage')
        bridge = self.config('bridge', 'vmbr0')
        
        # Get next available VMID
        vmid_response = self.request(f"/cluster/nextid")
        vmid = vmid_response.get('data')
        
        # VM configuration
        vm_config = {
            'vmid': vmid,
            'name': f"vm-{service.id}",
            'cores': service.service_config.get('cores', 1),
            'memory': service.service_config.get('memory', 1024),
            'storage': storage,
            'ostype': 'l26',  # Linux 2.6+
            'net0': f'virtio,bridge={bridge}',
        }
        
        # Create VM
        result = self.request(f"/nodes/{node}/qemu", method='POST', data=vm_config)
        
        return {
            'success': True,
            'vmid': vmid,
            'message': f'VM {vmid} created successfully',
            'data': result
        }
    
    def suspend(self, service) -> Dict[str, Any]:
        """
        Suspend a VM in Proxmox.
        
        Args:
            service: Service model instance
            
        Returns:
            Suspension result
        """
        node = self.config('node')
        vmid = service.service_config.get('vmid')
        
        if not vmid:
            raise Exception("VM ID not found in service configuration")
        
        # Stop the VM
        result = self.request(f"/nodes/{node}/qemu/{vmid}/status/stop", method='POST')
        
        return {
            'success': True,
            'message': f'VM {vmid} suspended successfully',
            'data': result
        }
    
    def unsuspend(self, service) -> Dict[str, Any]:
        """
        Unsuspend a VM in Proxmox.
        
        Args:
            service: Service model instance
            
        Returns:
            Unsuspension result
        """
        node = self.config('node')
        vmid = service.service_config.get('vmid')
        
        if not vmid:
            raise Exception("VM ID not found in service configuration")
        
        # Start the VM
        result = self.request(f"/nodes/{node}/qemu/{vmid}/status/start", method='POST')
        
        return {
            'success': True,
            'message': f'VM {vmid} unsuspended successfully',
            'data': result
        }
    
    def terminate(self, service) -> Dict[str, Any]:
        """
        Terminate a VM in Proxmox.
        
        Args:
            service: Service model instance
            
        Returns:
            Termination result
        """
        node = self.config('node')
        vmid = service.service_config.get('vmid')
        
        if not vmid:
            raise Exception("VM ID not found in service configuration")
        
        # Stop VM first
        try:
            self.request(f"/nodes/{node}/qemu/{vmid}/status/stop", method='POST')
        except:
            pass  # VM might already be stopped
        
        # Delete the VM
        result = self.request(f"/nodes/{node}/qemu/{vmid}", method='DELETE')
        
        return {
            'success': True,
            'message': f'VM {vmid} terminated successfully',
            'data': result
        }
    
    def get_login_url(self, service) -> str:
        """Get the Proxmox console URL"""
        host = self.config('host')
        port = self.config('port', 8006)
        node = self.config('node')
        vmid = service.service_config.get('vmid')
        
        if not vmid:
            return None
        
        return f"https://{host}:{port}/#v1:0:=qemu/{vmid}:4:5:::"
