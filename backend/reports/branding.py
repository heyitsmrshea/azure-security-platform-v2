"""
White-Label Branding Support

Provides branding configuration for customizing reports with
partner logos, colors, and contact information.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

# Brands directory
BRANDS_DIR = Path(__file__).parent.parent.parent / "brands"


@dataclass
class BrandColors:
    """Color palette for a brand."""
    primary: str = "#0F172A"      # Main background/header color
    secondary: str = "#1E293B"    # Secondary background
    accent: str = "#3B82F6"       # Accent/highlight color
    text_primary: str = "#F8FAFC" # Primary text
    text_secondary: str = "#94A3B8"  # Secondary text
    success: str = "#22C55E"      # Success/pass color
    warning: str = "#EAB308"      # Warning color
    danger: str = "#EF4444"       # Error/critical color


@dataclass
class BrandContact:
    """Contact information for a brand."""
    email: str = ""
    phone: str = ""
    website: str = ""
    address: str = ""


@dataclass
class BrandingConfig:
    """
    Complete branding configuration for reports.
    
    Attributes:
        brand_id: Unique identifier for the brand
        company_name: Company name to display in reports
        logo_path: Path to logo file (SVG or PNG)
        colors: Color palette
        contact: Contact information
        tagline: Optional tagline/slogan
        footer_text: Custom footer text for reports
        disclaimers: Legal disclaimers to include
        custom_sections: Any custom content sections
    """
    brand_id: str = "default"
    company_name: str = "Security Assessment"
    logo_path: Optional[str] = None
    colors: BrandColors = field(default_factory=BrandColors)
    contact: BrandContact = field(default_factory=BrandContact)
    tagline: str = ""
    footer_text: str = ""
    disclaimers: list[str] = field(default_factory=list)
    custom_sections: dict = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict) -> "BrandingConfig":
        """Create BrandingConfig from dictionary."""
        colors_data = data.get("colors", {})
        colors = BrandColors(
            primary=colors_data.get("primary", BrandColors.primary),
            secondary=colors_data.get("secondary", BrandColors.secondary),
            accent=colors_data.get("accent", BrandColors.accent),
            text_primary=colors_data.get("text_primary", BrandColors.text_primary),
            text_secondary=colors_data.get("text_secondary", BrandColors.text_secondary),
            success=colors_data.get("success", BrandColors.success),
            warning=colors_data.get("warning", BrandColors.warning),
            danger=colors_data.get("danger", BrandColors.danger),
        )
        
        contact_data = data.get("contact", {})
        contact = BrandContact(
            email=contact_data.get("email", ""),
            phone=contact_data.get("phone", ""),
            website=contact_data.get("website", ""),
            address=contact_data.get("address", ""),
        )
        
        return cls(
            brand_id=data.get("brand_id", "default"),
            company_name=data.get("company_name", "Security Assessment"),
            logo_path=data.get("logo_path"),
            colors=colors,
            contact=contact,
            tagline=data.get("tagline", ""),
            footer_text=data.get("footer_text", ""),
            disclaimers=data.get("disclaimers", []),
            custom_sections=data.get("custom_sections", {}),
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "brand_id": self.brand_id,
            "company_name": self.company_name,
            "logo_path": self.logo_path,
            "colors": {
                "primary": self.colors.primary,
                "secondary": self.colors.secondary,
                "accent": self.colors.accent,
                "text_primary": self.colors.text_primary,
                "text_secondary": self.colors.text_secondary,
                "success": self.colors.success,
                "warning": self.colors.warning,
                "danger": self.colors.danger,
            },
            "contact": {
                "email": self.contact.email,
                "phone": self.contact.phone,
                "website": self.contact.website,
                "address": self.contact.address,
            },
            "tagline": self.tagline,
            "footer_text": self.footer_text,
            "disclaimers": self.disclaimers,
            "custom_sections": self.custom_sections,
        }


def load_brand_config(brand_id: str) -> BrandingConfig:
    """
    Load branding configuration by ID.
    
    Looks for config in:
    1. brands/<brand_id>/config.json
    2. Falls back to default brand
    
    Args:
        brand_id: Brand identifier (e.g., "operationmos", "partner_xyz")
        
    Returns:
        BrandingConfig instance
    """
    # Try to load specific brand
    brand_dir = BRANDS_DIR / brand_id
    config_path = brand_dir / "config.json"
    
    if config_path.exists():
        try:
            with open(config_path) as f:
                data = json.load(f)
            
            # Resolve logo path
            if data.get("logo_path") and not Path(data["logo_path"]).is_absolute():
                data["logo_path"] = str(brand_dir / data["logo_path"])
            
            logger.info("brand_loaded", brand_id=brand_id)
            return BrandingConfig.from_dict(data)
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("brand_load_error", brand_id=brand_id, error=str(e))
    
    # Fall back to default
    logger.warning("brand_not_found", brand_id=brand_id, fallback="default")
    return get_default_brand()


def get_default_brand() -> BrandingConfig:
    """Get default branding configuration."""
    return BrandingConfig(
        brand_id="default",
        company_name="Security Assessment",
        tagline="Protecting Your Digital Assets",
        footer_text="© 2026 Security Assessment. All rights reserved.",
        disclaimers=[
            "This assessment represents a point-in-time snapshot of your security posture.",
            "Recommendations should be validated and tested before implementation.",
            "This report is confidential and intended only for the recipient organization.",
        ],
    )


def list_available_brands() -> list[dict]:
    """
    List all available brand configurations.
    
    Returns:
        List of brand summaries
    """
    brands = []
    
    if BRANDS_DIR.exists():
        for brand_dir in BRANDS_DIR.iterdir():
            if brand_dir.is_dir():
                config_path = brand_dir / "config.json"
                if config_path.exists():
                    try:
                        with open(config_path) as f:
                            data = json.load(f)
                        brands.append({
                            "brand_id": brand_dir.name,
                            "company_name": data.get("company_name", brand_dir.name),
                            "has_logo": (brand_dir / data.get("logo_path", "logo.svg")).exists() if data.get("logo_path") else False,
                        })
                    except json.JSONDecodeError:
                        pass
    
    return brands


def create_brand_config(
    brand_id: str,
    company_name: str,
    **kwargs,
) -> BrandingConfig:
    """
    Create and save a new brand configuration.
    
    Args:
        brand_id: Unique identifier for the brand
        company_name: Company name
        **kwargs: Additional BrandingConfig fields
        
    Returns:
        Created BrandingConfig
    """
    brand_dir = BRANDS_DIR / brand_id
    brand_dir.mkdir(parents=True, exist_ok=True)
    
    config = BrandingConfig(
        brand_id=brand_id,
        company_name=company_name,
        **kwargs,
    )
    
    config_path = brand_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config.to_dict(), f, indent=2)
    
    logger.info("brand_created", brand_id=brand_id)
    return config
