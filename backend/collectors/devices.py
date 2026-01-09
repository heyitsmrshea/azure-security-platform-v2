"""
Device Collector for Azure Security Platform V2

Collects device compliance and management data from Intune.
"""
from datetime import datetime
from typing import Optional
import structlog

from ..services.graph_client import GraphClient
from ..services.cache_service import CacheService
from ..models.schemas import (
    DeviceCompliance,
    MetricTrend,
    TrendDirection,
)

logger = structlog.get_logger(__name__)


class DeviceCollector:
    """
    Collects device compliance metrics from Intune/Endpoint Manager.
    
    Features:
    - Device compliance status
    - Non-compliant device details
    - Agent health (EDR/AV status)
    - Unmanaged device detection
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
        
        # Fetch managed devices
        devices = await self._graph.get_managed_devices()
        
        # Count by compliance state
        compliant = 0
        non_compliant = 0
        unknown = 0
        
        for device in devices:
            state = device.get("compliance_state", "").lower()
            if state == "compliant":
                compliant += 1
            elif state == "noncompliant":
                non_compliant += 1
            else:
                unknown += 1
        
        total = len(devices)
        compliance_percent = (compliant / total * 100) if total > 0 else 0
        
        compliance = DeviceCompliance(
            compliant_count=compliant,
            non_compliant_count=non_compliant,
            unknown_count=unknown,
            total_devices=total,
            compliance_percent=round(compliance_percent, 1),
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "device_compliance", compliance.model_dump())
        
        logger.info(
            "device_compliance_collected",
            tenant_id=self._tenant_id,
            total=total,
            compliant=compliant,
            non_compliant=non_compliant,
        )
        
        return compliance
    
    async def get_non_compliant_devices(self) -> list[dict]:
        """
        Get detailed list of non-compliant devices with failure reasons.
        """
        devices = await self._graph.get_managed_devices()
        
        non_compliant = []
        for device in devices:
            if device.get("compliance_state", "").lower() == "noncompliant":
                non_compliant.append({
                    "device_id": device.get("id"),
                    "device_name": device.get("device_name"),
                    "os_type": device.get("operating_system"),
                    "os_version": device.get("os_version"),
                    "owner": device.get("user_principal_name"),
                    "compliance_state": device.get("compliance_state"),
                    "last_sync": device.get("last_sync"),
                    "is_encrypted": device.get("is_encrypted", False),
                    # In production, would fetch compliance policy details
                    "failure_reasons": self._determine_failure_reasons(device),
                })
        
        return non_compliant
    
    async def get_agent_health(self) -> list[dict]:
        """
        Get EDR/Antivirus agent health status.
        
        Note: Requires Defender for Endpoint integration.
        """
        devices = await self._graph.get_managed_devices()
        
        agent_health = []
        for device in devices:
            agent_health.append({
                "device_id": device.get("id"),
                "device_name": device.get("device_name"),
                "os_type": device.get("operating_system"),
                # In production, would query Defender API
                "defender_status": "active" if device.get("is_encrypted") else "unknown",
                "av_signature_date": None,
                "last_scan": None,
                "last_sync": device.get("last_sync"),
            })
        
        return agent_health
    
    async def get_unmanaged_devices(self) -> list[dict]:
        """
        Get devices accessing corporate data that aren't managed.
        
        Note: Requires Azure AD sign-in logs analysis.
        """
        # In production, this would:
        # 1. Query sign-in logs for unique devices
        # 2. Compare against managed device list
        # 3. Return devices not in Intune
        
        # For now, return empty (would need sign-in log access)
        return []
    
    async def get_device_summary(self) -> dict:
        """
        Get comprehensive device summary for IT dashboard.
        """
        devices = await self._graph.get_managed_devices()
        
        # Group by OS
        os_breakdown = {}
        encryption_status = {"encrypted": 0, "not_encrypted": 0}
        stale_devices = []  # Devices not synced in 30+ days
        
        thirty_days_ago = datetime.utcnow().timestamp() - (30 * 24 * 60 * 60)
        
        for device in devices:
            # OS breakdown
            os_type = device.get("operating_system", "Unknown")
            os_breakdown[os_type] = os_breakdown.get(os_type, 0) + 1
            
            # Encryption
            if device.get("is_encrypted"):
                encryption_status["encrypted"] += 1
            else:
                encryption_status["not_encrypted"] += 1
            
            # Stale check
            last_sync = device.get("last_sync")
            if last_sync:
                try:
                    sync_time = datetime.fromisoformat(str(last_sync).replace("Z", "")).timestamp()
                    if sync_time < thirty_days_ago:
                        stale_devices.append({
                            "device_name": device.get("device_name"),
                            "last_sync": last_sync,
                            "owner": device.get("user_principal_name"),
                        })
                except:
                    pass
        
        return {
            "total_devices": len(devices),
            "os_breakdown": os_breakdown,
            "encryption_status": encryption_status,
            "stale_devices": stale_devices,
            "stale_count": len(stale_devices),
        }
    
    def _determine_failure_reasons(self, device: dict) -> list[str]:
        """
        Determine compliance failure reasons based on device properties.
        
        In production, would query compliance policy evaluation results.
        """
        reasons = []
        
        if not device.get("is_encrypted"):
            reasons.append("Device not encrypted")
        
        # Check OS version (simplified)
        os_version = device.get("os_version", "")
        if "10.0.19041" in os_version or "10.0.18" in os_version:
            reasons.append("OS version outdated")
        
        # Check last sync
        last_sync = device.get("last_sync")
        if last_sync:
            try:
                sync_time = datetime.fromisoformat(str(last_sync).replace("Z", ""))
                days_since_sync = (datetime.utcnow() - sync_time).days
                if days_since_sync > 14:
                    reasons.append(f"Not synced in {days_since_sync} days")
            except:
                pass
        
        if not reasons:
            reasons.append("Policy violation detected")
        
        return reasons
