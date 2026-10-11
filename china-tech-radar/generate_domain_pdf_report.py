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
            self.drawString(40, 755, "BMW Group Customer Studies – Technology Domain & Complaint Pipeline Report")
            self.drawRightString(572, 755, "BMW EV / PHEV Cohort Study 2025")
            self.setStrokeColor(C_BORDER_LIGHT)
            self.setLineWidth(0.75)
            self.line(40, 747, 572, 747)

        # Footer (all pages)
        self.setStrokeColor(C_BORDER_LIGHT)
        self.setLineWidth(0.75)
        self.line(40, 38, 572, 38)
        self.setFont("Helvetica", 8)
        self.setFillColor(C_MUTED)
        self.drawString(40, 26, "CONFIDENTIAL & PROPRIETARY – Automotive Engineering & Data Pipeline Benchmark")
        self.drawRightString(572, 26, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()

def build_pdf():
    pdf_path = "/Users/miao/Desktop/Hackathon/BMW_EV_Technology_Domains_Analysis_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=19,
        leading=23,
        textColor=C_PRIMARY,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13.5,
        textColor=C_ACCENT,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=C_PRIMARY,
        spaceBefore=8,
        spaceAfter=5
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
        spaceAfter=5
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=C_DARK
    )

    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=9.8,
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

    quote_style = ParagraphStyle(
        'QuoteStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor("#1E3A8A")
    )

    story = []

    # ==========================================
    # PAGE 1: TITLE, EXECUTIVE SUMMARY & METHODOLOGY CHECK
    # ==========================================
    story.append(Paragraph("BMW EV / PHEV Technology Domain & Complaint Analysis", title_style))
    story.append(Paragraph("Systematic evaluation of 1,892 electrified customer complaints across 7 technology domains (i5 BEV, i7 BEV, 5 Series PHEV, 7 Series PHEV)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_ACCENT, spaceBefore=0, spaceAfter=8))

    # KPI Banner (4 boxes)
    kpi_data = [
        [
            Paragraph("<b>Electrified Cohorts</b><br/><font size=12 color='#0066B1'><b>4 Model Groups</b></font><br/><font size=6 color='#64748B'>i5, i7, 5er PHEV, 7er PHEV</font>", td_center_style),
            Paragraph("<b>Total Feedback Pool</b><br/><font size=12 color='#0F172A'><b>3,971 Records</b></font><br/><font size=6 color='#64748B'>100% ICE Models Excluded</font>", td_center_style),
            Paragraph("<b>Verified Complaints</b><br/><font size=12 color='#DC2626'><b>1,892 Cases</b></font><br/><font size=6 color='#64748B'>Difficult to Use + Defect + Wants</font>", td_center_style),
            Paragraph("<b>Technology Domains</b><br/><font size=12 color='#059669'><b>7 Core Domains</b></font><br/><font size=6 color='#64748B'>NEV / SDV Industry Standard</font>", td_center_style)
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

    story.append(Paragraph("1. Architectural Validation & Plausibility Audit of the 7 Technology Domains", h1_style))
    story.append(Paragraph(
        "Die vorgegebene 7-gliedrige Technologie-Taxonomie wurde gegen etablierte Benchmark-Standards "
        "(Dongchedi, CPCA NEV Index, McKinsey Connected Car Architecture, ISO 26262 / SAE J3016) geprüft. "
        "<b>Ergebnis: Die Taxonomie ist methodisch vollständig valide, trennscharf und MECE</b> "
        "(Mutually Exclusive, Collectively Exhaustive). "
        "Die Ergänzung um <i>Smart Exterior</i> schließt die entscheidende Lücke moderner mechatronischer Karosserieaktoren.",
        body_style
    ))

    # Taxonomy Assessment Table (using German & English text to avoid CJK rendering issues in Helvetica)
    tax_headers = [
        Paragraph("<b>Technology Domain</b>", th_style),
        Paragraph("<b>Aspect Focus</b>", th_style),
        Paragraph("<b>Feature Scope & Examples</b>", th_style),
        Paragraph("<b>Methodological Assessment</b>", th_style)
    ]
    tax_rows = [
        [
            Paragraph("<b>1. Energy & Charging</b>", td_bold_style),
            Paragraph("Charging UX, thermal pre-conditioning, range management & V2X", td_style),
            Paragraph("Charging route planning, battery pre-heating, DC fast-charging curve, Plug&Charge, V2L", td_style),
            Paragraph("<font color='#059669'><b>Valid:</b></font> Isolates core friction points of pure EV ownership.", td_style)
        ],
        [
            Paragraph("<b>2. Driving Assistance</b>", td_bold_style),
            Paragraph("Highway/City pilot, automated parking, handoff & GSR2 compliance", td_style),
            Paragraph("Highway Assistant (L2+ hands-free), Parking Assistant Pro, speed limit alerts, handoff", td_style),
            Paragraph("<font color='#059669'><b>Valid:</b></font> Industry standard for ADAS/AD perception and actuation.", td_style)
        ],
        [
            Paragraph("<b>3. Digital Cockpit & AI</b>", td_bold_style),
            Paragraph("Display HMI, voice assistant & in-cabin entertainment", td_style),
            Paragraph("Curved Display, QuickSelect OS 8.5/9, Theatre Screen (i7), NLU voice assistant (IPA), B&W sound", td_style),
            Paragraph("<font color='#059669'><b>Valid:</b></font> In-cabin HMI, compute, and multimodal user interaction.", td_style)
        ],
        [
            Paragraph("<b>4. Connected Ecosystem</b>", td_bold_style),
            Paragraph("Smartphone integration, remote telematics & OTA services", td_style),
            Paragraph("My BMW App, Digital Key Plus (UWB), Remote Software Upgrade (OTA), Personal eSIM 5G", td_style),
            Paragraph("<font color='#059669'><b>Valid:</b></font> Delineates onboard vehicle systems from cloud/mobile services.", td_style)
        ],
        [
            Paragraph("<b>5. Smart Cabin</b>", td_bold_style),
            Paragraph("Thermal comfort, seating, acoustics, air quality & ergonomics", td_style),
            Paragraph("Veganza/Merino seating, 4-zone climate, acoustic glass, center console, panoramic roof", td_style),
            Paragraph("<font color='#059669'><b>Valid:</b></font> Physical micro-climate comfort (hardware, haptics, materials).", td_style)
        ],
        [
            Paragraph("<b>6. Vehicle Dynamics & Safety</b>", td_bold_style),
            Paragraph("Drivetrain control, chassis, active braking & occupant safety", td_style),
            Paragraph("Recuperation (B-mode), 2-axle air suspension, Integral Active Steering, brake blending, CPD", td_style),
            Paragraph("<font color='#059669'><b>Valid:</b></font> BMW core brand competency: longitudinal/lateral dynamics & safety.", td_style)
        ],
        [
            Paragraph("<b>7. Smart Exterior</b>", td_bold_style),
            Paragraph("Smart bodywork, motorized doors, active lighting & aerodynamics", td_style),
            Paragraph("Motorized doors (i7), hands-free tailgate kick sensor, flush handles, Matrix LED", td_style),
            Paragraph("<font color='#059669'><b>Valid:</b></font> Indispensable for modern luxury-tier exterior mechatronics.", td_style)
        ]
    ]

    t_tax = Table([tax_headers] + tax_rows, colWidths=[98, 120, 202, 112])
    t_tax.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tax)
    story.append(Spacer(1, 7))

    # Strategic Insight Box
    callout_content = [
        [
            Paragraph(
                "<b>Taxonomic Boundary Rules for Automated Ingestion Pipelines:</b><br/>"
                "• <b>Voice Assistant & NLU:</b> Strictly allocated to <i>Digital Cockpit & AI</i> (multimodal interaction layer).<br/>"
                "• <b>Seat Climate vs. Infotainment:</b> Physical heating/ventilation in <i>Smart Cabin</i>; touchscreen controls in <i>Digital Cockpit & AI</i>.<br/>"
                "• <b>Connected Services:</b> All smartphone-enabled features (Digital Key, My BMW App, OTA) strictly in <i>Connected Ecosystem</i>.",
                callout_style
            )
        ]
    ]
    t_callout = Table(callout_content, colWidths=[532])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_ACCENT_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#7DD3FC")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_callout)

    story.append(PageBreak())

    # ==========================================
    # PAGE 2: QUANTITATIVE MATRIX & COHORT BENCHMARK
    # ==========================================
    story.append(Paragraph("2. Quantitative Domain Ranking & Cohort Distribution Matrix", h1_style))
    story.append(Paragraph(
        "Distribution of all 1,892 verified customer complaints across the 4 electrified BMW model cohorts. "
        "All data points originate from the verified intersection of G60 (5 Series/i5) and G70 (7 Series/i7), strictly cleaned of combustion engine records.",
        body_style
    ))

    # Matrix Table
    matrix_headers = [
        Paragraph("<b>Technology Domain</b>", th_style),
        Paragraph("<b>i5 BEV<br/>(G60/61)</b>", th_style),
        Paragraph("<b>i7 BEV<br/>(G70)</b>", th_style),
        Paragraph("<b>5 Series PHEV<br/>(G60)</b>", th_style),
        Paragraph("<b>7 Series PHEV<br/>(G70)</b>", th_style),
        Paragraph("<b>Total<br/>Cases</b>", th_style),
        Paragraph("<b>Share<br/>%</b>", th_style),
        Paragraph("<b>Primary Problem Components</b>", th_style)
    ]

    matrix_rows_data = [
        ("Smart Cabin", "144", "108", "36", "39", "327", "17,28 %", "Seats & upholstery (39); Sunroof (21); Climate (17)"),
        ("Smart Exterior", "150", "94", "41", "38", "323", "17,07 %", "Body gaps/seals (60); Kick sensor (24); Doors (22)"),
        ("Energy & Charging", "167", "101", "26", "21", "315", "16,65 %", "Winter real range (97); DC fast-charging (64); HV battery (43)"),
        ("Digital Cockpit & AI", "125", "114", "34", "23", "296", "15,64 %", "Infotainment OS 8.5 (39); B&W Audio (28); Nav (26)"),
        ("Vehicle Dynamics & Safety", "102", "76", "37", "26", "241", "12,74 %", "PHEV kickdown transition (45); My Modes (29); Recuperation (19)"),
        ("Connected Ecosystem", "93", "80", "23", "16", "212", "11,21 %", "CarPlay (31); Personal eSIM (27); My BMW App (24)"),
        ("Driving Assistance", "66", "55", "23", "10", "154", "8,14 %", "Parking Assistant (21); Highway Assist (15); GSR2 speed warnings (15)"),
        ("General & Services*", "8", "11", "1", "4", "24", "1,27 %", "General inquiries (15); Digital manual (9)"),
    ]

    table_data = [matrix_headers]
    for r in matrix_rows_data:
        is_gen = "*" in r[0]
        table_data.append([
            Paragraph(f"<b>{r[0]}</b>", td_bold_style if not is_gen else td_style),
            Paragraph(r[1], td_center_style),
            Paragraph(r[2], td_center_style),
            Paragraph(r[3], td_center_style),
            Paragraph(r[4], td_center_style),
            Paragraph(f"<b>{r[5]}</b>", td_center_style),
            Paragraph(f"<b>{r[6]}</b>", td_center_style),
            Paragraph(r[7], td_style)
        ])
    # Add Total row
    table_data.append([
        Paragraph("<b>Total Universe</b>", td_bold_style),
        Paragraph("<b>855</b>", td_center_style),
        Paragraph("<b>639</b>", td_center_style),
        Paragraph("<b>221</b>", td_center_style),
        Paragraph("<b>177</b>", td_center_style),
        Paragraph("<b>1.892</b>", td_center_style),
        Paragraph("<b>100,0 %</b>", td_center_style),
        Paragraph("<b>Full Verified Baseline</b>", td_bold_style)
    ])

    t_matrix = Table(table_data, colWidths=[108, 44, 44, 44, 44, 42, 44, 162])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, C_BG_LIGHT]),
        ('BACKGROUND', (0,-1), (-1,-1), C_BG_ALT),
        ('LINEABOVE', (0,-1), (-1,-1), 1.5, C_DARK),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_matrix)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. Failure Category & Severity Distribution (Pipeline Metric Layer)", h1_style))
    story.append(Paragraph(
        "Für die Weiterverarbeitung in Data Pipelines werden Beanstandungen nach Feedback-Typ und Gewichtung segmentiert: "
        "<b>Defect (Gewicht 3)</b> = Technische Fehlfunktion / Hardwaredefekt; "
        "<b>Difficult to Use (Gewicht 2)</b> = Ergonomische Hürde / Software-UX; "
        "<b>Wants (Gewicht 1)</b> = Fehlendes Kundenfeature / Feature-Request.",
        body_style
    ))

    # Severity Table
    sev_headers = [
        Paragraph("<b>Technology Domain</b>", th_style),
        Paragraph("<b>Defect (Failure)</b>", th_style),
        Paragraph("<b>Diff. to Use (UX)</b>", th_style),
        Paragraph("<b>Wants (Requests)</b>", th_style),
        Paragraph("<b>Avg. Severity Score</b>", th_style),
        Paragraph("<b>Dominant Friction Profile</b>", th_style)
    ]
    sev_rows = [
        [
            Paragraph("<b>Smart Cabin</b>", td_bold_style),
            Paragraph("74 (22,6 %)", td_center_style),
            Paragraph("168 (51,4 %)", td_center_style),
            Paragraph("85 (26,0 %)", td_center_style),
            Paragraph("<b>1,97</b>", td_center_style),
            Paragraph("Ergonomics & haptics (climate menu, seat firmness)", td_style)
        ],
        [
            Paragraph("<b>Smart Exterior</b>", td_bold_style),
            Paragraph("98 (30,3 %)", td_center_style),
            Paragraph("151 (46,8 %)", td_center_style),
            Paragraph("74 (22,9 %)", td_center_style),
            Paragraph("<b>2,07</b>", td_center_style),
            Paragraph("Actuators & sensors (kick sensor, motorized door)", td_style)
        ],
        [
            Paragraph("<b>Energy & Charging</b>", td_bold_style),
            Paragraph("52 (16,5 %)", td_center_style),
            Paragraph("174 (55,2 %)", td_center_style),
            Paragraph("89 (28,3 %)", td_center_style),
            Paragraph("<b>1,88</b>", td_center_style),
            Paragraph("Expectation gap (cold-weather range, charger preheat)", td_style)
        ],
        [
            Paragraph("<b>Digital Cockpit & AI</b>", td_bold_style),
            Paragraph("68 (23,0 %)", td_center_style),
            Paragraph("157 (53,0 %)", td_center_style),
            Paragraph("71 (24,0 %)", td_center_style),
            Paragraph("<b>1,99</b>", td_center_style),
            Paragraph("Software stability & nested menu depth (OS 8.5)", td_style)
        ],
        [
            Paragraph("<b>Vehicle Dynamics & Safety</b>", td_bold_style),
            Paragraph("41 (17,0 %)", td_center_style),
            Paragraph("143 (59,3 %)", td_center_style),
            Paragraph("57 (23,7 %)", td_center_style),
            Paragraph("<b>1,93</b>", td_center_style),
            Paragraph("Software calibration (recuperation, PHEV shift jerk)", td_style)
        ],
        [
            Paragraph("<b>Connected Ecosystem</b>", td_bold_style),
            Paragraph("42 (19,8 %)", td_center_style),
            Paragraph("121 (57,1 %)", td_center_style),
            Paragraph("49 (23,1 %)", td_center_style),
            Paragraph("<b>1,97</b>", td_center_style),
            Paragraph("Connectivity & timeouts (eSIM, My BMW App latency)", td_style)
        ],
        [
            Paragraph("<b>Driving Assistance</b>", td_bold_style),
            Paragraph("17 (11,0 %)", td_center_style),
            Paragraph("88 (57,1 %)", td_center_style),
            Paragraph("49 (31,9 %)", td_center_style),
            Paragraph("<b>1,79</b>", td_center_style),
            Paragraph("Lowest failure rate, primarily GSR2 chime warnings", td_style)
        ],
    ]

    t_sev = Table([sev_headers] + sev_rows, colWidths=[110, 80, 85, 80, 65, 112])
    t_sev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_DARK),
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
    story.append(t_sev)

    story.append(PageBreak())

    # ==========================================
    # PAGE 3: DEEP DIVES DOMAINS 1 - 4
    # ==========================================
    story.append(Paragraph("4. Deep Dive: Top 4 Technology Domains (Exhaustive Analysis)", h1_style))
    story.append(Paragraph(
        "Exhaustive analysis of the top 4 volume pain points featuring customer verbatim quotes and engineering root-cause diagnoses.",
        body_style
    ))

    # Deep Dive Cards (using clean ASCII tag headers)
    def make_deep_dive_box(dom_title, badge_txt, total_str, share_str, aspect_str, pain_points, verbatim_str, eng_action):
        box_data = [
            [
                Paragraph(f"<b>[{badge_txt}] {dom_title}</b>", ParagraphStyle('B1', parent=h2_style, textColor=C_ACCENT)),
                Paragraph(f"<b>Volume: {total_str} ({share_str})</b>", ParagraphStyle('B2', parent=td_bold_style, alignment=2, textColor=C_PRIMARY))
            ],
            [
                Paragraph(f"<b>Aspect Focus:</b> {aspect_str}", td_style),
                Paragraph("", td_style)
            ],
            [
                Paragraph(f"<b>Core Pain Points:</b><br/>{pain_points}", td_style),
                Paragraph(f"<b>Original Customer Voice (Verbatim):</b><br/><i>\"{verbatim_str}\"</i>", quote_style)
            ],
            [
                Paragraph(f"<b>Recommended Engineering Action:</b> {eng_action}", td_style),
                Paragraph("", td_style)
            ]
        ]
        t = Table(box_data, colWidths=[266, 266])
        t.setStyle(TableStyle([
            ('SPAN', (0,1), (1,1)),
            ('SPAN', (0,3), (1,3)),
            ('BACKGROUND', (0,0), (-1,-1), C_BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 1, C_BORDER),
            ('LINEBELOW', (0,0), (-1,0), 0.75, C_ACCENT),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    # 1. Energy & Charging
    t1 = make_deep_dive_box(
        "Energy & Charging", "1/7", "315 Cases", "16,65 %",
        "Charging experience, battery pre-conditioning & winter range forecasting",
        "• Real-world winter range vs. WLTP (97 cases; up to 35% cold-weather drop).<br/>"
        "• DC fast-charging curve degradation above 60% SoC (64 cases) & lack of pre-heating.<br/>"
        "• Charge flap mechanics & plug latch freezing in wet/frost conditions (22 cases).",
        "On the Autobahn in winter, the i5 range drops drastically. If you navigate to a fast-charger outside the native BMW nav, it charges at a ridiculous 60 kW because the battery is freezing cold.",
        "Implement manual battery pre-conditioning via a dedicated QuickSelect dock button and dynamic winter SoC buffer adjustments in navigation."
    )
    story.append(t1)
    story.append(Spacer(1, 7))

    # 2. Smart Exterior
    t2 = make_deep_dive_box(
        "Smart Exterior", "2/7", "323 Cases", "17,07 %",
        "Smart motorized doors, body actuators, kick sensors & aerodynamic wind noise",
        "• Motorized doors on i7 (22 cases): Ultrasonic sensors abort opening near curbs/pillars; manual override requires excessive force.<br/>"
        "• Hands-free tailgate kick sensor (24 cases): Low detection success rate in wet conditions.<br/>"
        "• Body gap alignment & flush door handles (60 cases): Winter freezing and A-pillar wind rush.",
        "The automatic doors of the i7 are almost unusable in tight German parking structures: they stop after 15 cm sensing a pillar and then require excessive force to push open manually.",
        "Recalibrate ultrasonic threshold algorithms for close-proximity obstacles and optimize electromechanical door-brake freewheel logic."
    )
    story.append(t2)
    story.append(Spacer(1, 7))

    # 3. Smart Cabin
    t3 = make_deep_dive_box(
        "Smart Cabin", "3/7", "327 Cases", "17,28 %",
        "Cabin ergonomics, Veganza synthetic leather, panoramic roof & acoustic insulation",
        "• Seats & upholstery (39 cases): Veganza perceived as less breathable than Merino leather; side bolsters pinch on long journeys.<br/>"
        "• Panoramic glass roof without mechanical shade (21 cases): Extreme greenhouse heating in summer.<br/>"
        "• Touchscreen climate controls & fan acoustic noise (32 cases): Hidden air vent adjustments.",
        "The new Veganza material in the 5 Series feels sweaty in summer. Furthermore, the panoramic glass roof lacks a physical sunblind, causing extreme in-cabin heat buildup.",
        "Enhance micro-perforation and seat ventilation intensity for Veganza upholstery; upgrade IR-reflective solar glazing coatings."
    )
    story.append(t3)
    story.append(Spacer(1, 7))

    # 4. Digital Cockpit & AI
    t4 = make_deep_dive_box(
        "Digital Cockpit & AI", "4/7", "296 Cases", "15,64 %",
        "BMW OS 8.5/9, QuickSelect interface, Theatre Screen & in-cabin audio playback",
        "• OS 8.5 menu depth (39 cases): Widgets obscure navigation map; climate adjustments require too many touchscreen taps.<br/>"
        "• Bowers & Wilkins sound system (28 cases): Occasional wireless Bluetooth audio latency.<br/>"
        "• Theatre Screen on i7: Folding mechanism deployment delay and FireTV streaming disconnects.",
        "Operating System 8.5 has overly nested menu layers. Adjusting seat heating or air recirculation while driving causes severe distraction.",
        "Introduce customizable, persistent climate docking bars on display borders and reduce voice assistant latency via quantized on-device LLMs."
    )
    story.append(t4)

    story.append(PageBreak())

    # ==========================================
    # PAGE 4: DOMAINS 5-7, PIPELINE GUIDE & ROADMAP
    # ==========================================
    story.append(Paragraph("5. Deep Dive: Domains 5 – 7 & Core BMW Brand Strengths", h1_style))

    # 5. Vehicle Dynamics & Safety
    t5 = make_deep_dive_box(
        "Vehicle Dynamics & Safety", "5/7", "241 Cases", "12,74 %",
        "Recuperation, brake blending & PHEV kickdown powertrain transitions",
        "• PHEV engine engagement (45 cases): Noticeable lag and drivetrain shudder during kickdown on 530e/750e.<br/>"
        "• B-mode one-pedal driving (19 cases): Adaptive recuperation brakes unexpectedly before roundabouts.<br/>"
        "• Contrast: Overall chassis and air suspension achieve benchmark rating of 9.95/10!",
        "The chassis of the i5 is exceptionally serene. But when adaptive recuperation is active, it sometimes decelerates unexpectedly hard when cars ahead enter turning lanes.",
        "Software smoothing of the torque transition during PHEV kickdown and enhanced driver haptic predictability in adaptive recuperation."
    )
    story.append(t5)
    story.append(Spacer(1, 6))

    # 6. Connected Ecosystem & Driving Assistance Compact
    t6_data = [
        [
            Paragraph("<b>[6/7] Connected Ecosystem (212 Cases | 11,21 %)</b><br/>"
                      "• <b>CarPlay / Android Auto (31):</b> WiFi-Verbindungsabbrüche.<br/>"
                      "• <b>Personal eSIM 5G (27):</b> Kompliziertes Carrier-Pairing.<br/>"
                      "• <b>My BMW App (24):</b> Timeout bei Fernklimatisierung in Tiefgaragen.<br/>"
                      "• <b>O-Ton:</b> <i>\"The My BMW App constantly reports 'Vehicle unreachable' when attempting to preheat cabin in winter.\"</i>", td_style),
            Paragraph("<b>[7/7] Driving Assistance (154 Cases | 8,14 % – Bester Bereich)</b><br/>"
                      "• <b>Höchste Zufriedenheit:</b> Highway Assistant (Hands-free L2+) top!<br/>"
                      "• <b>EU GSR2 Speed Limit Assistant (15):</b> Akustisches Gebimmel.<br/>"
                      "• <b>Parking Assistant Remote (21):</b> Abbruch bei Bordsteinkanten.<br/>"
                      "• <b>O-Ton:</b> <i>\"The Highway Assistant on the Autobahn is world-class. Only the EU speed limit warning chime is annoying.\"</i>", td_style)
        ]
    ]
    t6 = Table(t6_data, colWidths=[266, 266])
    t6.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t6)
    story.append(Spacer(1, 8))

    story.append(Paragraph("6. Data Pipeline Ingestion & Standardized CSV Artifacts", h1_style))
    story.append(Paragraph(
        "Für die nahtlose Weiterverarbeitung in Data Pipelines (Python Pandas, SQL Data Warehouses, NLP Sentiment Pipelines) "
        "wurden die Daten in standardisierten CSV-Dateien mit vollständiger Schema-Dokumentation exportiert:",
        body_style
    ))

    # Pipeline Artifacts Table
    pipe_headers = [
        Paragraph("<b>File / Artifact</b>", th_style),
        Paragraph("<b>Rows & Granularity</b>", th_style),
        Paragraph("<b>Primary Columns & Schema</b>", th_style),
        Paragraph("<b>Pipeline Application</b>", th_style)
    ]
    pipe_rows = [
        [
            Paragraph("<b>bmw_ev_technology_domain_records.csv</b>", td_bold_style),
            Paragraph("1,892 Rows<br/>(Record-Level)", td_style),
            Paragraph("feedback_id, brand, series, cohort, powertrain, technology_domain, aspect_cn, vfc_level2, customer_feedback_verbatim, severity_weight", td_style),
            Paragraph("Comprehensive dataset for NLP topic modeling, text mining, and machine learning pipelines.", td_style)
        ],
        [
            Paragraph("<b>bmw_ev_technology_domain_summary.csv</b>", td_bold_style),
            Paragraph("8 Rows<br/>(Domain-Level)", td_style),
            Paragraph("technology_domain, aspect_cn, total_complaints, overall_share_pct, bev_count, phev_count, defect_count, avg_severity, top_vfc_components", td_style),
            Paragraph("Direct ingestion into BI dashboards, management KPI tracking, and executive summaries.", td_style)
        ],
        [
            Paragraph("<b>bmw_ev_technology_domain_matrix.csv</b>", td_bold_style),
            Paragraph("9 Rows × 6 Cols<br/>(Cross-Tab)", td_style),
            Paragraph("technology_domain, 5er PHEV, 7er PHEV, i5 BEV, i7 BEV, Total, Share_Pct", td_style),
            Paragraph("Matrix for pivot analyses, heatmaps, and cohort comparisons in business intelligence tools.", td_style)
        ]
    ]
    t_pipe = Table([pipe_headers] + pipe_rows, colWidths=[130, 75, 175, 152])
    t_pipe.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_pipe)
    story.append(Spacer(1, 8))

    # Python Code Snippet Box
    code_text = (
        "<b>Downstream Pipeline Integration Snippet (Python Pandas):</b><br/>"
        "<font face='Courier' size=6.5 color='#0F172A'>"
        "import pandas as pd<br/>"
        "df = pd.read_csv('bmw_ev_technology_domain_records.csv')<br/>"
        "# Filter Top Severity Hardware Defects in Energy & Exterior<br/>"
        "crit = df[(df['technology_domain'].isin(['Energy & Charging', 'Smart Exterior'])) & (df['severity_weight'] == 3)]<br/>"
        "print(crit[['cohort', 'vfc_level2_component', 'customer_feedback_verbatim']].head())"
        "</font>"
    )
    t_code = Table([[Paragraph(code_text, callout_style)]], colWidths=[532])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_code)

    # Build document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully re-generated PDF: {pdf_path}")

    # Copy to artifacts directory
    artifact_pdf = "/Users/miao/.gemini/antigravity-ide/brain/50b3aecf-d9ce-4482-b37b-c634a4750503/BMW_EV_Technology_Domains_Analysis_Report.pdf"
    shutil.copy2(pdf_path, artifact_pdf)
    print(f"Copied to brain artifacts: {artifact_pdf}")

    # Render pages as PNGs using PyMuPDF
    doc_fitz = fitz.open(pdf_path)
    for p_idx in range(len(doc_fitz)):
        page = doc_fitz[p_idx]
        pix = page.get_pixmap(dpi=150)
        png_out = f"/Users/miao/.gemini/antigravity-ide/brain/50b3aecf-d9ce-4482-b37b-c634a4750503/domain_report_page_{p_idx+1}.png"
        pix.save(png_out)
        print(f"Saved page preview: {png_out}")

build_pdf()
