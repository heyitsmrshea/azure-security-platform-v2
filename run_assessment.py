#!/usr/bin/env python3
"""
Azure Security Platform - Point-in-Time Assessment Runner

This CLI tool runs security assessments for customer tenants and generates
comprehensive reports with compliance mapping.

Usage:
    python run_assessment.py --tenant-id <TENANT_ID> --customer-name "Acme Corp"
    
    # With comparison to previous assessment
    python run_assessment.py --tenant-id <TENANT_ID> --customer-name "Acme Corp" \
        --compare-with ./assessments/acme-2025-10-15
        
    # With custom branding
    python run_assessment.py --tenant-id <TENANT_ID> --customer-name "Acme Corp" \
        --brand partner_xyz
"""
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.assessment.engine import AssessmentEngine
from backend.assessment.comparison import ComparisonEngine
from backend.reports.branding import BrandingConfig, load_brand_config


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Azure Security Assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic assessment
  python run_assessment.py --tenant-id abc123 --customer-name "Acme Corp"
  
  # With all frameworks
  python run_assessment.py --tenant-id abc123 --customer-name "Acme Corp" \\
      --frameworks cis,nist,soc2,iso27001
  
  # Compare with previous
  python run_assessment.py --tenant-id abc123 --customer-name "Acme Corp" \\
      --compare-with ./assessments/acme-2025-10-15
  
  # White-labeled for partner
  python run_assessment.py --tenant-id abc123 --customer-name "Acme Corp" \\
      --brand partner_xyz

Environment Variables:
  AZURE_CLIENT_ID       Your multi-tenant app client ID
  AZURE_CLIENT_SECRET   Your app client secret
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--tenant-id",
        required=True,
        help="Customer's Azure AD tenant ID (from consent)"
    )
    parser.add_argument(
        "--customer-name",
        required=True,
        help="Customer organization name for reports"
    )
    
    # Optional arguments
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: ./assessments/<customer>-<date>)"
    )
    parser.add_argument(
        "--frameworks",
        default="cis,nist,soc2,iso27001",
        help="Comma-separated frameworks to assess (default: all)"
    )
    parser.add_argument(
        "--compare-with",
        default=None,
        help="Path to previous assessment for comparison report"
    )
    parser.add_argument(
        "--brand",
        default="operationmos",
        help="Brand configuration to use (default: operationmos)"
    )
    
    # Credential overrides
    parser.add_argument(
        "--client-id",
        default=os.getenv("AZURE_CLIENT_ID"),
        help="Azure AD app client ID (or set AZURE_CLIENT_ID env var)"
    )
    parser.add_argument(
        "--client-secret",
        default=os.getenv("AZURE_CLIENT_SECRET"),
        help="Azure AD app client secret (or set AZURE_CLIENT_SECRET env var)"
    )
    
    # Output options
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Skip PDF generation (JSON output only)"
    )
    parser.add_argument(
        "--keep-raw-data",
        action="store_true",
        help="Keep raw API response data (default: delete after processing)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without running assessment"
    )
    
    return parser.parse_args()


def validate_credentials(args) -> bool:
    """Validate that required credentials are available."""
    if not args.client_id:
        print("❌ Error: AZURE_CLIENT_ID not set")
        print("   Set via environment variable or --client-id flag")
        return False
    
    if not args.client_secret:
        print("❌ Error: AZURE_CLIENT_SECRET not set")
        print("   Set via environment variable or --client-secret flag")
        return False
    
    if not args.tenant_id:
        print("❌ Error: --tenant-id is required")
        return False
    
    return True


def get_output_dir(args) -> Path:
    """Determine output directory."""
    if args.output_dir:
        return Path(args.output_dir)
    
    # Generate default path
    customer_slug = args.customer_name.lower().replace(" ", "-").replace(".", "")
    date_str = datetime.now().strftime("%Y-%m-%d")
    return Path(f"./assessments/{customer_slug}-{date_str}")


def print_banner():
    """Print startup banner."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         Azure Security Platform - Assessment Engine            ║
║                    Point-in-Time Snapshot                      ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def print_summary(manifest: dict, output_dir: Path):
    """Print assessment summary."""
    scores = manifest.get("scores", {})
    findings = manifest.get("findings", {})
    
    print("\n" + "=" * 60)
    print("                    ASSESSMENT COMPLETE")
    print("=" * 60)
    
    # Grade
    grade = scores.get("overall_grade", "?")
    score = scores.get("overall_score", 0)
    grade_color = {
        "A": "\033[92m",  # Green
        "B": "\033[92m",  # Green
        "C": "\033[93m",  # Yellow
        "D": "\033[91m",  # Red
        "F": "\033[91m",  # Red
    }.get(grade, "")
    reset = "\033[0m"
    
    print(f"""
    Customer:     {manifest['customer']['name']}
    Date:         {manifest['assessment']['date'][:10]}
    Duration:     {manifest['assessment']['duration_seconds']}s
    
    ┌─────────────────────────────────────┐
    │         OVERALL GRADE: {grade_color}{grade}{reset}            │
    │         Score: {score}/100                │
    └─────────────────────────────────────┘
    
    Findings:
      • Critical: {findings.get('critical', 0)}
      • High:     {findings.get('high', 0)}
      • Medium:   {findings.get('medium', 0)}
      • Low:      {findings.get('low', 0)}
    
    Compliance Scores:
      • CIS Azure 2.0:  {scores.get('compliance', {}).get('cis_azure_v2', 'N/A')}%
      • NIST 800-53:    {scores.get('compliance', {}).get('nist_800_53', 'N/A')}%
      • SOC 2:          {scores.get('compliance', {}).get('soc2', 'N/A')}%
      • ISO 27001:      {scores.get('compliance', {}).get('iso27001', 'N/A')}%
    
    Output Directory: {output_dir}
    """)
    
    # List generated files
    print("    Generated Files:")
    for f in output_dir.rglob("*"):
        if f.is_file():
            rel_path = f.relative_to(output_dir)
            size = f.stat().st_size
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            print(f"      • {rel_path} ({size_str})")
    
    print("\n" + "=" * 60)


async def run_assessment(args):
    """Run the assessment."""
    print_banner()
    
    # Validate
    if not validate_credentials(args):
        sys.exit(1)
    
    # Setup output directory
    output_dir = get_output_dir(args)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse frameworks
    frameworks = [f.strip().lower() for f in args.frameworks.split(",")]
    
    # Load branding
    brand_config = load_brand_config(args.brand)
    
    print(f"📋 Assessment Configuration:")
    print(f"   Customer:    {args.customer_name}")
    print(f"   Tenant ID:   {args.tenant_id}")
    print(f"   Frameworks:  {', '.join(frameworks)}")
    print(f"   Brand:       {brand_config.company_name}")
    print(f"   Output:      {output_dir}")
    
    if args.compare_with:
        print(f"   Comparing:   {args.compare_with}")
    
    print()
    
    if args.dry_run:
        print("✅ Dry run complete - configuration is valid")
        return
    
    # Initialize engine
    print("🔧 Initializing assessment engine...")
    engine = AssessmentEngine(
        client_id=args.client_id,
        client_secret=args.client_secret,
        tenant_id=args.tenant_id,
        customer_name=args.customer_name,
        output_dir=output_dir,
        frameworks=frameworks,
        brand_config=brand_config,
        verbose=args.verbose,
    )
    
    # Run collection
    print("\n📡 Collecting data from Azure/Microsoft 365...")
    await engine.collect_all()
    
    # Analyze
    print("\n🔍 Analyzing findings and mapping to frameworks...")
    await engine.analyze()
    
    # Compare if requested
    if args.compare_with:
        print(f"\n📊 Comparing with previous assessment...")
        comparison_engine = ComparisonEngine(
            current_dir=output_dir,
            previous_dir=Path(args.compare_with),
        )
        await comparison_engine.generate_comparison()
    
    # Generate reports
    if not args.skip_pdf:
        print("\n📄 Generating PDF reports...")
        await engine.generate_reports()
    
    # Cleanup raw data
    if not args.keep_raw_data:
        print("\n🧹 Cleaning up raw data...")
        engine.cleanup_raw_data()
    
    # Save manifest
    manifest = engine.get_manifest()
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    
    # Print summary
    print_summary(manifest, output_dir)
    
    print("✅ Assessment complete!")
    return manifest


def main():
    """Main entry point."""
    args = parse_args()
    
    try:
        asyncio.run(run_assessment(args))
    except KeyboardInterrupt:
        print("\n\n⚠️  Assessment cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Assessment failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
