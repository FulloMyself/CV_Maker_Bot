from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def generate_ats_cv(cv_data, output_path):
    """
    Generate an ATS-compliant CV PDF
    ATS-friendly features:
    - Simple, clean layout
    - Standard fonts
    - No columns, graphics, or tables for critical info
    - Clear section headings
    - Proper keyword placement
    """
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles for ATS compliance
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.black,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    story = []
    
    # Header - Name
    personal = cv_data['personal_info']
    story.append(Paragraph(personal['full_name'].upper(), title_style))
    
    # Contact Information
    contact_info = []
    if personal.get('phone'):
        contact_info.append(f"📞 {personal['phone']}")
    if personal.get('email'):
        contact_info.append(f"✉ {personal['email']}")
    if personal.get('address'):
        contact_info.append(f"📍 {personal['address']}")
    if personal.get('linkedin'):
        contact_info.append(f"🔗 {personal['linkedin']}")
    if personal.get('portfolio'):
        contact_info.append(f"🌐 {personal['portfolio']}")
    
    contact_text = " | ".join(contact_info)
    story.append(Paragraph(contact_text, normal_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.2 * inch))
    
    # Professional Summary
    if cv_data.get('professional_summary'):
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(cv_data['professional_summary'], normal_style))
        story.append(Spacer(1, 0.1 * inch))
    
    # Work Experience
    if cv_data.get('work_experience'):
        story.append(Paragraph("WORK EXPERIENCE", heading_style))
        for exp in cv_data['work_experience']:
            # Job title and company
            title_text = f"<b>{exp['title']}</b>"
            if exp.get('company'):
                title_text += f" | {exp['company']}"
            story.append(Paragraph(title_text, normal_style))
            
            # Dates
            if exp.get('start_date') or exp.get('end_date'):
                date_text = f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}"
                story.append(Paragraph(date_text, normal_style))
            
            # Responsibilities
            if exp.get('responsibilities'):
                story.append(Paragraph(exp['responsibilities'], normal_style))
            
            story.append(Spacer(1, 0.1 * inch))
    
    # Education
    if cv_data.get('education'):
        story.append(Paragraph("EDUCATION", heading_style))
        for edu in cv_data['education']:
            degree_text = f"<b>{edu['degree']}</b>"
            if edu.get('institution'):
                degree_text += f" - {edu['institution']}"
            story.append(Paragraph(degree_text, normal_style))
            
            if edu.get('grad_year'):
                story.append(Paragraph(f"Graduated: {edu['grad_year']}", normal_style))
            
            story.append(Spacer(1, 0.1 * inch))
    
    # Skills
    if cv_data.get('skills'):
        story.append(Paragraph("SKILLS", heading_style))
        skills_text = ", ".join(cv_data['skills'])
        story.append(Paragraph(skills_text, normal_style))
        story.append(Spacer(1, 0.1 * inch))
    
    # Certifications
    if cv_data.get('certifications'):
        story.append(Paragraph("CERTIFICATIONS", heading_style))
        for cert in cv_data['certifications']:
            cert_text = f"<b>{cert['name']}</b>"
            if cert.get('issuer'):
                cert_text += f" | {cert['issuer']}"
            if cert.get('year'):
                cert_text += f" | {cert['year']}"
            story.append(Paragraph(cert_text, normal_style))
        story.append(Spacer(1, 0.1 * inch))
    
    # Languages
    if cv_data.get('languages'):
        story.append(Paragraph("LANGUAGES", heading_style))
        languages_text = ", ".join(cv_data['languages'])
        story.append(Paragraph(languages_text, normal_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ ATS-Compliant CV generated: {output_path}")