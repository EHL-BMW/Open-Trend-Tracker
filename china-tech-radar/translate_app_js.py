with open('app.js', 'r', encoding='utf-8') as f:
    c = f.read()

replacements = {
    'BMW Fleet: Alle <span class="gradient-text">EV & PHEV Modelle</span> (53 Varianten)': 'BMW Fleet: All <span class="gradient-text">EV & PHEV Models</span> (53 Variants)',
    'Lückenlose Erfassung aller 53 existierenden rein elektrischen (BEV) und Plug-in-Hybrid (PHEV) Modelle von <strong>BMW</strong> (iX1, iX2, iX3, i4, i5, i7, iX, 2er, 3er, 5er, 7er, X1, X2, X3, X5, XM, M5, i3, i8) mit offiziellen <strong>Preislisten-Ausstattungsdetails</strong>, ADAC-Daten und technischen Kennwerten.': 'Complete enumeration of all 53 existing battery-electric (BEV) and plug-in hybrid (PHEV) models by <strong>BMW</strong> (iX1, iX2, iX3, i4, i5, i7, iX, 2 Series, 3 Series, 5 Series, 7 Series, X1, X2, X3, X5, XM, M5, i3, i8) with official <strong>price list equipment options</strong>, ADAC specifications, and verified engineering metrics.',
    'ADAC Autokatalog BMW Modelle': 'ADAC Catalog BMW Models',
    '100% des elektrifizierten BMW Portfolios': '100% of electrified BMW portfolio',
    'Jährliche Zulassungen in Europa & weltweit': 'Annual registrations across Europe & globally',
    '45.3% Rein Elektrisch (BEV) • 54.7% PHEV': '45.3% Battery Electric (BEV) • 54.7% PHEV',
    'Preisspektrum & Top-Power': 'Price Range & Top Power',
    '79.250 € Ø • bis 748 PS': '€79,250 Ø • Up to 748 hp',
    'BMW Grundpreise • Bis 1.000 Nm XM/M5': 'BMW base MSRP • Up to 1,000 Nm XM/M5',
    'BMW Listenpreis': 'Base Price (MSRP)',
    'WLTP Reichweite': 'WLTP Range',
    'Anhängelast': 'Towing Capacity',
    'DC Ladepeak': 'Peak DC Fast Charge',
    'Kundenstudie & Beanstandungen': 'Customer Study & Complaints',
    'ADAC Katalog': 'ADAC Catalog',
    'BMW Modell, Baureihe oder Ausstattung suchen (z.B. i4, M50, i5 Touring, 330e, 550e, X5 50e, XM, Curved Display, Bowers & Wilkins)...': 'Search BMW model, series, or equipment (e.g. i4, M50, i5 Touring, 330e, 550e, X5 50e, XM, Curved Display, Bowers & Wilkins)...',
    'BMW Flotten-Erfassung & Preislisten-Methodik': 'BMW Fleet Census & Price List Methodology',
    'Alle BMW Baureihen': 'All BMW Series',
    '1. 100% Vollerfassung aller BMW Modelle': '1. 100% Full Census of All Electrified BMW Models',
    '2. Offizielle BMW Preislisten & Ausstattungskataloge': '2. Official BMW Price Lists & Options Catalog',
    '3. ADAC Autokatalog & KBA Zulassungen': '3. ADAC Autokatalog & Registration Volumes',
    'Erfasst jeden einzelnen jemals in Europa offiziell produzierten Serien-BEV und Serien-PHEV von BMW.': 'Captures every single series BEV and PHEV officially produced in Europe by BMW.',
    'Detaillierte Erfassung von Preislisten-Ausstattungen:': 'Comprehensive census of official price list equipment:',
    'Jedes Modell verlinkt direkt auf den offiziellen': 'Every vehicle links directly to official',
    'Exakter Abgleich mit den internen Studien- und Feedbackdateien': 'Exact verification against internal customer study datasets',
    'Alle 53 BMW Modelle': 'All 53 BMW Models',
    'Nur untersuchte Studien-Modelle': 'Studied Cohort Models Only',
    'Nicht in Studie enthalten': 'Unstudied Models'
}

for k, v in replacements.items():
    c = c.replace(k, v)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated app.js successfully!')
