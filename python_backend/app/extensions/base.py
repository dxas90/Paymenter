"""
Base extension classes for Paymenter Python backend.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class ExtensionConfig(BaseModel):
    """Base configuration for extensions"""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None


class BaseExtension(ABC):
    """Base class for all extensions"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the extension with configuration.
        
        Args:
            config: Dictionary containing extension configuration
        """
        self._config = config or {}
    
    def config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    @abstractmethod
    def get_config(self, values: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get the configuration schema for the extension.
        
        Args:
            values: Current configuration values
            
        Returns:
            List of configuration field definitions
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the extension.
        
        Returns:
            Dictionary containing extension metadata (name, description, version, etc.)
        """
        pass


class ServerExtension(BaseExtension):
    """Base class for server extensions (provisioning integrations)"""
    
    @abstractmethod
    def create(self, service) -> Dict[str, Any]:
        """
        Create a new service instance.
        
        Args:
            service: Service model instance
            
        Returns:
            Dictionary with creation result
        """
        pass
    
    @abstractmethod
    def suspend(self, service) -> Dict[str, Any]:
        """
        Suspend a service instance.
        
        Args:
            service: Service model instance
            
        Returns:
            Dictionary with suspension result
        """
        pass
    
    @abstractmethod
    def unsuspend(self, service) -> Dict[str, Any]:
        """
        Unsuspend a service instance.
        
        Args:
            service: Service model instance
            
        Returns:
            Dictionary with unsuspension result
        """
        pass
    
    @abstractmethod
    def terminate(self, service) -> Dict[str, Any]:
        """
        Terminate a service instance.
        
        Args:
            service: Service model instance
            
        Returns:
            Dictionary with termination result
        """
        pass
    
    def get_login_url(self, service) -> Optional[str]:
        """
        Get the login URL for the service (optional).
        
        Args:
            service: Service model instance
            
        Returns:
            Login URL or None
        """
        return None


class GatewayExtension(BaseExtension):
    """Base class for payment gateway extensions"""
    
    @abstractmethod
    def pay(self, invoice) -> Dict[str, Any]:
        """
        Initiate payment for an invoice.
        
        Args:
            invoice: Invoice model instance
            
        Returns:
            Dictionary with payment initiation result (redirect_url, status, etc.)
        """
        pass
    
    @abstractmethod
    def webhook(self, request: Any) -> Dict[str, Any]:
        """
        Handle webhook from payment gateway.
        
        Args:
            request: HTTP request object
            
        Returns:
            Dictionary with webhook processing result
        """
        pass
    
    def refund(self, transaction) -> Dict[str, Any]:
        """
        Refund a transaction (optional).
        
        Args:
            transaction: Transaction model instance
            
        Returns:
            Dictionary with refund result
        """
        raise NotImplementedError("Refund not supported by this gateway")


class OtherExtension(BaseExtension):
    """Base class for other extensions (notifications, integrations, etc.)"""
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the extension functionality.
        
        Args:
            **kwargs: Extension-specific arguments
            
        Returns:
            Dictionary with execution result
        """
        pass
