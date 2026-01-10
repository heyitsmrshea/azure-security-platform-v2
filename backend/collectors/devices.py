"""
Device Collector for Azure Security Platform V2

Collects device compliance and management data from Microsoft Intune.
"""
from datetime import datetime
from typing import Optional
import structlog

from ..services.graph_client import GraphClient
from ..services.cache_service import CacheService
from ..models.schemas import DeviceCompliance, MetricTrend, TrendDirection

logger = structlog.get_logger(__name__)


class DeviceCollector:
    """
    Collects device compliance metrics from Intune.
    """
    
    def __init__(
        self,
        graph_client: GraphClient,
        cache_service: Optional[CacheService] = None,
    ):
        self._graph = graph_client
        self._cache = cache_service
        self._tenant_id = graph_client.tenant_id
        
        logger.info("device_collector_initialized", tenant_id=self._tenant_id)
    
    async def collect_device_compliance(self, force_refresh: bool = False) -> DeviceCompliance:
        """
        Collect device compliance metrics.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "device_compliance")
            if cached:
                return DeviceCompliance(**cached)
        
        # Fetch devices from Intune
        devices = await self._graph.get_managed_devices()
        
        # Calculate compliance metrics
        total_devices = len(devices)
        compliant = len([d for d in devices if d.get("compliance_state") == "compliant"])
        non_compliant = len([d for d in devices if d.get("compliance_state") == "noncompliant"])
        unknown = total_devices - compliant - non_compliant
        
        compliance_percent = (compliant / total_devices * 100) if total_devices > 0 else 0
        
        compliance = DeviceCompliance(
            compliant_count=compliant,
            non_compliant_count=non_compliant,
            unknown_count=unknown,
            total_devices=total_devices,
            compliance_percent=round(compliance_percent, 1),
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "device_compliance", compliance.model_dump())
        
        logger.info(
            "device_compliance_collected",
            tenant_id=self._tenant_id,
            total=total_devices,
            compliant=compliant,
            non_compliant=non_compliant,
        )
        
        return compliance
    
    async def get_non_compliant_devices(self) -> list[dict]:
        """
        Get list of non-compliant devices with details.
        """
        devices = await self._graph.get_managed_devices()
        
        non_compliant = []
        for device in devices:
            if device.get("compliance_state") == "noncompliant":
                non_compliant.append({
                    "device_name": device.get("device_name"),
                    "user": device.get("user_display_name"),
                    "email": device.get("user_principal_name"),
                    "os": device.get("operating_system"),
                    "os_version": device.get("os_version"),
                    "last_sync": device.get("last_sync"),
                    "is_encrypted": device.get("is_encrypted", False),
                })
        
        return non_compliant
    
    async def get_device_summary_by_os(self) -> dict:
        """
        Get device count summary by operating system.
        """
        devices = await self._graph.get_managed_devices()
        
        os_counts = {}
        for device in devices:
            os_name = device.get("operating_system", "Unknown")
            os_counts[os_name] = os_counts.get(os_name, 0) + 1
        
        return os_counts
    
    async def get_stale_devices(self, days: int = 30) -> list[dict]:
        """
        Get devices that haven't synced in specified number of days.
        """
        devices = await self._graph.get_managed_devices()
        
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        stale = []
        for device in devices:
            last_sync = device.get("last_sync")
            if last_sync:
                try:
                    sync_dt = datetime.fromisoformat(str(last_sync).replace("Z", "+00:00"))
                    if sync_dt.replace(tzinfo=None) < cutoff:
                        stale.append({
                            "device_name": device.get("device_name"),
                            "user": device.get("user_display_name"),
                            "last_sync": last_sync,
                            "days_since_sync": (datetime.utcnow() - sync_dt.replace(tzinfo=None)).days,
                        })
                except (ValueError, TypeError):
                    pass
        
        return stale
