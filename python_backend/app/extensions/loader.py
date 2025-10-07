"""
Extension loader and manager for Paymenter Python backend.
"""
import importlib
import os
from typing import Dict, Type, Optional, List
from app.extensions.base import BaseExtension, ServerExtension, GatewayExtension, OtherExtension


class ExtensionManager:
    """Manages loading and accessing extensions"""
    
    def __init__(self):
        self._extensions: Dict[str, Dict[str, Type[BaseExtension]]] = {
            'servers': {},
            'gateways': {},
            'others': {}
        }
        self._loaded = False
    
    def load_extensions(self):
        """Load all available extensions"""
        if self._loaded:
            return
        
        base_path = os.path.dirname(__file__)
        
        # Load server extensions
        self._load_category('servers', base_path)
        
        # Load gateway extensions
        self._load_category('gateways', base_path)
        
        # Load other extensions
        self._load_category('others', base_path)
        
        self._loaded = True
    
    def _load_category(self, category: str, base_path: str):
        """Load extensions from a specific category"""
        category_path = os.path.join(base_path, category)
        
        if not os.path.exists(category_path):
            return
        
        for item in os.listdir(category_path):
            item_path = os.path.join(category_path, item)
            
            # Skip __pycache__ and non-directories
            if item.startswith('__') or not os.path.isdir(item_path):
                continue
            
            # Try to load the extension
            try:
                module_name = f"app.extensions.{category}.{item}.{item.lower()}"
                module = importlib.import_module(module_name)
                
                # Find the extension class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseExtension) and 
                        attr not in [BaseExtension, ServerExtension, GatewayExtension, OtherExtension]):
                        self._extensions[category][item.lower()] = attr
                        break
            except (ImportError, AttributeError) as e:
                # Extension not found or invalid, skip it
                print(f"Warning: Could not load extension {category}/{item}: {e}")
                continue
    
    def get_extension(self, category: str, name: str, config: Dict = None) -> Optional[BaseExtension]:
        """
        Get an extension instance by category and name.
        
        Args:
            category: Extension category (servers, gateways, others)
            name: Extension name
            config: Extension configuration
            
        Returns:
            Extension instance or None if not found
        """
        if not self._loaded:
            self.load_extensions()
        
        extension_class = self._extensions.get(category, {}).get(name.lower())
        if extension_class:
            return extension_class(config or {})
        return None
    
    def list_extensions(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all available extensions.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary mapping categories to extension names
        """
        if not self._loaded:
            self.load_extensions()
        
        if category:
            return {category: list(self._extensions.get(category, {}).keys())}
        
        return {
            cat: list(exts.keys())
            for cat, exts in self._extensions.items()
        }


# Global extension manager instance
extension_manager = ExtensionManager()
