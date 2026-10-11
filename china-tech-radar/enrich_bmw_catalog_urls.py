#!/usr/bin/env python3
import csv
import json

bmw_press_map = {
    'iX1': 'https://www.press.bmwgroup.com/global/article/detail/T0387532EN/the-all-new-bmw-ix1-and-the-all-new-bmw-x1',
    'i3': 'https://www.press.bmwgroup.com/global/article/detail/T0285098EN/the-bmw-i3-and-the-bmw-i3s',
    'i3s': 'https://www.press.bmwgroup.com/global/article/detail/T0285098EN/the-bmw-i3-and-the-bmw-i3s',
    'X1': 'https://www.press.bmwgroup.com/global/article/detail/T0387532EN/the-all-new-bmw-ix1-and-the-all-new-bmw-x1',
    'i4': 'https://www.press.bmwgroup.com/global/article/detail/T0334000EN/the-first-ever-bmw-i4',
    'X5': 'https://www.press.bmwgroup.com/global/article/detail/T0408453EN/the-new-bmw-x5-and-the-new-bmw-x6',
    'iX': 'https://www.press.bmwgroup.com/global/article/detail/T0334006EN/the-all-new-bmw-ix',
    'i5': 'https://www.press.bmwgroup.com/global/article/detail/T0417751EN/the-all-new-bmw-5-series-sedan-and-the-all-new-bmw-i5',
    'i5 Touring': 'https://www.press.bmwgroup.com/global/article/detail/T0439247EN/the-new-bmw-5-series-touring-and-the-new-bmw-i5-touring',
    '3er': 'https://www.press.bmwgroup.com/global/article/detail/T0393685EN/the-new-bmw-3-series-sedan-and-bmw-3-series-touring',
    '3er Touring': 'https://www.press.bmwgroup.com/global/article/detail/T0393685EN/the-new-bmw-3-series-sedan-and-bmw-3-series-touring',
    '2er Active Tourer': 'https://www.press.bmwgroup.com/global/article/detail/T0348744EN/the-all-new-bmw-2-series-active-tourer',
    '5er': 'https://www.press.bmwgroup.com/global/article/detail/T0417751EN/the-all-new-bmw-5-series-sedan-and-the-all-new-bmw-i5',
    '5er Touring': 'https://www.press.bmwgroup.com/global/article/detail/T0439247EN/the-new-bmw-5-series-touring-and-the-new-bmw-i5-touring',
    'X3': 'https://www.press.bmwgroup.com/global/article/detail/T0442345EN/the-all-new-bmw-x3',
    'iX3': 'https://www.press.bmwgroup.com/global/article/detail/T0339591EN/the-new-bmw-ix3',
    'iX2': 'https://www.press.bmwgroup.com/global/article/detail/T0436444EN/the-all-new-bmw-x2-and-the-first-ever-bmw-ix2',
    'X2': 'https://www.press.bmwgroup.com/global/article/detail/T0436444EN/the-all-new-bmw-x2-and-the-first-ever-bmw-ix2',
    'i7': 'https://www.press.bmwgroup.com/global/article/detail/T0378873EN/the-all-new-bmw-7-series-and-the-first-ever-bmw-i7',
    '7er': 'https://www.press.bmwgroup.com/global/article/detail/T0378873EN/the-all-new-bmw-7-series-and-the-first-ever-bmw-i7',
    'M5': 'https://www.press.bmwgroup.com/global/article/detail/T0442751EN/the-all-new-bmw-m5',
    'M5 Touring': 'https://www.press.bmwgroup.com/global/article/detail/T0444319EN/the-all-new-bmw-m5-touring',
    'XM': 'https://www.press.bmwgroup.com/global/article/detail/T0403759EN/the-first-ever-bmw-xm',
    'i8': 'https://www.press.bmwgroup.com/global/article/detail/T0276606EN/the-new-bmw-i8-coupe-the-new-bmw-i8-roadster'
}

SALES_URL = "https://www.bmwgroup.com/en/investor-relations/company-reports.html"

def update_csv():
    with open('bmw_ev_phev_catalog.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # Insert bmw_press_url and sales_evidence_url after adac_url
    if 'bmw_press_url' not in fieldnames:
        idx = fieldnames.index('adac_url') + 1
        fieldnames.insert(idx, 'bmw_press_url')
        fieldnames.insert(idx + 1, 'sales_evidence_url')

    for r in rows:
        m = r['model']
        r['bmw_press_url'] = bmw_press_map.get(m, 'https://www.press.bmwgroup.com')
        r['sales_evidence_url'] = SALES_URL

    with open('bmw_ev_phev_catalog.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print("Updated bmw_ev_phev_catalog.csv successfully.")

def update_json_and_js():
    with open('bmw_ev_phev_catalog.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    data['sources'] = [
        "BMW Group Official Investor Relations & Annual Company Reports (https://www.bmwgroup.com/en/investor-relations/company-reports.html)",
        "BMW Group Official PressClub Technical Data Sheets & Press Kits (https://www.press.bmwgroup.com)",
        "KBA Kraftfahrt-Bundesamt Neuzulassungen & ACEA European EV Registrations",
        "ADAC Autokatalog & Offizielle BMW Preislisten"
    ]

    for car in data['cars']:
        m = car['model']
        car['bmw_press_url'] = bmw_press_map.get(m, 'https://www.press.bmwgroup.com')
        car['sales_evidence_url'] = SALES_URL

    with open('bmw_ev_phev_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Updated bmw_ev_phev_catalog.json successfully.")

    with open('data_bmw.js', 'w', encoding='utf-8') as f:
        f.write("window.BMW_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")
    print("Updated data_bmw.js successfully.")

if __name__ == '__main__':
    update_csv()
    update_json_and_js()
