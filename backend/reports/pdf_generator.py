"""
PDF Report Generator for Azure Security Platform V2

Generates executive and compliance PDF reports using ReportLab.
Supports white-label branding for partner reports.
"""
import io
from datetime import datetime
from pathlib import Path
from typing import Optional
import structlog

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable, ListFlowable, ListItem
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.widgets.markers import makeMarker

from models.schemas import ExecutiveDashboard
from reports.branding import BrandingConfig, get_default_brand

logger = structlog.get_logger(__name__)

# Color palette matching the UI design system
COLORS = {
    'primary': colors.HexColor('#0F172A'),
    'secondary': colors.HexColor('#1E293B'),
    'accent': colors.HexColor('#3B82F6'),
    'text_primary': colors.HexColor('#F8FAFC'),
    'text_secondary': colors.HexColor('#94A3B8'),
    'text_muted': colors.HexColor('#64748B'),
    'critical': colors.HexColor('#EF4444'),
    'high': colors.HexColor('#F97316'),
    'medium': colors.HexColor('#EAB308'),
    'low': colors.HexColor('#3B82F6'),
    'success': colors.HexColor('#22C55E'),
    'white': colors.white,
    'black': colors.black,
}


class PDFReportGenerator:
    """
    Generates PDF reports for security dashboards.
    
    Report Types:
    - Executive Summary: High-level metrics for board/executives
    - Technical Findings: Detailed findings for IT staff
    - Compliance Report: Framework compliance details
    - Comparison Report: Before/after assessment comparison
    
    Supports white-label branding for partner reports.
    """
    
    def __init__(self, brand_config: Optional[BrandingConfig] = None):
        self.brand = brand_config or get_default_brand()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self._setup_brand_colors()
        
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=COLORS['primary'],
            spaceAfter=20,
            alignment=TA_CENTER,
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=COLORS['primary'],
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=(0, 0, 5, 0),
        ))
        
        # Metric label
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=COLORS['text_muted'],
        ))
        
        # Metric value
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=24,
            textColor=COLORS['primary'],
            fontName='Helvetica-Bold',
        ))
        
        # Body text - modify existing style
        if 'BodyText' in self.styles:
            self.styles['BodyText'].fontSize = 10
            self.styles['BodyText'].textColor = COLORS['primary']
            self.styles['BodyText'].leading = 14
        else:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=COLORS['primary'],
                leading=14,
            ))
        
        # Risk item
        self.styles.add(ParagraphStyle(
            name='RiskItem',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=COLORS['primary'],
            leftIndent=20,
            spaceBefore=5,
        ))
    
    def _setup_brand_colors(self):
        """Apply brand colors to the color palette."""
        if self.brand:
            COLORS['primary'] = colors.HexColor(self.brand.colors.primary)
            COLORS['secondary'] = colors.HexColor(self.brand.colors.secondary)
            COLORS['accent'] = colors.HexColor(self.brand.colors.accent)
    
    # ========================================================================
    # Assessment Report Methods (for snapshot assessments)
    # ========================================================================
    
    def generate_executive_summary(
        self,
        customer_name: str,
        assessment_date: datetime,
        scores: dict,
        findings: list[dict],
        compliance_results: dict,
    ) -> bytes:
        """
        Generate branded executive summary PDF.
        
        Args:
            customer_name: Customer organization name
            assessment_date: Date of assessment
            scores: Score dictionary with overall_grade, overall_score, etc.
            findings: List of security findings
            compliance_results: Compliance framework results
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        story = []
        
        # Cover page with branding
        story.extend(self._create_cover_page(
            title="Security Assessment",
            subtitle="Executive Summary",
            customer_name=customer_name,
            assessment_date=assessment_date,
        ))
        
        story.append(PageBreak())
        
        # Overall Grade Section
        story.append(Paragraph("Security Posture Overview", self.styles['SectionHeader']))
        story.append(self._create_grade_display(scores))
        story.append(Spacer(1, 20))
        
        # Key Metrics Table
        story.append(Paragraph("Key Metrics", self.styles['SectionHeader']))
        story.append(self._create_scores_table(scores))
        story.append(Spacer(1, 20))
        
        # Finding Summary
        story.append(Paragraph("Finding Summary", self.styles['SectionHeader']))
        story.append(self._create_finding_summary_table(findings))
        story.append(Spacer(1, 20))
        
        # Compliance Overview
        story.append(Paragraph("Compliance Overview", self.styles['SectionHeader']))
        story.append(self._create_compliance_summary_table(compliance_results))
        story.append(Spacer(1, 20))
        
        # Top Risks
        story.append(PageBreak())
        story.append(Paragraph("Top Risks", self.styles['SectionHeader']))
        critical_high = [f for f in findings if f.get('severity') in ['critical', 'high']][:5]
        for i, finding in enumerate(critical_high, 1):
            story.extend(self._format_risk_item(i, finding))
        
        # Footer with disclaimers
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=COLORS['secondary']))
        story.append(Spacer(1, 10))
        for disclaimer in self.brand.disclaimers[:2]:
            story.append(Paragraph(
                f"<i>{disclaimer}</i>",
                self.styles['MetricLabel']
            ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_technical_report(
        self,
        customer_name: str,
        assessment_date: datetime,
        findings: list[dict],
        raw_data: dict,
    ) -> bytes:
        """
        Generate technical findings report for IT staff.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        story = []
        
        # Cover page
        story.extend(self._create_cover_page(
            title="Security Assessment",
            subtitle="Technical Findings Report",
            customer_name=customer_name,
            assessment_date=assessment_date,
        ))
        
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph("Table of Contents", self.styles['SectionHeader']))
        story.append(Paragraph("1. Finding Summary", self.styles['BodyText']))
        story.append(Paragraph("2. Critical Findings", self.styles['BodyText']))
        story.append(Paragraph("3. High Findings", self.styles['BodyText']))
        story.append(Paragraph("4. Medium Findings", self.styles['BodyText']))
        story.append(Paragraph("5. Low Findings", self.styles['BodyText']))
        story.append(Spacer(1, 20))
        
        # Finding Summary
        story.append(PageBreak())
        story.append(Paragraph("1. Finding Summary", self.styles['SectionHeader']))
        story.append(self._create_finding_summary_table(findings))
        story.append(Spacer(1, 20))
        
        # Findings by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            severity_findings = [f for f in findings if f.get('severity') == severity]
            if severity_findings:
                story.append(PageBreak())
                story.append(Paragraph(
                    f"{severity.title()} Findings ({len(severity_findings)})",
                    self.styles['SectionHeader']
                ))
                
                for i, finding in enumerate(severity_findings, 1):
                    story.extend(self._format_detailed_finding(finding))
                    if i < len(severity_findings):
                        story.append(Spacer(1, 15))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=COLORS['secondary']))
        story.append(Paragraph(
            f"Generated by {self.brand.company_name} | {datetime.utcnow().strftime('%Y-%m-%d')}",
            self.styles['MetricLabel']
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_compliance_report(
        self,
        customer_name: str,
        assessment_date: datetime,
        compliance_results: dict,
        findings: list[dict],
    ) -> bytes:
        """
        Generate compliance framework report.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        story = []
        
        # Cover page
        story.extend(self._create_cover_page(
            title="Security Assessment",
            subtitle="Compliance Report",
            customer_name=customer_name,
            assessment_date=assessment_date,
        ))
        
        story.append(PageBreak())
        
        # Compliance Summary
        story.append(Paragraph("Compliance Summary", self.styles['SectionHeader']))
        story.append(self._create_compliance_summary_table(compliance_results))
        story.append(Spacer(1, 30))
        
        # Framework Details
        for framework_id, result in compliance_results.items():
            story.append(PageBreak())
            fw_info = result.get('framework', {})
            story.append(Paragraph(
                f"{fw_info.get('name', framework_id)}",
                self.styles['SectionHeader']
            ))
            
            # Framework score
            story.append(Paragraph(
                f"<b>Score: {result.get('score', 0):.1f}%</b> | "
                f"Passed: {result.get('controls', {}).get('passed', 0)} | "
                f"Failed: {result.get('controls', {}).get('failed', 0)} | "
                f"Total: {result.get('controls', {}).get('total', 0)}",
                self.styles['BodyText']
            ))
            story.append(Spacer(1, 15))
            
            # Failed controls
            failed = result.get('failed_controls', [])
            if failed:
                story.append(Paragraph("Failed Controls:", self.styles['BodyText']))
                for ctrl in failed[:10]:  # Limit to 10
                    story.append(Paragraph(f"• {ctrl}", self.styles['RiskItem']))
            else:
                story.append(Paragraph(
                    "All assessed controls passed.",
                    self.styles['BodyText']
                ))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=COLORS['secondary']))
        story.append(Paragraph(
            f"Generated by {self.brand.company_name} | {datetime.utcnow().strftime('%Y-%m-%d')}",
            self.styles['MetricLabel']
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_cover_page(
        self,
        title: str,
        subtitle: str,
        customer_name: str,
        assessment_date: datetime,
    ) -> list:
        """Create branded cover page elements."""
        elements = []
        
        # Logo (if available)
        if self.brand.logo_path and Path(self.brand.logo_path).exists():
            try:
                logo = Image(self.brand.logo_path, width=2*inch, height=0.75*inch)
                elements.append(logo)
                elements.append(Spacer(1, 30))
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")
        
        elements.append(Spacer(1, 100))
        
        # Title
        elements.append(Paragraph(title, self.styles['ReportTitle']))
        elements.append(Paragraph(subtitle, self.styles['Heading2']))
        elements.append(Spacer(1, 40))
        
        # Customer name
        elements.append(Paragraph(
            f"<b>Prepared for:</b> {customer_name}",
            self.styles['BodyText']
        ))
        elements.append(Paragraph(
            f"<b>Assessment Date:</b> {assessment_date.strftime('%B %d, %Y') if assessment_date else 'N/A'}",
            self.styles['BodyText']
        ))
        elements.append(Paragraph(
            f"<b>Prepared by:</b> {self.brand.company_name}",
            self.styles['BodyText']
        ))
        
        elements.append(Spacer(1, 100))
        
        # Tagline
        if self.brand.tagline:
            elements.append(Paragraph(
                f"<i>{self.brand.tagline}</i>",
                self.styles['MetricLabel']
            ))
        
        # Contact info
        if self.brand.contact.website:
            elements.append(Paragraph(
                self.brand.contact.website,
                self.styles['MetricLabel']
            ))
        
        return elements
    
    def _create_grade_display(self, scores: dict) -> Table:
        """Create visual grade display."""
        grade = scores.get('overall_grade', '?')
        score = scores.get('overall_score', 0)
        
        # Grade description
        descriptions = {
            'A': 'Excellent - Industry leading security',
            'B': 'Good - Above average posture',
            'C': 'Fair - Meets minimum standards',
            'D': 'Poor - Significant gaps',
            'F': 'Critical - Immediate action required',
        }
        
        data = [
            [f"Grade: {grade}", f"Score: {score}/100"],
            [descriptions.get(grade, ''), ''],
        ]
        
        table = Table(data, colWidths=[3.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, 0), 36),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 1), (1, 1)),
        ]))
        
        return table
    
    def _create_scores_table(self, scores: dict) -> Table:
        """Create scores summary table."""
        categories = scores.get('categories', {})
        compliance = scores.get('compliance', {})
        
        data = [['Category', 'Score']]
        
        data.append(['Secure Score', f"{scores.get('secure_score', 0):.1f}%"])
        
        for cat, score in categories.items():
            data.append([cat.replace('_', ' ').title(), f"{score:.1f}%"])
        
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['secondary']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['white'], colors.HexColor('#F8FAFC')]),
        ]))
        
        return table
    
    def _create_finding_summary_table(self, findings: list[dict]) -> Table:
        """Create finding count summary table."""
        counts = {
            'Critical': len([f for f in findings if f.get('severity') == 'critical']),
            'High': len([f for f in findings if f.get('severity') == 'high']),
            'Medium': len([f for f in findings if f.get('severity') == 'medium']),
            'Low': len([f for f in findings if f.get('severity') == 'low']),
        }
        
        data = [['Severity', 'Count']]
        for sev, count in counts.items():
            data.append([sev, str(count)])
        data.append(['Total', str(sum(counts.values()))])
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['secondary']),
        ]))
        
        return table
    
    def _create_compliance_summary_table(self, compliance_results: dict) -> Table:
        """Create compliance frameworks summary table."""
        data = [['Framework', 'Score', 'Passed', 'Failed']]
        
        for fw_id, result in compliance_results.items():
            fw_name = result.get('framework', {}).get('name', fw_id)
            controls = result.get('controls', {})
            data.append([
                fw_name[:30],  # Truncate long names
                f"{result.get('score', 0):.1f}%",
                str(controls.get('passed', 0)),
                str(controls.get('failed', 0)),
            ])
        
        table = Table(data, colWidths=[3*inch, 1.5*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['secondary']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['white'], colors.HexColor('#F8FAFC')]),
        ]))
        
        return table
    
    def _format_risk_item(self, number: int, finding: dict) -> list:
        """Format a risk item for the executive summary."""
        elements = []
        severity = finding.get('severity', 'medium').upper()
        color = self._get_severity_color(severity.lower())
        
        elements.append(Paragraph(
            f"<font color='{color}'><b>{number}. [{severity}]</b></font> {finding.get('title', 'Unknown')}",
            self.styles['BodyText']
        ))
        elements.append(Paragraph(
            finding.get('description', ''),
            self.styles['RiskItem']
        ))
        if finding.get('recommendation'):
            elements.append(Paragraph(
                f"<b>Recommendation:</b> {finding.get('recommendation')}",
                self.styles['RiskItem']
            ))
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _format_detailed_finding(self, finding: dict) -> list:
        """Format a detailed finding for the technical report."""
        elements = []
        severity = finding.get('severity', 'medium').upper()
        color = self._get_severity_color(severity.lower())
        
        elements.append(Paragraph(
            f"<font color='{color}'><b>[{severity}]</b></font> {finding.get('title', 'Unknown')}",
            self.styles['BodyText']
        ))
        elements.append(Paragraph(
            f"<b>ID:</b> {finding.get('id', 'N/A')} | <b>Category:</b> {finding.get('category', 'N/A')}",
            self.styles['MetricLabel']
        ))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph(
            f"<b>Description:</b> {finding.get('description', '')}",
            self.styles['RiskItem']
        ))
        if finding.get('recommendation'):
            elements.append(Paragraph(
                f"<b>Recommendation:</b> {finding.get('recommendation')}",
                self.styles['RiskItem']
            ))
        if finding.get('framework_controls'):
            elements.append(Paragraph(
                f"<b>Framework Controls:</b> {', '.join(finding.get('framework_controls', []))}",
                self.styles['RiskItem']
            ))
        
        return elements
    
    def generate_executive_report(
        self,
        dashboard: ExecutiveDashboard,
        include_trends: bool = True,
        include_recommendations: bool = True,
    ) -> bytes:
        """
        Generate executive summary PDF report.
        
        Args:
            dashboard: Executive dashboard data
            include_trends: Include trend charts
            include_recommendations: Include recommendations section
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            f"Security Executive Report",
            self.styles['ReportTitle']
        ))
        story.append(Paragraph(
            f"{dashboard.tenant_name}",
            self.styles['Heading2']
        ))
        story.append(Paragraph(
            f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}",
            self.styles['MetricLabel']
        ))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=COLORS['secondary']))
        story.append(Spacer(1, 20))
        
        # Executive Summary Section
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(self._create_summary_table(dashboard))
        story.append(Spacer(1, 20))
        
        # Security Posture
        story.append(Paragraph("Security Posture", self.styles['SectionHeader']))
        story.append(self._create_posture_table(dashboard))
        story.append(Spacer(1, 20))
        
        # Ransomware Readiness
        story.append(Paragraph("Ransomware Readiness", self.styles['SectionHeader']))
        story.append(self._create_backup_table(dashboard))
        story.append(Spacer(1, 20))
        
        # Identity & Access
        story.append(Paragraph("Identity & Access", self.styles['SectionHeader']))
        story.append(self._create_identity_table(dashboard))
        story.append(Spacer(1, 20))
        
        # IT Accountability
        story.append(Paragraph("IT Accountability Metrics", self.styles['SectionHeader']))
        story.append(self._create_accountability_table(dashboard))
        story.append(Spacer(1, 20))
        
        # Top Risks
        if include_recommendations:
            story.append(PageBreak())
            story.append(Paragraph("Top Risks & Recommendations", self.styles['SectionHeader']))
            for i, risk in enumerate(dashboard.top_risks[:5], 1):
                severity_color = self._get_severity_color(risk.severity)
                story.append(Paragraph(
                    f"<font color='{severity_color}'>{i}. [{risk.severity.upper()}]</font> {risk.title}",
                    self.styles['BodyText']
                ))
                story.append(Paragraph(
                    f"{risk.description}",
                    self.styles['RiskItem']
                ))
                story.append(Paragraph(
                    f"<b>Recommendation:</b> {risk.recommendation}",
                    self.styles['RiskItem']
                ))
                story.append(Paragraph(
                    f"<i>Affected Resources: {risk.affected_resources}</i>",
                    self.styles['RiskItem']
                ))
                story.append(Spacer(1, 10))
        
        # Score Trend Chart
        if include_trends and dashboard.score_trend:
            story.append(Paragraph("Score Trend (6 Months)", self.styles['SectionHeader']))
            story.append(self._create_trend_chart(dashboard.score_trend))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=COLORS['secondary']))
        story.append(Paragraph(
            f"Data as of: {dashboard.data_freshness.last_updated}",
            self.styles['MetricLabel']
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_summary_table(self, dashboard: ExecutiveDashboard) -> Table:
        """Create executive summary metrics table."""
        data = [
            ['Security Score', 'Compliance', 'Critical Risks', 'High Risks'],
            [
                f"{dashboard.security_score.current_score:.1f}%",
                f"{dashboard.compliance_score.score_percent:.1f}%",
                str(dashboard.risk_summary.critical_count),
                str(dashboard.risk_summary.high_count),
            ],
        ]
        
        table = Table(data, colWidths=[1.75*inch]*4)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 18),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, 1), 15),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 15),
            ('GRID', (0, 0), (-1, -1), 1, COLORS['secondary']),
        ]))
        
        return table
    
    def _create_posture_table(self, dashboard: ExecutiveDashboard) -> Table:
        """Create security posture table."""
        trend_symbol = lambda t: "↑" if t and t.direction == "up" else "↓" if t and t.direction == "down" else "→"
        
        data = [
            ['Metric', 'Value', 'Trend', 'Status'],
            [
                'Security Score',
                f"{dashboard.security_score.current_score:.1f} / {dashboard.security_score.max_score}",
                f"{trend_symbol(dashboard.security_score.trend)} {dashboard.security_score.trend.change_value if dashboard.security_score.trend else 0:.1f}",
                dashboard.security_score.comparison_label or 'N/A',
            ],
            [
                'Compliance Score',
                f"{dashboard.compliance_score.score_percent:.1f}%",
                f"{trend_symbol(dashboard.compliance_score.trend)} {dashboard.compliance_score.trend.change_value if dashboard.compliance_score.trend else 0:.1f}",
                f"{dashboard.compliance_score.controls_passed}/{dashboard.compliance_score.controls_total} controls",
            ],
            [
                'Device Compliance',
                f"{dashboard.device_compliance.compliance_percent:.1f}%",
                f"{trend_symbol(dashboard.device_compliance.trend)} {dashboard.device_compliance.trend.change_value if dashboard.device_compliance.trend else 0:.1f}",
                f"{dashboard.device_compliance.non_compliant_count} non-compliant",
            ],
        ]
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['secondary']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['white'], colors.HexColor('#F8FAFC')]),
        ]))
        
        return table
    
    def _create_backup_table(self, dashboard: ExecutiveDashboard) -> Table:
        """Create backup/ransomware readiness table."""
        data = [
            ['Metric', 'Value', 'Status'],
            [
                'Backup Health',
                f"{dashboard.backup_health.protected_percent:.1f}%",
                dashboard.backup_health.status.upper(),
            ],
            [
                'Last Successful Backup',
                f"{dashboard.backup_health.hours_since_backup}h ago" if dashboard.backup_health.hours_since_backup else 'N/A',
                'OK' if dashboard.backup_health.hours_since_backup and dashboard.backup_health.hours_since_backup < 24 else 'WARNING',
            ],
            [
                'RTO Status',
                f"{dashboard.recovery_readiness.rto_actual_hours}h / {dashboard.recovery_readiness.rto_target_hours}h target",
                dashboard.recovery_readiness.rto_status.upper(),
            ],
            [
                'RPO Status',
                f"{dashboard.recovery_readiness.rpo_actual_hours}h / {dashboard.recovery_readiness.rpo_target_hours}h target",
                dashboard.recovery_readiness.rpo_status.upper(),
            ],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 2.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['secondary']),
        ]))
        
        return table
    
    def _create_identity_table(self, dashboard: ExecutiveDashboard) -> Table:
        """Create identity & access table."""
        data = [
            ['Metric', 'Value', 'Details'],
            [
                'MFA Coverage (Admins)',
                f"{dashboard.mfa_coverage.admin_coverage_percent:.1f}%",
                f"{dashboard.mfa_coverage.admins_with_mfa}/{dashboard.mfa_coverage.total_admins} admins",
            ],
            [
                'MFA Coverage (All Users)',
                f"{dashboard.mfa_coverage.user_coverage_percent:.1f}%",
                f"{dashboard.mfa_coverage.users_with_mfa}/{dashboard.mfa_coverage.total_users} users",
            ],
            [
                'Global Administrators',
                str(dashboard.privileged_accounts.global_admin_count),
                f"{dashboard.privileged_accounts.pim_eligible_count} PIM eligible",
            ],
            [
                'Risky Users',
                str(dashboard.risky_users.requires_investigation),
                f"High: {dashboard.risky_users.high_risk_count}, Med: {dashboard.risky_users.medium_risk_count}",
            ],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 2*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['secondary']),
        ]))
        
        return table
    
    def _create_accountability_table(self, dashboard: ExecutiveDashboard) -> Table:
        """Create IT accountability metrics table."""
        data = [
            ['Metric', 'Value', 'Target/Details'],
            [
                'Patch SLA Compliance',
                f"{dashboard.patch_sla.compliance_percent:.1f}%",
                f"Target: {dashboard.patch_sla.target_percent}%",
            ],
            [
                'Mean Time to Remediate',
                f"{dashboard.mttr.mttr_days:.1f} days",
                f"Critical: {dashboard.mttr.critical_mttr_days}d, High: {dashboard.mttr.high_mttr_days}d",
            ],
            [
                'Open Findings',
                str(dashboard.finding_age.total_open),
                f"90+ days: {dashboard.finding_age.age_90_plus}",
            ],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 2*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['secondary']),
        ]))
        
        return table
    
    def _create_trend_chart(self, score_trend: list) -> Drawing:
        """Create score trend line chart."""
        drawing = Drawing(500, 200)
        
        # Extract data
        secure_scores = [t.secure_score for t in score_trend]
        compliance_scores = [t.compliance_score or 0 for t in score_trend]
        
        lp = LinePlot()
        lp.x = 50
        lp.y = 30
        lp.height = 150
        lp.width = 400
        
        lp.data = [
            list(enumerate(secure_scores)),
            list(enumerate(compliance_scores)),
        ]
        
        lp.lines[0].strokeColor = COLORS['accent']
        lp.lines[0].strokeWidth = 2
        lp.lines[1].strokeColor = COLORS['success']
        lp.lines[1].strokeWidth = 2
        
        lp.xValueAxis.valueMin = 0
        lp.xValueAxis.valueMax = len(score_trend) - 1
        lp.yValueAxis.valueMin = 0
        lp.yValueAxis.valueMax = 100
        
        drawing.add(lp)
        
        # Legend
        drawing.add(String(460, 170, "Secure Score", fontSize=8, fillColor=COLORS['accent']))
        drawing.add(String(460, 155, "Compliance", fontSize=8, fillColor=COLORS['success']))
        
        return drawing
    
    def _get_severity_color(self, severity: str) -> str:
        """Get hex color for severity level."""
        colors_map = {
            'critical': '#EF4444',
            'high': '#F97316',
            'medium': '#EAB308',
            'low': '#3B82F6',
        }
        return colors_map.get(severity.lower(), '#64748B')


# Factory function
def create_pdf_report(
    dashboard: ExecutiveDashboard,
    report_type: str = 'executive',
    **kwargs
) -> bytes:
    """
    Create a PDF report.
    
    Args:
        dashboard: Dashboard data
        report_type: Type of report ('executive', 'compliance', 'vulnerability')
        **kwargs: Additional options
        
    Returns:
        PDF file as bytes
    """
    generator = PDFReportGenerator()
    
    if report_type == 'executive':
        return generator.generate_executive_report(
            dashboard,
            include_trends=kwargs.get('include_trends', True),
            include_recommendations=kwargs.get('include_recommendations', True),
        )
    else:
        # Default to executive report
        return generator.generate_executive_report(dashboard)
