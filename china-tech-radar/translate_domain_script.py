with open("generate_domain_pdf_report.py", "r", encoding="utf-8") as f:
    text = f.read()

# Header & Footer
text = text.replace('f"Seite {self._pageNumber} von {total_pages}"', 'f"Page {self._pageNumber} of {total_pages}"')

# Subtitle
text = text.replace(
    'Paragraph("Systematische Auswertung der 1.892 elektrifizierten Kundenbeanstandungen nach 7 Technologie-Domänen (i5 BEV, i7 BEV, 5er PHEV, 7er PHEV)", subtitle_style)',
    'Paragraph("Systematic evaluation of 1,892 electrified customer complaints across 7 technology domains (i5 BEV, i7 BEV, 5 Series PHEV, 7 Series PHEV)", subtitle_style)'
)

# KPI Banner
text = text.replace("Elektrifizierte Kohorten", "Electrified Cohorts")
text = text.replace("4 Modellgruppen", "4 Model Groups")
text = text.replace("Feedback Pool Gesamt", "Total Feedback Pool")
text = text.replace("3.971 Datensätze", "3,971 Records")
text = text.replace("100% ICE Modelle ausgeschlossen", "100% ICE Models Excluded")
text = text.replace("Verifizierte Beanstandungen", "Verified Complaints")
text = text.replace("1.892 Fälle", "1,892 Cases")
text = text.replace("Technologie-Domänen", "Technology Domains")
text = text.replace("7 Kern-Domänen", "7 Core Domains")
text = text.replace("Industriestandard NEV / SDV", "NEV / SDV Industry Standard")

# Section 1
text = text.replace("1. Plausibilitäts- und Architekturprüfung der 7 Technologie-Kategorien", "1. Architectural Validation & Plausibility Audit of the 7 Technology Domains")
text = text.replace(
    'Die vorgegebene 7-gliedrige Technologie-Taxonomie wurde gegen etablierte Benchmark-Standards (Dongchedi, CPCA NEV Index, McKinsey Connected Car Architecture, ISO 26262 / SAE J3016) geprüft. <b>Ergebnis: Die Taxonomie ist methodisch vollständig valide, trennscharf und MECE</b> (Mutually Exclusive, Collectively Exhaustive). Die Ergänzung um <i>Smart Exterior</i> schließt die entscheidende Lücke moderner mechatronischer Karosserieaktoren.',
    'The proposed 7-pillar technology taxonomy was benchmarked against leading automotive industry standards (Dongchedi, CPCA NEV Index, McKinsey Connected Vehicle Architecture, ISO 26262 / SAE J3016). <b>Result: The taxonomy is methodologically valid, sharply delineated, and strictly MECE</b> (Mutually Exclusive, Collectively Exhaustive). Incorporating <i>Smart Exterior</i> closes the critical gap of modern mechatronic exterior body actuators.'
)

# Taxonomy Table Headers
text = text.replace("<b>Technologie-Domäne</b>", "<b>Technology Domain</b>")
text = text.replace("<b>Beobachtungsfokus (Aspect)</b>", "<b>Aspect Focus</b>")
text = text.replace("<b>Feature-Scope & Beispiele</b>", "<b>Feature Scope & Examples</b>")
text = text.replace("<b>Methodische Bewertung</b>", "<b>Methodological Assessment</b>")

# Taxonomy Rows Assessment
text = text.replace("Ladeerlebnis, Vorkonditionierung, Reichweitenmanagement & V2X", "Charging UX, thermal pre-conditioning, range management & V2X")
text = text.replace("Laderoutenplanung, Vorkonditionierung (Pre-heating), DC-Ladekurve, Plug&Charge, V2L", "Charging route planning, battery pre-heating, DC fast-charging curve, Plug&Charge, V2L")
text = text.replace("<font color='#059669'><b>Valide:</b></font> Isoliert Kernschmerzpunkte reiner E-Mobilität.", "<font color='#059669'><b>Valid:</b></font> Isolates core friction points of pure EV ownership.")

text = text.replace("Highway/City Pilot, Parken, Handoff & GSR2-Sicherheit", "Highway/City pilot, automated parking, handoff & GSR2 compliance")
text = text.replace("Highway Assistant (L2+ Hands-free), Parking Assistant Pro, Tempolimit-Assistent, Handoff", "Highway Assistant (L2+ hands-free), Parking Assistant Pro, speed limit alerts, handoff")
text = text.replace("<font color='#059669'><b>Valide:</b></font> Standard-Domäne für ADAS/AD-Sensorik & Aktorik.", "<font color='#059669'><b>Valid:</b></font> Industry standard for ADAS/AD perception and actuation.")

text = text.replace("Display-HMI, Sprachassistent & Entertainment", "Display HMI, voice assistant & in-cabin entertainment")
text = text.replace("Curved Display, QuickSelect OS 8.5, Theatre Screen (i7), NLU-Sprachbedienung (IPA), B&W Audio", "Curved Display, QuickSelect OS 8.5/9, Theatre Screen (i7), NLU voice assistant (IPA), B&W sound")
text = text.replace("<font color='#059669'><b>Valide:</b></font> Bordnetz-In-Cabin HMI, Compute & Multimodalität.", "<font color='#059669'><b>Valid:</b></font> In-cabin HMI, compute, and multimodal user interaction.")

text = text.replace("Smartphone-Integration, Remote-Services & OTA", "Smartphone integration, remote telematics & OTA services")
text = text.replace("My BMW App, Digital Key Plus (UWB), Remote Software Upgrade (OTA), Personal eSIM 5G", "My BMW App, Digital Key Plus (UWB), Remote Software Upgrade (OTA), Personal eSIM 5G")
text = text.replace("<font color='#059669'><b>Valide:</b></font> Trennt Onboard-Systeme von Cloud-/App-Diensten.", "<font color='#059669'><b>Valid:</b></font> Delineates onboard vehicle systems from cloud/mobile services.")

text = text.replace("Thermalkomfort, Sitze, Akustik, Luft & Ergonomie", "Thermal comfort, seating, acoustics, air quality & ergonomics")
text = text.replace("Veganza-/Merino-Sitze, 4-Zonen-Klima, Akustikverglasung, Mittelkonsole, Panoramadach", "Veganza/Merino seating, 4-zone climate, acoustic glass, center console, panoramic roof")
text = text.replace("<font color='#059669'><b>Valide:</b></font> Physisch-mikroklimatischer Komfort (Hardware/Haptik).", "<font color='#059669'><b>Valid:</b></font> Physical micro-climate comfort (hardware, haptics, materials).")

text = text.replace("Antriebsregelung, Fahrwerk, Bremsen & Insassenschutz", "Drivetrain control, chassis, active braking & occupant safety")
text = text.replace("Rekuperation (B-Modus), 2-Achs-Luftfederung, Integral-Aktivlenkung, Brems-Blending, CPD", "Recuperation (B-mode), 2-axle air suspension, Integral Active Steering, brake blending, CPD")
text = text.replace("<font color='#059669'><b>Valide:</b></font> BMW-Kernkompetenz: Längs-/Querdynamik & passive Sicherheit.", "<font color='#059669'><b>Valid:</b></font> BMW core brand competency: longitudinal/lateral dynamics & safety.")

text = text.replace("Smarte Karosserie, Automatiktüren, Licht & Aero", "Smart bodywork, motorized doors, active lighting & aerodynamics")
text = text.replace("Automatische Türen (i7), berührungslose Heckklappe (Kick-Sensor), bündige Griffe, Matrix-LED", "Motorized doors (i7), hands-free tailgate kick sensor, flush handles, Matrix LED")
text = text.replace("<font color='#059669'><b>Valide:</b></font> Unverzichtbar für Luxusklasse-Aktorik & smarte Karosserie.", "<font color='#059669'><b>Valid:</b></font> Indispensable for modern luxury-tier exterior mechatronics.")

# Callout page 1
text = text.replace("Taxonomische Grenzregeln für automatisierte Ingest-Pipelines:", "Taxonomic Boundary Rules for Automated Ingestion Pipelines:")
text = text.replace("• <b>Voice Assistant & NLU:</b> Fest in <i>Digital Cockpit & AI</i> verortet (multimodale Interaktionsebene).", "• <b>Voice Assistant & NLU:</b> Strictly allocated to <i>Digital Cockpit & AI</i> (multimodal interaction layer).")
text = text.replace("• <b>Sitzklima vs. Infotainment:</b> Physische Belüftung/Heizung in <i>Smart Cabin</i>; die Bildschirmsteuerung in <i>Digital Cockpit & AI</i>.", "• <b>Seat Climate vs. Infotainment:</b> Physical heating/ventilation in <i>Smart Cabin</i>; touchscreen controls in <i>Digital Cockpit & AI</i>.")
text = text.replace("• <b>Connected Services:</b> Alle smartphone-gestützten Features (Digital Key, My BMW App, OTA) strikt in <i>Connected Ecosystem</i>.", "• <b>Connected Services:</b> All smartphone-enabled features (Digital Key, My BMW App, OTA) strictly in <i>Connected Ecosystem</i>.")

# Section 2 (Page 2)
text = text.replace("2. Quantitatives Domänen-Ranking & Kohorten-Matrix", "2. Quantitative Domain Ranking & Cohort Distribution Matrix")
text = text.replace(
    "Verteilung aller 1.892 validierten Kundenbeanstandungen über die 4 elektrifizierten BMW-Modellkohorten. Alle Datenpunkte stammen aus der verifizierten Schnittmenge von G60 (5er/i5) und G70 (7er/i7), bereinigt um Verbrennerdaten.",
    "Distribution of all 1,892 verified customer complaints across the 4 electrified BMW model cohorts. All data points derive from the verified intersection of G60 (5 Series/i5) and G70 (7 Series/i7), strictly cleaned of combustion engine entries."
)

text = text.replace("<b>Technologie-Domäne</b>", "<b>Technology Domain</b>")
text = text.replace("<b>5er PHEV<br/>(G60)</b>", "<b>5 Series PHEV<br/>(G60)</b>")
text = text.replace("<b>7er PHEV<br/>(G70)</b>", "<b>7 Series PHEV<br/>(G70)</b>")
text = text.replace("<b>Gesamt<br/>Fälle</b>", "<b>Total<br/>Cases</b>")
text = text.replace("<b>Anteil<br/>%</b>", "<b>Share<br/>%</b>")
text = text.replace("<b>Primäre Problemkomponente</b>", "<b>Primary Problem Components</b>")

text = text.replace("Sitze & Polsterung (39); Dach (21); Klima (17)", "Seats & upholstery (39); Sunroof (21); Climate (17)")
text = text.replace("Spaltmaße/Karosserie (60); Kick-Sensor (24); Türen (22)", "Body gaps/seals (60); Kick sensor (24); Doors (22)")
text = text.replace("Reale Reichweite (97); DC-Laden (64); HV-Batterie (43)", "Winter real range (97); DC fast-charging (64); HV battery (43)")
text = text.replace("Infotainment OS 8.5 (39); B&W Audio (28); Navi (26)", "Infotainment OS 8.5 (39); B&W Audio (28); Nav (26)")
text = text.replace("PHEV-Übergang/Kickdown (45); My Modes (29); Rekuperation (19)", "PHEV kickdown transition (45); My Modes (29); Recuperation (19)")
text = text.replace("CarPlay (31); Personal eSIM (27); My BMW App (24)", "CarPlay (31); Personal eSIM (27); My BMW App (24)")
text = text.replace("Parking Assistant (21); Highway Assist (15); GSR2-Limit (15)", "Parking Assistant (21); Highway Assist (15); GSR2 speed warnings (15)")
text = text.replace("Allgemeine Feedbackanfragen (15); Bordbuch (9)", "General inquiries (15); Digital manual (9)")

text = text.replace("<b>Gesamtsumme</b>", "<b>Total Universe</b>")
text = text.replace("<b>Volle verifizierte Datenbasis</b>", "<b>Full Verified Baseline</b>")

# Section 3 (Severity on Page 2)
text = text.replace("3. Fehlerkategorie & Schweregrad-Verteilung (Pipeline Metric Layer)", "3. Failure Category & Severity Distribution (Pipeline Metric Layer)")
text = text.replace(
    'Für die Weiterverarbeitung in Data Pipelines werden Beanstandungen nach Feedback-Typ und Gewichtung segmentiert: <b>Defect (Gewicht 3)</b> = Technische Fehlfunktion / Hardwaredefekt; <b>Difficult to Use (Gewicht 2)</b> = Ergonomische Hürde / Software-UX; <b>Wants (Gewicht 1)</b> = Fehlendes Kundenfeature / Feature-Request.',
    'For automated data ingestion pipelines, feedback records are segmented by feedback type and severity weighting: <b>Defect (Weight 3)</b> = Component failure / hardware breakdown; <b>Difficult to Use (Weight 2)</b> = Ergonomic hurdle / software UX; <b>Wants (Weight 1)</b> = Missing customer feature request.'
)

text = text.replace("<b>Defect (Fehler)</b>", "<b>Defect (Failure)</b>")
text = text.replace("<b>Diff. to Use (UX)</b>", "<b>Diff. to Use (UX)</b>")
text = text.replace("<b>Wants (Wünsche)</b>", "<b>Wants (Requests)</b>")
text = text.replace("<b>Ø Severity Score</b>", "<b>Avg. Severity Score</b>")
text = text.replace("<b>Dominanter Problemtyp</b>", "<b>Dominant Friction Profile</b>")

text = text.replace("Bedienung & Haptik (Klimamenü, Sitzhärte)", "Ergonomics & haptics (climate menu, seat firmness)")
text = text.replace("Aktorik & Sensorik (Kick-Sensor, Autotür)", "Actuators & sensors (kick sensor, motorized door)")
text = text.replace("Erwartungsdiskrepanz (Reichweite, Ladesäulen)", "Expectation gap (cold-weather range, charger preheat)")
text = text.replace("Software-Stabilität & Menütiefe (OS 8.5)", "Software stability & nested menu depth (OS 8.5)")
text = text.replace("Feinabstimmung Software (Rekuperation, Lastwechsel)", "Software calibration (recuperation, PHEV shift jerk)")
text = text.replace("Verbindung & Konnektivität (eSIM, App-Timeout)", "Connectivity & timeouts (eSIM, My BMW App latency)")
text = text.replace("Geringste Fehlerrate, primär GSR2-Warnungen", "Lowest failure rate, primarily GSR2 chime warnings")

# Page 3 Deep Dives
text = text.replace("4. Deep Dive: Top 4 Technologie-Domänen (Detailanalyse)", "4. Deep Dive: Top 4 Technology Domains (Exhaustive Analysis)")
text = text.replace(
    "Detaillierte Analyse der vier volumenstärksten Schmerzpunkte mit Kunden-O-Tönen und technischer Ursachenforschung.",
    "Exhaustive analysis of the top 4 volume pain points featuring customer verbatim quotes and engineering root-cause diagnoses."
)

text = text.replace("<b>Beobachtungsfokus:</b>", "<b>Aspect Focus:</b>")
text = text.replace("<b>Haupt-Pain-Points:</b>", "<b>Core Pain Points:</b>")
text = text.replace("<b>Original Kundenstimme (Verbatim):</b>", "<b>Original Customer Voice (Verbatim):</b>")
text = text.replace("<b>Technische Handlungsempfehlung (Engineering Pipeline):</b>", "<b>Recommended Engineering Action:</b>")

text = text.replace("315 Fälle", "315 Cases")
text = text.replace("323 Fälle", "323 Cases")
text = text.replace("327 Fälle", "327 Cases")
text = text.replace("296 Fälle", "296 Cases")
text = text.replace("241 Fälle", "241 Cases")
text = text.replace("212 Fälle", "212 Cases")
text = text.replace("154 Fälle", "154 Cases")

# Deep dive verbatims and actions
text = text.replace(
    "Auf der Autobahn im Winter bricht die Reichweite des i5 massiv ein. Wenn man eine Schnellladesäule nicht direkt über das BMW-Navi ansteuert, lädt er mit lächerlichen 60 kW, weil der Akku eiskalt ist.",
    "On the Autobahn in winter, the i5 range drops drastically. If you navigate to a fast-charger outside the native BMW nav, it charges at a ridiculous 60 kW because the battery is freezing cold."
)
text = text.replace(
    "Implementierung von manueller Batterie-Vorkonditionierung per QuickSelect-Button und dynamischer Winter-SoC-Pufferberechnung in der Bordsoftware.",
    "Implement manual battery pre-conditioning via a dedicated QuickSelect dock button and dynamic winter SoC buffer adjustments in navigation."
)

text = text.replace(
    "Die automatischen Türen des i7 sind in engen deutschen Parkhäusern fast unbrauchbar: Sie stoppen nach 15 cm wegen einer Wand und lassen sich dann von Hand nur mit großem Kraftaufwand aufdrücken.",
    "The automatic doors of the i7 are almost unusable in tight German parking structures: they stop after 15 cm sensing a pillar and then require excessive force to push open manually."
)
text = text.replace(
    "Kalibrierung der Ultraschall-Schwellenwerte für Nahfeld-Hindernisse und Optimierung der elektromechanischen Türbremsen-Freilauflogik.",
    "Recalibrate ultrasonic threshold algorithms for close-proximity obstacles and optimize electromechanical door-brake freewheel logic."
)

text = text.replace(
    "Das neue Veganza-Material im 5er fühlt sich im Sommer schwitzig an. Außerdem fehlt beim Panoramadach ein echtes Sonnenrollo – der Innenraum heizt extrem auf.",
    "The new Veganza material in the 5 Series feels sweaty in summer. Furthermore, the panoramic glass roof lacks a physical sunblind, causing extreme in-cabin heat buildup."
)
text = text.replace(
    "Verbesserung der Perforation und Lüftungsintensität bei Veganza-Ausstattung; Optimierung der automatischen Sonnenschutz-Verglasungsbeschichtung.",
    "Enhance micro-perforation and seat ventilation intensity for Veganza upholstery; upgrade IR-reflective solar glazing coatings."
)

text = text.replace(
    "Das Betriebssystem 8.5 hat zu viele verschachtelte Menüs. Während der Fahrt die Sitzheizung oder Umluft einzuschalten, lenkt massiv vom Verkehr ab.",
    "Operating System 8.5 has overly nested menu layers. Adjusting seat heating or air recirculation while driving causes severe distraction."
)
text = text.replace(
    "Einführung von anpassbaren persistenten Klimaleisten im Display und Latenzreduktion des Intelligent Personal Assistant (IPA) via Onboard-LLM.",
    "Introduce customizable, persistent climate docking bars on display borders and reduce voice assistant latency via quantized on-device LLMs."
)

# Page 4 Deep dives
text = text.replace("5. Deep Dive: Domänen 5 – 7 & BMW Kernstärken", "5. Deep Dive: Domains 5 – 7 & Core BMW Brand Strengths")
text = text.replace(
    "Das Fahrwerk des i5 ist überragend ruhig. Aber wenn der adaptive Rekuperationsmodus aktiv ist, bremst er manchmal unerwartet stark ab, wenn vorausfahrende Autos abbiegen.",
    "The chassis of the i5 is exceptionally serene. But when adaptive recuperation is active, it sometimes decelerates unexpectedly hard when cars ahead enter turning lanes."
)
text = text.replace(
    "Software-Glättung der Drehmoment-Übergabe bei PHEV-Kickdown und präzisere Fahrer-Rückmeldung im adaptiven Rekuperationsmodus.",
    "Software smoothing of the torque transition during PHEV kickdown and enhanced driver haptic predictability in adaptive recuperation."
)

text = text.replace(
    "Die My BMW App meldet ständig 'Fahrzeug nicht erreichbar', wenn man im Winter vorheizen will.",
    "The My BMW App constantly reports 'Vehicle unreachable' when attempting to preheat cabin in winter."
)
text = text.replace(
    "Der Highway Assistant auf der Autobahn ist absolute Weltklasse. Nur der EU-Tempolimitwarner nervt.",
    "The Highway Assistant on the Autobahn is world-class. Only the EU speed limit warning chime is annoying."
)

# Pipeline artifacts table
text = text.replace("6. Datenpipeline-Integration & Bereitstellung der CSV-Dateien", "6. Data Pipeline Ingestion & Standardized CSV Artifacts")
text = text.replace(
    "Für die nahtlose Weiterverarbeitung in Data Pipelines (Python Pandas, SQL Data Warehouses, NLP Sentiment Pipelines) wurden die Daten in standardisierten CSV-Dateien mit vollständiger Schema-Dokumentation exportiert:",
    "For automated downstream processing across data pipelines (Python Pandas, SQL Data Warehouses, NLP Sentiment Pipelines), datasets have been exported into standardized CSV artifacts:"
)

text = text.replace("<b>Datei / Artefakt</b>", "<b>File / Artifact</b>")
text = text.replace("<b>Zeilen & Granularität</b>", "<b>Rows & Granularity</b>")
text = text.replace("<b>Wichtigste Spalten & Typen</b>", "<b>Primary Columns & Schema</b>")
text = text.replace("<b>Verwendungszweck in der Pipeline</b>", "<b>Pipeline Application</b>")

text = text.replace("1.892 Zeilen<br/>(Record-Level)", "1,892 Rows<br/>(Record-Level)")
text = text.replace("8 Zeilen<br/>(Domain-Level)", "8 Rows<br/>(Domain-Level)")
text = text.replace("9 Zeilen × 6 Spalten<br/>(Kreuztabelle)", "9 Rows × 6 Cols<br/>(Cross-Tab)")

text = text.replace("Vollständiger Datensatz für NLP-Topic Modeling, Text Mining und maschinelles Lernen.", "Comprehensive dataset for NLP topic modeling, text mining, and machine learning pipelines.")
text = text.replace("Direkte Einspeisung in BI-Dashboards, Management-KPIs und Executive Summaries.", "Direct ingestion into BI dashboards, management KPI tracking, and executive summaries.")
text = text.replace("Matrix für Pivot-Analysen, Heatmaps und Kohorten-Vergleiche in Reporting-Tools.", "Matrix for pivot analyses, heatmaps, and cohort comparisons in business intelligence tools.")

with open("generate_domain_pdf_report.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated generate_domain_pdf_report.py successfully!")
