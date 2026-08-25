import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from app.models.models import Project, FabricAnalysis, Fabric, DyeMethod

def generate_pdf_sustainability_report(
    project: Project,
    analysis: FabricAnalysis,
    selected_fabric: Fabric,
    selected_dye: DyeMethod,
    impact_data: dict
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    c_forest = colors.HexColor("#1C3A27")
    c_sage = colors.HexColor("#8A9A86")
    c_charcoal = colors.HexColor("#222525")
    c_cream = colors.HexColor("#F9F7F1")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=c_forest,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=c_sage,
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'H2Header',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=c_forest,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        textColor=c_charcoal,
        leading=14
    )

    elements = []

    elements.append(Paragraph("SUSTAINABLE FASHION IMPACT REPORT", title_style))
    elements.append(Paragraph(f"Project: {project.title} | Target: {project.target_garment_type or 'Garment'}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=c_sage, spaceAfter=15))

    elements.append(Paragraph("1. Original Garment Inspiration Analysis", h2_style))
    analysis_text = (
        f"<b>Detected Fabric:</b> {analysis.fabric_type}<br/>"
        f"<b>Garment Category:</b> {analysis.garment_category}<br/>"
        f"<b>Texture / Weave:</b> {analysis.weave} (Thickness: {analysis.thickness}, Drape: {analysis.drape})<br/>"
        f"<b>Colors:</b> {', '.join(analysis.dominant_colors or [])}"
    )
    elements.append(Paragraph(analysis_text, body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. Selected Sustainable Alternatives", h2_style))
    alt_data = [
        ["Category", "Selected Choice", "Key Benefit"],
        ["Fabric Fiber", selected_fabric.name, f"Water Score: {selected_fabric.water_impact_score}/100, Carbon Score: {selected_fabric.carbon_impact_score}/100"],
        ["Dyeing Method", selected_dye.name, f"Water Impact: {selected_dye.water_impact_level}, Energy Impact: {selected_dye.energy_impact_level}"]
    ]
    alt_table = Table(alt_data, colWidths=[120, 160, 250])
    alt_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_forest),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), c_cream),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
    ]))
    elements.append(alt_table)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("3. Estimated Lifecycle Reductions", h2_style))
    summary_msg = impact_data.get("summary_text", "Significant reduction in water and carbon emissions achieved.")
    elements.append(Paragraph(f"<b>Executive Summary:</b> {summary_msg}", body_style))
    elements.append(Spacer(1, 10))

    metrics_table_data = [
        ["Metric", "Conventional Baseline", "Sustainable Alternative", "Estimated Reduction"],
        ["Water Usage", f"{impact_data.get('water_comparison', {}).get('conventional', 0)} L", f"{impact_data.get('water_comparison', {}).get('sustainable', 0)} L", f"<b>{impact_data.get('water_saved_liters', 0)} L Saved</b>"],
        ["CO2 Emissions", f"{impact_data.get('co2_comparison', {}).get('conventional', 0)} kg", f"{impact_data.get('co2_comparison', {}).get('sustainable', 0)} kg", f"<b>{impact_data.get('co2_reduced_kg', 0)} kg CO2 Reduced</b>"],
        ["Textile Waste", "Standard Scrap", "Zero-Waste Patterning", f"<b>{impact_data.get('waste_reduced_kg', 0)} kg Reduced</b>"],
        ["Chemical Load", "High Toxicity", "Non-Toxic / Organic", f"<b>{impact_data.get('chemical_reduction_pct', 0)}% Lower Impact</b>"]
    ]
    m_table = Table(metrics_table_data, colWidths=[120, 140, 140, 130])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_sage),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(m_table)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<b>Assumptions & Transparency Disclosure:</b>", h2_style))
    for note in impact_data.get("assumptions", []):
        elements.append(Paragraph(f"• {note}", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
