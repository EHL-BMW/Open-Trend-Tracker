import os
import shutil
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
import fitz # PyMuPDF

# Palette definition
C_PRIMARY = colors.HexColor("#0F172A")    # Deep Navy
C_ACCENT = colors.HexColor("#0066B1")     # BMW Electric Blue
C_ACCENT_LIGHT = colors.HexColor("#E0F2FE")
C_DARK = colors.HexColor("#1E293B")       # Slate 800
C_TEXT = colors.HexColor("#334155")       # Slate 700
C_MUTED = colors.HexColor("#64748B")      # Slate 500
C_BORDER = colors.HexColor("#CBD5E1")     # Slate 300
C_BORDER_LIGHT = colors.HexColor("#E2E8F0")
C_BG_LIGHT = colors.HexColor("#F8FAFC")   # Slate 50
C_BG_ALT = colors.HexColor("#F1F5F9")     # Slate 100
C_RED = colors.HexColor("#DC2626")
C_AMBER = colors.HexColor("#D97706")
C_GREEN = colors.HexColor("#059669")
C_PURPLE = colors.HexColor("#7C3AED")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica", 8)
            self.setFillColor(C_MUTED)
            self.drawString(40, 755, "BMW Technology Domains: Ranking & Sentiment Methodology Report")
            self.drawRightString(572, 755, "Mathematical Modeling & Customer Voice Study 2025")
            self.setStrokeColor(C_BORDER_LIGHT)
            self.setLineWidth(0.75)
            self.line(40, 747, 572, 747)

        # Footer (all pages)
        self.setStrokeColor(C_BORDER_LIGHT)
        self.setLineWidth(0.75)
        self.line(40, 38, 572, 38)
        self.setFont("Helvetica", 8)
        self.setFillColor(C_MUTED)
        self.drawString(40, 26, "CONFIDENTIAL – Automotive Customer Analytics & Engineering Pipeline Benchmark")
        self.drawRightString(572, 26, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()

def build_pdf():
    pdf_path = "/Users/miao/Desktop/Hackathon/BMW_Technology_Domains_Ranking_and_Methodology.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=C_PRIMARY,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=C_ACCENT,
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=C_PRIMARY,
        spaceBefore=7,
        spaceAfter=4
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=C_DARK,
        spaceBefore=4,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=C_TEXT,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=C_DARK
    )

    formula_style = ParagraphStyle(
        'FormulaText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1E3A8A")
    )

    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1 # Center
    )

    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=C_TEXT
    )

    td_center_style = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=C_TEXT,
        alignment=1
    )

    td_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=C_DARK
    )

    story = []

    # ==========================================
    # PAGE 1: TITLE, METHODOLOGY & MATHEMATICAL FORMULATION
    # ==========================================
    story.append(Paragraph("BMW EV/PHEV Technology Domains: Ranking & Sentiment Methodology", title_style))
    story.append(Paragraph("Mathematical Modeling, Derivation of Likes vs. Friction, Net Sentiment Formulation & Severity Weighting", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_ACCENT, spaceBefore=0, spaceAfter=8))

    # KPI Banner (4 boxes)
    kpi_data = [
        [
            Paragraph("<b>Total Analyzed Records</b><br/><font size=12 color='#0066B1'><b>3,971 Records</b></font><br/><font size=6 color='#64748B'>16 Models (100% ICE Excluded)</font>", td_center_style),
            Paragraph("<b>Positive Praise (Likes)</b><br/><font size=12 color='#059669'><b>1,491 Cases</b></font><br/><font size=6 color='#64748B'>Promoter Voice / Excitement</font>", td_center_style),
            Paragraph("<b>Customer Friction</b><br/><font size=12 color='#DC2626'><b>1,892 Cases</b></font><br/><font size=6 color='#64748B'>Defect + Diff. to Use + Wants</font>", td_center_style),
            Paragraph("<b>Evaluated Universe</b><br/><font size=12 color='#0F172A'><b>3,383 Cases</b></font><br/><font size=6 color='#64748B'>Likes + Real Pain Points</font>", td_center_style)
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[133, 133, 133, 133])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Data Provenance: How 'Likes' and 'Friction' Were Derived", h1_style))
    story.append(Paragraph(
        "Die Rohdaten entstammen den offiziellen BMW-Kundenstudien der aktuellen Modellgenerationen "
        "(<code>G60_feedback_hackathon.xlsx</code> und <code>G70_feedback_hackathon.xlsx</code>). "
        "Um strikte Datenintegrität zu gewährleisten, wurden alle reinen Verbrenner (ICE) und der 1er (F70) herausgefiltert. "
        "In der verifizierten Schnittmenge von <b>16 elektrifizierten BMW Modellen</b> (i5 BEV, i7 BEV, 5er PHEV, 7er PHEV) "
        "ist jeder Datensatz in der Spalte <code>Feedback Type</code> exakt einer von vier Kategorien zugeordnet:",
        body_style
    ))

    # Data Categorization Table
    cat_headers = [
        Paragraph("<b>Category (Feedback Type)</b>", th_style),
        Paragraph("<b>Volume</b>", th_style),
        Paragraph("<b>Methodological Definition in Automotive Pipeline</b>", th_style),
        Paragraph("<b>Classification</b>", th_style)
    ]
    cat_rows = [
        [
            Paragraph("<b>Likes</b>", td_bold_style),
            Paragraph("1.491", td_center_style),
            Paragraph("Explicit customer praise, admiration for driving dynamics, design, or acoustic comfort. Functions as a <b>Promoter Signal</b>.", td_style),
            Paragraph("<font color='#059669'><b>Positive Praise</b></font>", td_style)
        ],
        [
            Paragraph("<b>Difficult to Use (DTU)</b>", td_bold_style),
            Paragraph("1.007", td_center_style),
            Paragraph("Ergonomic hurdles, deeply nested menus, unintuitive logic, or oversensitive sensors. System functions but frustrates the driver.", td_style),
            Paragraph("<font color='#D97706'><b>UX Friction (Weight 2)</b></font>", td_style)
        ],
        [
            Paragraph("<b>Defect</b>", td_bold_style),
            Paragraph("392", td_center_style),
            Paragraph("Real hardware component failures, system crashes, frozen charging flaps, or jammed automated doors.", td_style),
            Paragraph("<font color='#DC2626'><b>Hard Malfunction (Weight 3)</b></font>", td_style)
        ],
        [
            Paragraph("<b>Wants</b>", td_bold_style),
            Paragraph("493", td_center_style),
            Paragraph("Unmet customer needs, missing equipment (e.g. panoramic roof tilt/slide function) or requested software features.", td_style),
            Paragraph("<font color='#2563EB'><b>Feature Gap (Weight 1)</b></font>", td_style)
        ]
    ]
    t_cat = Table([cat_headers] + cat_rows, colWidths=[110, 55, 260, 107])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. Mathematical Formulations: Net Sentiment & Severity Score", h1_style))

    # Mathematical Formula Box
    formula_box = [
        [
            Paragraph("<b>A. Net Sentiment Score (Formulated Analogously to Net Promoter Score / NPS):</b><br/>"
                      "<font face='Courier' color='#1E3A8A' size=8>"
                      "Net Sentiment (%) = [ ( N_Likes - N_Friction ) / ( N_Likes + N_Friction ) ] * 100%"
                      "</font><br/>"
                      "• <b>Scale:</b> Ranges from <b>+100%</b> (pure customer praise) to <b>-100%</b> (pure complaint friction).<br/>"
                      "• <b>Interpretation:</b> Values above <b>0%</b> represent net positive advocacy. Negative values denote that friction outweighs praise.", callout_style),
            Paragraph("<b>B. Weighted Severity Score (Average Severity Score):</b><br/>"
                      "<font face='Courier' color='#1E3A8A' size=8>"
                      "Severity = [ 3 * N_Defect + 2 * N_DiffToUse + 1 * N_Wants ] / N_Friction"
                      "</font><br/>"
                      "• <b>Scale:</b> Ranges from <b>1.00</b> (pure feature requests) to <b>3.00</b> (hard hardware defects).<br/>"
                      "• <b>Priority Backlog Index (Action Leverage):</b><br/>"
                      "<font face='Courier' color='#1E3A8A' size=8>Prio Index = N_Friction * Severity</font>", callout_style)
        ]
    ]
    t_form = Table(formula_box, colWidths=[266, 266])
    t_form.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#7DD3FC")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_form)

    story.append(PageBreak())

    # ==========================================
    # PAGE 2: COMPLETE DOMAIN RANKING TABLE & ANALYSIS
    # ==========================================
    story.append(Paragraph("3. Comprehensive Technology Domain Ranking (Ranked by Net Sentiment)", h1_style))
    story.append(Paragraph("The following table details the official ranking of all 7 technology domains (plus General/Services). The Net Sentiment Score rigorously isolates BMW's competitive brand moats from severe architectural friction areas.", body_style))

    # Full Ranking Table
    rank_headers = [
        Paragraph("<b>Rank & Domain</b>", th_style),
        Paragraph("<b>Aspect Focus</b>", th_style),
        Paragraph("<b>Praise<br/>(Likes)</b>", th_style),
        Paragraph("<b>Friction<br/>(Complaints)</b>", th_style),
        Paragraph("<b>Evaluated<br/>Universe</b>", th_style),
        Paragraph("<b>Net Sentiment<br/>Score</b>", th_style),
        Paragraph("<b>Avg. Severity<br/>(1–3)</b>", th_style),
        Paragraph("<b>Status & Engineering Takeaway</b>", th_style)
    ]

    rank_rows = [
        [
            Paragraph("<b>1. Vehicle Dynamics</b>", td_bold_style),
            Paragraph("Drivetrain control, chassis, active brakes", td_style),
            Paragraph("<b>630</b>", td_center_style),
            Paragraph("241", td_center_style),
            Paragraph("871", td_center_style),
            Paragraph("<font color='#059669'><b>+44,7 %</b></font>", td_center_style),
            Paragraph("1,93", td_center_style),
            Paragraph("<font color='#059669'><b>Brand Moat</b></font>: Benchmark chassis beats friction.", td_style)
        ],
        [
            Paragraph("<b>2. Smart Cabin</b>", td_bold_style),
            Paragraph("Thermal comfort, seating, acoustics, space", td_style),
            Paragraph("257", td_center_style),
            Paragraph("327", td_center_style),
            Paragraph("584", td_center_style),
            Paragraph("<font color='#D97706'><b>-12,0 %</b></font>", td_center_style),
            Paragraph("1,87", td_center_style),
            Paragraph("<font color='#D97706'><b>Mixed</b></font>: Acoustics top; Veganza leather sweaty.", td_style)
        ],
        [
            Paragraph("<b>3. Smart Exterior</b>", td_bold_style),
            Paragraph("Smart bodywork, doors, lighting, aero", td_style),
            Paragraph("224", td_center_style),
            Paragraph("323", td_center_style),
            Paragraph("547", td_center_style),
            Paragraph("<font color='#D97706'><b>-18,1 %</b></font>", td_center_style),
            Paragraph("1,93", td_center_style),
            Paragraph("<font color='#D97706'><b>Hardware top</b></font>, but door sensors frustrate.", td_style)
        ],
        [
            Paragraph("<b>4. Digital Cockpit & AI</b>", td_bold_style),
            Paragraph("Display HMI, voice assistant, entertainment", td_style),
            Paragraph("153", td_center_style),
            Paragraph("296", td_center_style),
            Paragraph("449", td_center_style),
            Paragraph("<font color='#DC2626'><b>-31,8 %</b></font>", td_center_style),
            Paragraph("<b>2,03</b>", td_center_style),
            Paragraph("<font color='#DC2626'><b>Critical Area</b></font>: Highest severity (OS 8.5 menus).", td_style)
        ],
        [
            Paragraph("<b>5. Driving Assistance</b>", td_bold_style),
            Paragraph("Highway/City pilot, automated parking, handoff", td_style),
            Paragraph("68", td_center_style),
            Paragraph("154", td_center_style),
            Paragraph("222", td_center_style),
            Paragraph("<font color='#DC2626'><b>-38,7 %</b></font>", td_center_style),
            Paragraph("1,94", td_center_style),
            Paragraph("<font color='#DC2626'><b>GSR2 Friction</b></font>: Highway Assist top; speed bongs annoy.", td_style)
        ],
        [
            Paragraph("<b>6. Energy & Charging</b>", td_bold_style),
            Paragraph("Charging UX, preconditioning, winter range", td_style),
            Paragraph("125", td_center_style),
            Paragraph("315", td_center_style),
            Paragraph("440", td_center_style),
            Paragraph("<font color='#DC2626'><b>-43,2 %</b></font>", td_center_style),
            Paragraph("1,94", td_center_style),
            Paragraph("<font color='#DC2626'><b>Cold Charge Trap</b></font>: Winter range drops disappoint.", td_style)
        ],
        [
            Paragraph("<b>7. General & Services*</b>", td_style),
            Paragraph("Owner's manual, dealership delivery & service", td_style),
            Paragraph("6", td_center_style),
            Paragraph("24", td_center_style),
            Paragraph("30", td_center_style),
            Paragraph("-60,0 %", td_center_style),
            Paragraph("1,96", td_center_style),
            Paragraph("Low volume; primarily digital onboard manual.", td_style)
        ],
        [
            Paragraph("<b>8. Connected Ecosystem</b>", td_bold_style),
            Paragraph("Smartphone app, remote services, OTA upgrades", td_style),
            Paragraph("28", td_center_style),
            Paragraph("212", td_center_style),
            Paragraph("240", td_center_style),
            Paragraph("<font color='#DC2626'><b>-76,7 %</b></font>", td_center_style),
            Paragraph("2,00", td_center_style),
            Paragraph("<font color='#DC2626'><b>Crisis Point</b></font>: Garage connection timeouts, CarPlay drops.", td_style)
        ],
        [
            Paragraph("<b>Total Universe / Weighted Average</b>", td_bold_style),
            Paragraph("<b>All 16 Electrified BMW Models</b>", td_bold_style),
            Paragraph("<b>1.491</b>", td_center_style),
            Paragraph("<b>1.892</b>", td_center_style),
            Paragraph("<b>3.383</b>", td_center_style),
            Paragraph("<b>-11,8 %</b>", td_center_style),
            Paragraph("<b>1,95</b>", td_center_style),
            Paragraph("<b>Verified Baseline (100% ICE Excluded)</b>", td_bold_style)
        ]
    ]

    t_rank = Table([rank_headers] + rank_rows, colWidths=[105, 115, 38, 42, 45, 55, 42, 90])
    t_rank.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, C_BG_LIGHT]),
        ('BACKGROUND', (0,-1), (-1,-1), C_BG_ALT),
        ('LINEABOVE', (0,-1), (-1,-1), 1.5, C_DARK),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_rank)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. Strategic Synthesis & Engineering Roadmap Implications", h1_style))

    summary_boxes = [
        [
            Paragraph(
                "<b>1. Mechanische Exzellenz vs. Digitale Reife:</b><br/>"
                "BMW erzielt im Fahrwerk (<i>Vehicle Dynamics</i>) mit <b>+44,7 % Net Sentiment</b> eine überragende Dominanz. "
                "Kein chinesischer oder europäischer Wettbewerber erreicht diesen Komfort. "
                "Demgegenüber steht <i>Connected Ecosystem</i> mit <b>-76,7 %</b> – hier erwarten Premiumkunden sofortige Cloud-Reaktion ohne Timeouts.",
                callout_style
            ),
            Paragraph(
                "<b>2. Der 'Difficult to Use'-Faktor (UX vor Hardware):</b><br/>"
                "Über <b>53 % aller Beanstandungen</b> sind keine Hardwaredefekte, sondern UX-Reibungspunkte. "
                "Die teuerste Erkenntnis: Das Über-Engineering von mechatronischen Automatiktüren und Touch-Klimamenüs "
                "erzeugt mehr Unzufriedenheit als schlichte physische Lösungen.",
                callout_style
            )
        ]
    ]
    t_sum = Table(summary_boxes, colWidths=[266, 266])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_ACCENT_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#7DD3FC")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_sum)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {pdf_path}")

    # Copy to brain artifacts
    artifact_pdf = "/Users/miao/.gemini/antigravity-ide/brain/50b3aecf-d9ce-4482-b37b-c634a4750503/BMW_Technology_Domains_Ranking_and_Methodology.pdf"
    shutil.copy2(pdf_path, artifact_pdf)

    # Render PNG previews
    doc_fitz = fitz.open(pdf_path)
    for p_idx in range(len(doc_fitz)):
        page = doc_fitz[p_idx]
        pix = page.get_pixmap(dpi=150)
        png_out = f"/Users/miao/.gemini/antigravity-ide/brain/50b3aecf-d9ce-4482-b37b-c634a4750503/methodology_report_page_{p_idx+1}.png"
        pix.save(png_out)
        print(f"Saved page preview: {png_out}")

build_pdf()
