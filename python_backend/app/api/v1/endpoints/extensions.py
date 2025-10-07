from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_admin_user
from app.models.models import User
from app.extensions.loader import extension_manager

router = APIRouter()


@router.get("/")
async def list_all_extensions(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, List[str]]:
    """List all available extensions"""
    return extension_manager.list_extensions()


@router.get("/{category}")
async def list_extensions_by_category(
    category: str,
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, List[str]]:
    """List extensions in a specific category"""
    if category not in ['servers', 'gateways', 'others']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category. Must be one of: servers, gateways, others"
        )
    return extension_manager.list_extensions(category)


@router.get("/{category}/{name}/metadata")
async def get_extension_metadata(
    category: str,
    name: str,
    current_user: User = Depends(get_current_admin_user)
) -> Dict:
    """Get metadata for a specific extension"""
    extension = extension_manager.get_extension(category, name)
    
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extension {category}/{name} not found"
        )
    
    return extension.get_metadata()


@router.get("/{category}/{name}/config")
async def get_extension_config(
    category: str,
    name: str,
    current_user: User = Depends(get_current_admin_user)
) -> List[Dict]:
    """Get configuration schema for a specific extension"""
    extension = extension_manager.get_extension(category, name)
    
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extension {category}/{name} not found"
        )
    
    return extension.get_config()
