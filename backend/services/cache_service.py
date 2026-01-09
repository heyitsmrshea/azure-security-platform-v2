"""
Redis Cache Service for Azure Security Platform V2

Provides caching for API responses and collected data.
"""
import json
from datetime import timedelta
from typing import Any, Optional
import structlog

import redis.asyncio as redis

logger = structlog.get_logger(__name__)


class CacheService:
    """
    Redis-based caching service for security data.
    
    Features:
    - Tenant-isolated caching with key prefixes
    - Configurable TTL per data type
    - JSON serialization for complex objects
    - Connection pooling
    """
    
    # Default TTLs by data type (in seconds)
    DEFAULT_TTLS = {
        "secure_score": 14400,      # 4 hours
        "mfa_status": 14400,        # 4 hours
        "risky_users": 3600,        # 1 hour
        "alerts": 900,              # 15 minutes
        "conditional_access": 3600,  # 1 hour
        "pim": 3600,                # 1 hour
        "audit_logs": 1800,         # 30 minutes
        "devices": 14400,           # 4 hours
        "backup": 14400,            # 4 hours
        "executive_dashboard": 900,  # 15 minutes
        "it_dashboard": 900,        # 15 minutes
    }
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        key_prefix: str = "asp2",
    ):
        """
        Initialize cache service.
        
        Args:
            redis_url: Redis connection URL
            key_prefix: Prefix for all cache keys
        """
        self._redis_url = redis_url
        self._key_prefix = key_prefix
        self._client: Optional[redis.Redis] = None
        
        logger.info("cache_service_initialized", redis_url=redis_url)
    
    async def connect(self) -> None:
        """Establish Redis connection."""
        if not self._client:
            self._client = redis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("redis_connected")
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("redis_disconnected")
    
    async def _ensure_connected(self) -> None:
        """Ensure Redis connection is established."""
        if not self._client:
            await self.connect()
    
    def _make_key(self, tenant_id: str, data_type: str, suffix: str = "") -> str:
        """
        Generate a cache key.
        
        Format: {prefix}:{tenant_id}:{data_type}:{suffix}
        """
        key = f"{self._key_prefix}:{tenant_id}:{data_type}"
        if suffix:
            key += f":{suffix}"
        return key
    
    # ========================================================================
    # Core Cache Operations
    # ========================================================================
    
    async def get(
        self,
        tenant_id: str,
        data_type: str,
        suffix: str = "",
    ) -> Optional[Any]:
        """
        Get cached data.
        
        Returns:
            Cached data or None if not found/expired
        """
        await self._ensure_connected()
        
        key = self._make_key(tenant_id, data_type, suffix)
        
        try:
            data = await self._client.get(key)
            if data:
                logger.debug("cache_hit", key=key)
                return json.loads(data)
            logger.debug("cache_miss", key=key)
            return None
        except Exception as e:
            logger.warning("cache_get_error", key=key, error=str(e))
            return None
    
    async def set(
        self,
        tenant_id: str,
        data_type: str,
        data: Any,
        suffix: str = "",
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Set cached data.
        
        Args:
            tenant_id: Tenant identifier
            data_type: Type of data being cached
            data: Data to cache (must be JSON serializable)
            suffix: Optional key suffix
            ttl_seconds: TTL override (uses default if not specified)
            
        Returns:
            True if successful
        """
        await self._ensure_connected()
        
        key = self._make_key(tenant_id, data_type, suffix)
        ttl = ttl_seconds or self.DEFAULT_TTLS.get(data_type, 3600)
        
        try:
            await self._client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(data, default=str),
            )
            logger.debug("cache_set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.warning("cache_set_error", key=key, error=str(e))
            return False
    
    async def delete(
        self,
        tenant_id: str,
        data_type: str,
        suffix: str = "",
    ) -> bool:
        """
        Delete cached data.
        """
        await self._ensure_connected()
        
        key = self._make_key(tenant_id, data_type, suffix)
        
        try:
            await self._client.delete(key)
            logger.debug("cache_deleted", key=key)
            return True
        except Exception as e:
            logger.warning("cache_delete_error", key=key, error=str(e))
            return False
    
    async def invalidate_tenant(self, tenant_id: str) -> int:
        """
        Invalidate all cached data for a tenant.
        
        Returns:
            Number of keys deleted
        """
        await self._ensure_connected()
        
        pattern = self._make_key(tenant_id, "*")
        
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self._client.delete(*keys)
                logger.info("tenant_cache_invalidated", tenant_id=tenant_id, keys_deleted=len(keys))
            
            return len(keys)
        except Exception as e:
            logger.warning("cache_invalidate_error", tenant_id=tenant_id, error=str(e))
            return 0
    
    # ========================================================================
    # Convenience Methods
    # ========================================================================
    
    async def get_or_set(
        self,
        tenant_id: str,
        data_type: str,
        fetch_func,
        suffix: str = "",
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """
        Get from cache or fetch and cache.
        
        Args:
            tenant_id: Tenant identifier
            data_type: Type of data
            fetch_func: Async function to fetch data if not cached
            suffix: Optional key suffix
            ttl_seconds: TTL override
            
        Returns:
            Cached or freshly fetched data
        """
        # Try cache first
        cached = await self.get(tenant_id, data_type, suffix)
        if cached is not None:
            return cached
        
        # Fetch fresh data
        data = await fetch_func()
        
        # Cache it
        await self.set(tenant_id, data_type, data, suffix, ttl_seconds)
        
        return data
    
    async def get_executive_dashboard(self, tenant_id: str) -> Optional[dict]:
        """Get cached executive dashboard data."""
        return await self.get(tenant_id, "executive_dashboard")
    
    async def set_executive_dashboard(self, tenant_id: str, data: dict) -> bool:
        """Cache executive dashboard data."""
        return await self.set(tenant_id, "executive_dashboard", data)
    
    async def get_it_dashboard(self, tenant_id: str) -> Optional[dict]:
        """Get cached IT dashboard data."""
        return await self.get(tenant_id, "it_dashboard")
    
    async def set_it_dashboard(self, tenant_id: str, data: dict) -> bool:
        """Cache IT dashboard data."""
        return await self.set(tenant_id, "it_dashboard", data)
    
    # ========================================================================
    # Health Check
    # ========================================================================
    
    async def health_check(self) -> dict:
        """
        Check Redis connection health.
        
        Returns:
            Health status dict
        """
        await self._ensure_connected()
        
        try:
            await self._client.ping()
            info = await self._client.info("memory")
            
            return {
                "status": "healthy",
                "connected": True,
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", "unknown"),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
            }
