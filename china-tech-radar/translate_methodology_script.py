with open("generate_methodology_pdf.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace footer
text = text.replace('f"Seite {self._pageNumber} von {total_pages}"', 'f"Page {self._pageNumber} of {total_pages}"')

# Subtitle and titles
text = text.replace(
    'Paragraph("Mathematische Modellierung, Herleitung von \'Likes\' vs. \'Friction\', Net-Sentiment-Berechnung & Schweregrad-Gewichtung", subtitle_style)',
    'Paragraph("Mathematical Modeling, Derivation of Likes vs. Friction, Net Sentiment Formulation & Severity Weighting", subtitle_style)'
)

# KPI banner
text = text.replace("Analysierter Datenpool", "Total Analyzed Records")
text = text.replace("3.971 Einträge", "3,971 Records")
text = text.replace("16 Modelle (100% ICE Excluded)", "16 Models (100% ICE Excluded)")
text = text.replace("Positive Lobstimmen (Likes)", "Positive Praise (Likes)")
text = text.replace("1.491 Fälle", "1,491 Cases")
text = text.replace("Promoter Voice / Begeisterung", "Promoter Voice / Excitement")
text = text.replace("Beanstandungen (Friction)", "Customer Friction")
text = text.replace("1.892 Fälle", "1,892 Cases")
text = text.replace("Defect + Diff. to Use + Wants", "Defect + Diff. to Use + Wants")
text = text.replace("Evaluierte Datenbasis", "Evaluated Universe")
text = text.replace("3.383 Fälle", "3,383 Cases")
text = text.replace("Likes + Reale Schmerzpunkte", "Likes + Real Pain Points")

# Section 1
text = text.replace("1. Datenherkunft: Wie wurden 'Likes' und 'Friction' ermittelt?", "1. Data Provenance: How 'Likes' and 'Friction' Were Derived")
text = text.replace(
    'Die Rohdaten entstammen den offiziellen BMW-Kundenstudien der aktuellen Modellgenerationen (<code>G60_feedback_hackathon.xlsx</code> und <code>G70_feedback_hackathon.xlsx</code>). Um strikte Datenintegrität zu gewährleisten, wurden alle reinen Verbrenner (ICE) und der 1er (F70) herausgefiltert. In der verifizierten Schnittmenge von <b>16 elektrifizierten BMW Modellen</b> (i5 BEV, i7 BEV, 5er PHEV, 7er PHEV) ist jeder Datensatz in der Spalte <code>Feedback Type</code> exakt einer von vier Kategorien zugeordnet:',
    'Raw feedback was sourced from official BMW customer studies of current generation models (<code>G60_feedback_hackathon.xlsx</code> and <code>G70_feedback_hackathon.xlsx</code>). To guarantee strict data integrity, all pure internal combustion (ICE) derivates and the 1 Series (F70) were eliminated. Within the verified universe of <b>16 electrified BMW models</b> (i5 BEV, i7 BEV, 5 Series PHEV, 7 Series PHEV), every record in column <code>Feedback Type</code> maps strictly into one of four categories:'
)

# Category Table headers
text = text.replace("<b>Kategorie (Feedback Type)</b>", "<b>Category (Feedback Type)</b>")
text = text.replace("<b>Anzahl Fälle</b>", "<b>Volume</b>")
text = text.replace("<b>Methodische Definition in der Automotive Pipeline</b>", "<b>Methodological Definition in Automotive Pipeline</b>")
text = text.replace("<b>Klassifikation</b>", "<b>Classification</b>")

# Category Rows
text = text.replace(
    "Explizites Kundenlob, Begeisterung über Fahreigenschaften, Design oder Akustikkomfort. Fungiert als <b>Promoter-Signal</b>.",
    "Explicit customer praise, admiration for driving dynamics, design, or acoustic comfort. Functions as a <b>Promoter Signal</b>."
)
text = text.replace(
    "Ergonomische Hürden, verschachtelte Menüs, unklare Bedienlogik oder überempfindliche Sensorik. System ist funktionstüchtig, frustriert aber den Fahrer.",
    "Ergonomic hurdles, deeply nested menus, unintuitive logic, or oversensitive sensors. System functions but frustrates the driver."
)
text = text.replace("UX Friction (Gewicht 2)", "UX Friction (Weight 2)")
text = text.replace(
    "Echte Hardware-Ausfälle, Systemabstürze, vereiste Ladeklappen oder blockierende Automatiktüren.",
    "Real hardware component failures, system crashes, frozen charging flaps, or jammed automated doors."
)
text = text.replace("Hard Malfunction (Gewicht 3)", "Hard Malfunction (Weight 3)")
text = text.replace(
    "Unerfüllte Kundenbedürfnisse, fehlende Ausstattungen (z. B. Öffnungsfunktion für Glasdach) oder gewünschte Software-Features.",
    "Unmet customer needs, missing equipment (e.g. panoramic roof tilt/slide function) or requested software features."
)
text = text.replace("Feature Gap (Gewicht 1)", "Feature Gap (Weight 1)")

# Formulas Section 2
text = text.replace("2. Mathematische Formeln: Net Sentiment & Severity Score", "2. Mathematical Formulations: Net Sentiment & Severity Score")
text = text.replace("A. Net Sentiment Score (Analog zu Net Promoter Score / NPS Logik):", "A. Net Sentiment Score (Formulated Analogously to Net Promoter Score / NPS):")
text = text.replace("• <b>Skala:</b> Reicht von <b>+100 %</b> (reines Kundenlob) bis <b>-100 %</b> (reine Beanstandung).", "• <b>Scale:</b> Ranges from <b>+100%</b> (pure customer praise) to <b>-100%</b> (pure complaint friction).")
text = text.replace("• <b>Interpretation:</b> Ein Wert über <b>0 %</b> signalisiert Netto-Zufriedenheit. Negative Werte zeigen, dass der Schmerz die Begeisterung überwiegt.", "• <b>Interpretation:</b> Values above <b>0%</b> represent net positive advocacy. Negative values denote that friction outweighs praise.")
text = text.replace("B. Gewichteter Schweregrad (Average Severity Score):", "B. Weighted Severity Score (Average Severity Score):")
text = text.replace("• <b>Skala:</b> Reicht von <b>1,00</b> (reine Wünsche) bis <b>3,00</b> (reine Hard-Defects).", "• <b>Scale:</b> Ranges from <b>1.00</b> (pure feature requests) to <b>3.00</b> (hard hardware defects).")
text = text.replace("• <b>Prioritäts-Index (Backlog Prio):</b>", "• <b>Priority Backlog Index (Action Leverage):</b>")

# Section 3
text = text.replace("3. Vollständiges Domänen-Ranking (Sortiert nach Net Sentiment)", "3. Comprehensive Technology Domain Ranking (Ranked by Net Sentiment)")
text = text.replace(
    "Die folgende Tabelle zeigt das offizielle Ranking aller 7 Technologie-Domänen (plus Übergreifend). Der Net Sentiment Score trennt klar zwischen echten Wettbewerbsvorteilen von BMW und massiven Handlungsfeldern.",
    "The table below details the official ranking of all 7 technology domains (plus General/Services). The Net Sentiment Score rigorously isolates BMW's competitive brand moats from severe architectural friction areas."
)

# Ranking Table Headers
text = text.replace("<b>Rang & Domäne</b>", "<b>Rank & Domain</b>")
text = text.replace("<b>Beobachtungsfokus (Aspect)</b>", "<b>Aspect Focus</b>")
text = text.replace("<b>Lob<br/>(Likes)</b>", "<b>Praise<br/>(Likes)</b>")
text = text.replace("<b>Kritik<br/>(Friction)</b>", "<b>Friction<br/>(Complaints)</b>")
text = text.replace("<b>Evaluierte<br/>Basis</b>", "<b>Evaluated<br/>Universe</b>")
text = text.replace("<b>Net Sentiment<br/>Score</b>", "<b>Net Sentiment<br/>Score</b>")
text = text.replace("<b>Ø Severity<br/>(1–3)</b>", "<b>Avg. Severity<br/>(1–3)</b>")
text = text.replace("<b>Status & Handlung</b>", "<b>Status & Engineering Takeaway</b>")

# Ranking rows text
text = text.replace("Antriebsregelung, Fahrwerk, Bremsen", "Drivetrain control, chassis, active brakes")
text = text.replace("<font color='#059669'><b>Brand Moat</b></font>: Weltklasse-Fahrwerk schlägt Kritik.", "<font color='#059669'><b>Brand Moat</b></font>: Benchmark chassis beats friction.")
text = text.replace("Thermalkomfort, Sitze, Akustik, Raum", "Thermal comfort, seating, acoustics, space")
text = text.replace("<font color='#D97706'><b>Durchwachsen</b></font>: Akustik top, Veganza schwitzig.", "<font color='#D97706'><b>Mixed</b></font>: Acoustics top; Veganza leather sweaty.")
text = text.replace("Smarte Karosserie, Türen, Licht, Aero", "Smart bodywork, doors, lighting, aero")
text = text.replace("<font color='#D97706'><b>Hardware top</b></font>, aber Türsensorik frustriert.", "<font color='#D97706'><b>Hardware top</b></font>, but door sensors frustrate.")
text = text.replace("Display-HMI, Sprachassistent, Entertainment", "Display HMI, voice assistant, entertainment")
text = text.replace("<font color='#DC2626'><b>Problemzone</b></font>: Höchster Schweregrad (OS 8.5 Menüs).", "<font color='#DC2626'><b>Critical Area</b></font>: Highest severity (OS 8.5 menus).")
text = text.replace("Highway/City Pilot, Parken, Handoff", "Highway/City pilot, automated parking, handoff")
text = text.replace("<font color='#DC2626'><b>GSR2-Kritik</b></font>: Highway Assist top, Tempolimit nervt.", "<font color='#DC2626'><b>GSR2 Friction</b></font>: Highway Assist top; speed bongs annoy.")
text = text.replace("Ladeerlebnis, Vorkonditionierung, Reichweite", "Charging UX, preconditioning, winter range")
text = text.replace("<font color='#DC2626'><b>Kaltlade-Falle</b></font>: Reale Winterreichweite enttäuscht.", "<font color='#DC2626'><b>Cold Charge Trap</b></font>: Winter range drops disappoint.")
text = text.replace("Bordbuch, Händlerübergabe & Service", "Owner's manual, dealership delivery & service")
text = text.replace("Geringes Volumen; primär digitale Bordanleitung.", "Low volume; primarily digital onboard manual.")
text = text.replace("Smartphone-App, Remote-Services, OTA", "Smartphone app, remote services, OTA upgrades")
text = text.replace("<font color='#DC2626'><b>Krisenpunkt</b></font>: Tiefgaragen-Timeouts, CarPlay.", "<font color='#DC2626'><b>Crisis Point</b></font>: Garage connection timeouts, CarPlay drops.")

text = text.replace("<b>Gesamtsumme / Durchschnitt</b>", "<b>Total Universe / Weighted Average</b>")
text = text.replace("<b>Alle 16 elektrifizierten BMW-Modelle</b>", "<b>All 16 Electrified BMW Models</b>")
text = text.replace("<b>Verifizierte Datenbasis (100% ICE bereinigt)</b>", "<b>Verified Baseline (100% ICE Excluded)</b>")

# Section 4
text = text.replace("4. Fazit & Technische Implikationen für die Entwicklungs-Roadmap", "4. Strategic Synthesis & Engineering Roadmap Implications")
text = text.replace(
    '<b>1. Mechanische Exzellenz vs. Digitale Reife:</b><br/>BMW erzielt im Fahrwerk (<i>Vehicle Dynamics</i>) mit <b>+44,7 % Net Sentiment</b> eine überragende Dominanz. Kein chinesischer oder europäischer Wettbewerber erreicht diesen Komfort. Demgegenüber steht <i>Connected Ecosystem</i> mit <b>-76,7 %</b> – hier erwarten Premiumkunden sofortige Cloud-Reaktion ohne Timeouts.',
    '<b>1. Mechanical Excellence vs. Digital Maturity:</b><br/>BMW establishes undisputed dominance in chassis dynamics (<i>Vehicle Dynamics</i>) with <b>+44.7% Net Sentiment</b>. No Chinese or Western competitor matches this level of ride refinement. Conversely, <i>Connected Ecosystem</i> registers <b>-76.7%</b> – luxury EV owners demand instant, zero-timeout cloud execution.'
)
text = text.replace(
    '<b>2. Der \'Difficult to Use\'-Faktor (UX vor Hardware):</b><br/>Über <b>53 % aller Beanstandungen</b> sind keine Hardwaredefekte, sondern UX-Reibungspunkte. Die teuerste Erkenntnis: Das Über-Engineering von mechatronischen Automatiktüren und Touch-Klimamenüs erzeugt mehr Unzufriedenheit als schlichte physische Lösungen.',
    '<b>2. The \'Difficult to Use\' Factor (UX Over Hardware Defect):</b><br/>Over <b>53% of all customer complaints</b> are not broken hardware, but UX friction points. Crucial takeaway: Over-engineering motorized automated doors and nested touchscreen climate menus generates greater frustration than tactile physical solutions.'
)

with open("generate_methodology_pdf.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated generate_methodology_pdf.py successfully!")
