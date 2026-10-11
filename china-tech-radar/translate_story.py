import re

with open('bmw_pipeline_story.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace <html lang="de"> with <html lang="en">
c = c.replace('<html lang="de">', '<html lang="en">', 1)

# Navigation
c = c.replace('Zurück zum Interaktiven Fahrzeugkatalog', 'Back to Interactive Vehicle Explorer')
c = c.replace('📄 Tech Domains Report (PDF)', '📄 Tech Domains Report (PDF)')
c = c.replace('📊 Methodenbericht (PDF)', '📊 Methodology Report (PDF)')

# Hero
c = c.replace('Version 2.4.0 • Stand: Oktober 2026', 'Version 2.4.0 • Effective: October 2026')
c = c.replace('Von den Rohdaten zum <span class="glow">Endprodukt</span>', 'From Raw Data to <span class="glow">Strategic End-Product</span>')
c = c.replace(
    'Die vollständige Reise unseres Daten- und Analyse-Tracks: Wie wir <strong>53 elektrifizierte BMW-Modelle</strong> erfasst, gegen die realen Kundenstudien abgeglichen, nach <strong>7 Technologie-Domänen</strong> strukturiert und über ein mathematisches <strong>Net-Sentiment- & Schweregrad-Modell</strong> in priorisierte Engineering Action Items überführt haben.',
    'The end-to-end journey of our data intelligence track: How we inventoried <strong>53 electrified BMW models</strong>, matched them against empirical customer studies, structured them across <strong>7 technology domains</strong>, and applied a rigorous <strong>Net Sentiment & Severity mathematical model</strong> to establish prioritized engineering action items.'
)

# Hero action buttons & Stepper
c = c.replace('>01 Flottendaten<', '>01 Fleet Census<')
c = c.replace('>02 Matching-Filter<', '>02 Cohort Matching<')
c = c.replace('>03 7 Technologie-Domänen<', '>03 7 Tech Domains<')
c = c.replace('>04 Mathematische Modellierung<', '>04 Mathematical Modeling<')
c = c.replace('>05 Endprodukt & Pipeline<', '>05 End-Product & Pipeline<')

c = c.replace('<span class="step-tag">Rohdaten</span>', '<span class="step-tag">Raw Data</span>')
c = c.replace('<span class="step-tag">Filterung</span>', '<span class="step-tag">Filtering</span>')
c = c.replace('<span class="step-title">16 Matched Modelle</span>', '<span class="step-title">16 Matched Models</span>')
c = c.replace('<span class="step-tag">Architektur</span>', '<span class="step-tag">Architecture</span>')
c = c.replace('<span class="step-title">7 Tech-Domänen</span>', '<span class="step-title">7 Tech Domains</span>')
c = c.replace('<span class="step-title">Net Sentiment Math</span>', '<span class="step-title">Net Sentiment Math</span>')
c = c.replace('<span class="step-title">Engineering Backlog</span>', '<span class="step-title">Engineering Backlog</span>')

# Phase 1
c = c.replace('Die Datenbasis: Vollständiger BMW EV & PHEV Katalog', 'The Empirical Baseline: Complete BMW EV & PHEV Catalog')
c = c.replace('ADAC Autokatalog + Offizielle Preislisten', 'ADAC Autokatalog + Official Price Lists')
c = c.replace(
    'Ausgangspunkt war die lückenlose Erfassung aller in Europa und weltweit verfügbaren rein elektrischen (BEV) und Plug-in-Hybrid (PHEV) Fahrzeuge von BMW. Über ADAC-Spezifikationen und offizielle Preislisten-Datenblätter wurden technische Parameter mit Ausstattungs-Highlights in den Bereichen <strong>Interieur, Exterieur und Fahrassistenz</strong> angereichert.',
    'Our starting point was the exhaustive census of all battery-electric (BEV) and plug-in hybrid (PHEV) vehicles produced by BMW for Europe and global markets. Leveraging official ADAC specifications and price list equipment catalogs, technical metrics were enriched with standard and optional equipment across <strong>Interior, Exterior, and Driver Assistance</strong>.'
)
c = c.replace('<span class="metric-label">Erfasste Modelle</span>', '<span class="metric-label">Inventoried Models</span>')
c = c.replace('100% des elektrifizierten BMW Portfolios (iX1, i4, i5, i7, iX, 3er–7er PHEVs)', '100% of electrified BMW portfolio (iX1, i4, i5, i7, iX, 3–7 Series PHEVs)')
c = c.replace('<span class="metric-label">Antriebs-Split</span>', '<span class="metric-label">Powertrain Split</span>')
c = c.replace('Reine Batterie-Stromer und Hochvolt-Plug-in-Hybride', 'Pure Battery Electrics & High-Voltage Plug-in Hybrids')
c = c.replace('<span class="metric-label">Batteriekapazitäten</span>', '<span class="metric-label">Battery Capacities</span>')
c = c.replace('Von 225xe (14.9 kWh) bis zum Langstrecken-SAV iX xDrive50', 'From 225xe (14.9 kWh) to long-range SAV iX xDrive50')
c = c.replace('<span class="metric-label">Reichweiten-Spanne</span>', '<span class="metric-label">Range Spectrum</span>')
c = c.replace('Offizielle WLTP-Kennwerte aller Baureihen', 'Official WLTP range across all vehicle lines')
c = c.replace('<strong style="color:#ffffff;">Erhobene Preislisten-Attribute je Modell:</strong>', '<strong style="color:#ffffff;">Official Price List Attributes Tracked Per Model:</strong>')
c = c.replace('• <strong>Interieur:</strong> BMW Curved Display', '• <strong>Interior:</strong> BMW Curved Display')
c = c.replace('• <strong>Exterieur:</strong> BMW Niere Iconic Glow', '• <strong>Exterior:</strong> BMW Kidney Grille Iconic Glow')
c = c.replace('• <strong>Fahrassistenz:</strong> Driving Assistant Professional', '• <strong>Driver Assistance:</strong> Driving Assistant Professional')

# Phase 2
c = c.replace('Die Schnittmenge: Abgleich mit Kundenstudien & Bereinigung', 'Cohort Intersection: Alignment with Customer Studies & Cleaning')
c = c.replace('100% ICE & F70 Ausschluss', '100% Strict ICE & F70 Exclusion')
c = c.replace(
    'Um reale Kundenbeanstandungen präzise den elektrifizierten Fahrzeugen zuzuordnen, haben wir die 53 Modelle mit den Kundenbefragungen aus <code>F70_G60_G68_G70_customer_studies.xlsx</code> sowie den Detail-Feederdateien abgeglichen. Eine strenge methodische Bereinigung war unverzichtbar, um Verzerrungen durch Verbrennungsmotoren zu verhindern.',
    'To accurately correlate real customer friction points with electrified architectures, we aligned the 53 catalog vehicles with empirical customer studies from <code>F70_G60_G68_G70_customer_studies.xlsx</code> and detailed feedback logs. Strict methodological cleaning was essential to eliminate distortion caused by internal combustion powertrains.'
)
c = c.replace('<span class="metric-label">Gesamter Feedback-Pool</span>', '<span class="metric-label">Total Survey Pool</span>')
c = c.replace('9.695 Einträge', '9,695 Records')
c = c.replace('G60 (5er) + G70 (7er) Rohdaten', 'G60 (5 Series) + G70 (7 Series) Raw Data')
c = c.replace('<span class="metric-label" style="color:#f87171;">Eliminierte Verbrenner</span>', '<span class="metric-label" style="color:#f87171;">Eliminated Combustion ICE</span>')
c = c.replace('520i, 520d, 740i etc. 100% ausgeschlossen', '520i, 520d, 740i etc. 100% Excluded')
c = c.replace('<span class="metric-label" style="color:#34d399;">Verifizierte EV-Schnittmenge</span>', '<span class="metric-label" style="color:#34d399;">Verified Electrified Cohort</span>')
c = c.replace('16 Modelle / 3.971 Zeilen', '16 Models / 3,971 Records')
c = c.replace('Reine i5, i7, 5er PHEV, 7er PHEV Kohorten', 'Pure i5, i7, 5 Series PHEV, 7 Series PHEV Cohorts')
c = c.replace('Feedback-Fälle', 'Feedback Cases')
c = c.replace('gematchte Modelle', 'Matched Models')

# Phase 3
c = c.replace('Die 7 Technologie-Domänen (Architektur & MECE-Validierung)', 'The 7 Technology Domains (Architecture & MECE Validation)')
c = c.replace('Industriestandard NEV / SDV', 'NEV / SDV Industry Standard')
c = c.replace(
    'Die Strukturierung erfolgte entlang international anerkannter Benchmarking-Domänen (Dongchedi, CPCA, McKinsey Connected Vehicle). Die 7 Domänen sind <strong>vollständig MECE</strong> (Mutually Exclusive, Collectively Exhaustive) und trennen trennscharf zwischen physischer Aktorik, In-Cabin Software und Offboard-Konnektivität.',
    'Classification follows internationally recognized automotive benchmark domains (Dongchedi, CPCA, McKinsey Connected Vehicle). The 7 domains are <strong>strictly MECE</strong> (Mutually Exclusive, Collectively Exhaustive), providing sharp separation between physical actuators, in-cabin software, and off-board connectivity.'
)
c = c.replace('Prio 1 Backlog', 'Prio 1 Backlog')
c = c.replace('aller Fälle', 'of All Cases')
c = c.replace('Geringste Fehlerrate', 'Lowest Defect Rate')
c = c.replace('Höchste Severity (2,03)', 'Highest Severity (2.03)')
c = c.replace('Krisenpunkt (-76,7%)', 'Critical Friction (-76.7%)')
c = c.replace('Volumenstärkste Domäne', 'Highest Volume Domain')
c = c.replace('Brand Moat (+44,7%)', 'Brand Moat (+44.7%)')
c = c.replace('Bestnote 9,95/10', 'Top Score 9.95/10')
c = c.replace('Hohe Severity (2,07)', 'High Severity (2.07)')
c = c.replace('Kritik:', 'Friction:')
c = c.replace('• <strong>Fokus:</strong>', '• <strong>Focus:</strong>')
c = c.replace('• <strong>Kritik:</strong>', '• <strong>Friction:</strong>')
c = c.replace('• <strong>Stärke:</strong>', '• <strong>Strength:</strong>')

# Phase 4
c = c.replace('Mathematische Modellierung & Analytics (Likes vs. Friction)', 'Mathematical Modeling & Analytics (Likes vs. Friction)')
c = c.replace(
    'Um die Kundenstimmen objektiv quantifizierbar zu machen, haben wir ein mathematisches Berechnungsmodell aufgestellt. Es trennt zwischen reinem Kundenlob (<em>Likes</em>) und realer Unzufriedenheit (<em>Friction</em>) und gewichtet die Schwere der Beanstandungen nach Automotive-FMEA-Standards.',
    'To make customer sentiment objectively quantifiable, we formulated a rigorous mathematical model. It cleanly separates positive customer praise (<em>Likes</em>) from real dissatisfaction (<em>Friction</em>) and weights complaint severity according to automotive FMEA principles.'
)
c = c.replace('Wertebereich von +100% bis -100%. Positiv = Netto-Begeisterung; Negativ = Reibung überwiegt.', 'Scale from +100% to -100%. Positive = Net customer advocacy; Negative = Friction predominates.')
c = c.replace('Gewichte: Defect = 3 (Hardware), Difficult to Use = 2 (UX), Wants = 1 (Wunsch). Skala 1.00 – 3.00.', 'Weights: Defect = 3 (Hardware), Difficult to Use = 2 (UX), Wants = 1 (Wish). Scale 1.00 – 3.00.')
c = c.replace('Multiplikativer Prio-Faktor für die Engineering Pipeline zur Identifikation der teuersten Hebel.', 'Multiplicative priority index for the engineering pipeline to pinpoint the highest-leverage fixes.')

# Table headers
c = c.replace('<th>Rang & Domäne</th>', '<th>Rank & Domain</th>')
c = c.replace('<th>Lob (Likes)</th>', '<th>Praise (Likes)</th>')
c = c.replace('<th>Kritik (Friction)</th>', '<th>Friction (Complaints)</th>')
c = c.replace('<th>Evaluierte Basis</th>', '<th>Evaluated Universe</th>')
c = c.replace('<th>Ø Severity</th>', '<th>Avg. Severity</th>')
c = c.replace('<th>Dominanter Schmerzpunkt</th>', '<th>Dominant Friction Point</th>')
c = c.replace('Gesamtsumme / Durchschnitt', 'Total Universe / Weighted Average')
c = c.replace('53,2% aller Beanstandungen sind UX-Hürden!', '53.2% of all complaints are UX hurdles!')

# Callout paradox
c = c.replace('💡 Das fundamentale Paradoxon der BMW-Kundenstudie:', '💡 The Fundamental Paradox of the BMW Customer Study:')
c = c.replace('• <strong>Hardware & Mechanik sind Weltklasse:</strong>', '• <strong>Hardware & Mechanics are World-Class:</strong>')
c = c.replace(
    'Mit 9,95/10 und +44,7% Net Sentiment ist das Fahrwerk von i5 und i7 die absolute Referenz.',
    'With 9.95/10 satisfaction and +44.7% Net Sentiment, chassis engineering on i5 and i7 represents the gold standard.'
)
c = c.replace('• <strong>Die Achillesferse ist Software & Ergonomie:</strong>', '• <strong>The Achilles Heel is Software & Ergonomics:</strong>')
c = c.replace(
    'Über <strong>53% aller Beanstandungen</strong> sind keine Hardware-Defekte (`Defect`), sondern `Difficult to Use` (UX-Hürden). Die Autos sind nicht kaputt – die Kunden scheitern an verschachtelten Touch-Menüs, übervorsichtigen Türsensoren und nicht auffindbaren Lade-Vorheiz-Funktionen!',
    'Over <strong>53% of all complaints</strong> are not hardware breakdowns (`Defect`), but `Difficult to Use` (UX friction). The vehicles are mechanically sound – customers are frustrated by nested touchscreen menus, oversensitive door sensors, and hidden battery thermal preconditioning toggles!'
)

# Phase 5
c = c.replace('Das Endprodukt: Priority Engineering Backlog & Deliverables', 'The End-Product: Priority Engineering Backlog & Deliverables')
c = c.replace(
    'Das finale Ergebnis unseres Tracks: Eine automatisierte Pipeline, die aus den Kundenbeschwerden ein priorisiertes <strong>Engineering Backlog</strong> erzeugt, inklusive O-Ton-Zitaten und konkreten Handlungsempfehlungen.',
    'The final deliverable of our intelligence track: An automated pipeline converting raw customer feedback into a prioritized <strong>Engineering Backlog</strong>, complete with verbatim quotes and concrete architectural action items.'
)

c = c.replace('<th>Prio</th>', '<th>Prio</th>')
c = c.replace('<th>Domäne & Baugruppe</th>', '<th>Domain & Component</th>')
c = c.replace('<th>Fälle</th>', '<th>Cases</th>')
c = c.replace('<th>Prio-Score</th>', '<th>Prio Score</th>')
c = c.replace('<th>Original Kunden-O-Ton (Verbatim)</th>', '<th>Customer Verbatim Quote</th>')
c = c.replace('<th>Empfohlene Engineering-Maßnahme</th>', '<th>Recommended Engineering Action</th>')

c = c.replace('Manueller Pre-Heat Button in QuickSelect-Bar; dynamischer Winter-SoC-Puffer in Navigation.', 'Add manual battery pre-heat button in QuickSelect dock; dynamic cold-weather SoC buffer in native nav.')
c = c.replace('Autonavi-Kopplung für Fremdsäulen optimieren; Ladekurvenabfall über 60% SoC glätten.', 'Enable automatic pre-conditioning for 3rd-party charging hubs; smooth out charging curve drop above 60% SoC.')
c = c.replace('Türgriff-Beheizung / Enteisungslogik patchen; A-Säulen-Dichtungsgeometrie nachjustieren.', 'Patch door handle heating and de-icing logic via OTA; refine A-pillar weather-strip sealing geometry.')
c = c.replace('Persistente Docking-Leiste für Klima am Bildschirmrand; Sprachassistenz-Latenz <800ms senken.', 'Pin persistent docking tray for climate controls; reduce voice assistant latency below 800ms.')
c = c.replace('E-Motor-Drehmomentrampe während Verbrenner-Zündung softwareseitig harmonisieren.', 'Smooth e-motor torque delivery ramp during combustion engine engagement via software calibration.')

# Deliverables
c = c.replace('Generierte Deliverables (1-Click Download):', 'Generated Pipeline Deliverables (1-Click Download):')
c = c.replace('PDF Report (4 Seiten)', 'PDF Report (4 Pages)')
c = c.replace('Detaillierte Analyse aller 7 Domänen mit O-Tönen und Kohorten-Splits.', 'Exhaustive analysis across all 7 domains with verbatims and cohort splits.')
c = c.replace('PDF Report (2 Seiten)', 'PDF Report (2 Pages)')
c = c.replace('Methodik- & Ranglistenbericht', 'Methodology & Ranking Report')
c = c.replace('Mathematische Formeln für Net Sentiment, Severity und Datenherkunft.', 'Mathematical formulations for Net Sentiment, Severity weighting, and data provenance.')
c = c.replace('Hierarchischer Datensatz für REST-APIs, LLM-RAG und ML-Modelle.', 'Hierarchical schema for REST APIs, LLM RAG pipelines, and automated downstream processing.')
c = c.replace('CSV Datensatz (1.892 Zeilen)', 'CSV Dataset (1,892 Records)')
c = c.replace('Alle 1.892 Einzelbeanstandungen mit Schweregraden und Text-O-Tönen.', 'All 1,892 individual complaint records with severity scores and customer quotes.')

with open('bmw_pipeline_story.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Translated bmw_pipeline_story.html to English successfully!')
