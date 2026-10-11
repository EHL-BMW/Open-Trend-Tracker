import os
import re
import pandas as pd
import numpy as np

# Load raw feedback datasets
g60_path = '/Users/miao/Desktop/Hackathon/G60_feedback_hackathon.xlsx'
g70_path = '/Users/miao/Desktop/Hackathon/G70_feedback_hackathon.xlsx'

g60 = pd.read_excel(g60_path)
g70 = pd.read_excel(g70_path)

g60_ev = g60[g60['Engine Type'].isin(['BEVE', 'PHEV'])].copy()
g70_ev = g70[g70['Engine Type'].isin(['BEVE', 'PHEV'])].copy()

g60_ev['Series'] = '5er'
g70_ev['Series'] = '7er'

all_ev = pd.concat([g60_ev, g70_ev], ignore_index=True)
complaints = all_ev[all_ev['Feedback Type'].isin(['Difficult to Use', 'Defect', 'Wants'])].copy().reset_index(drop=True)

print(f"Total electrified complaints/improvements loaded: {len(complaints)}")

# Taxonomy domain mapping
def get_domain_info(row):
    vfc2 = str(row['Vfc level2 Name']).strip()
    vfc3 = str(row['Vfc level3 Name']).strip()
    
    # 1. Energy & Charging
    if any(k in vfc2 for k in [
        'Electric Range', 'Public charging', 'Charge high-voltage battery', 'High voltage battery',
        'High-voltage charging', 'Wallbox', 'Charging cable', 'Route optimized for charging',
        'Vehicle battery', 'preconditioning', 'Opening/closing charging socket cover'
    ]) or any(k in vfc3 for k in ['Charging', 'Battery', 'Recharge']):
        return (
            'Energy & Charging',
            '补能体验、续航管理、对外供电',
            'Charging experience, Range management, V2X/Power supply'
        )
        
    # 2. Driving Assistance
    if any(k in vfc2 for k in [
        'Parking Assistant', 'Highway assistant', 'Park Distance Control', 'Driver assistance',
        'Lane departure warning', 'Remote controlled parking', 'Front collision warning',
        'Speed Limit Assistant', 'Blind spot monitoring', 'Cross Traffic Warning',
        'Lane Change Assistant', '(Active) cruise control', 'Surround View', 'Rear view camera',
        'Traffic Light And Sign Warning', 'Back-up Assistant', 'Steering and lane guide assist',
        'Night Vision', 'Emergency Stop Assistant', 'Side View', 'Traffic Camera Information',
        'All-round view', 'Drive Recorder', 'Rear-end collision warning'
    ]):
        return (
            'Driving Assistance',
            '城市/高速辅助、泊车、人车交接',
            'Highway/City pilot, Automated parking, Driver-vehicle handover'
        )
        
    # 3. Digital Cockpit & AI
    if any(k in vfc2 for k in [
        'ConnectedDrive and Infotainment', 'Audio mode', 'Navigation', 'Touch screen',
        'Operating concept', 'Instrument cluster', 'Instrument panel', 'Intelligent Personal Assistant',
        'Head-Up Display', 'Radio function', 'Rear seat entertainment', 'Ambient light',
        'Apps (in-car)', 'Voice control', 'Touch Command', 'Controller operation',
        'Gesture control', 'Screen mirroring', 'Video: playback', 'CD / DVD', 'Display, time',
        'Driver profile', 'Multi-function steering wheel operation', 'Smart POI search'
    ]):
        return (
            'Digital Cockpit & AI',
            '显示交互、语音助手、娱乐',
            'Display & Interaction, Voice assistant, In-cabin entertainment'
        )
        
    # 4. Connected Ecosystem
    if any(k in vfc2 for k in [
        'Apple CarPlay', 'Personal eSIM', 'My BMW App', 'Remote Software Upgrade', 'Digital Key',
        'Remote Services', 'Manage / pair mobile device', 'WiFi hotspot', 'Remote Engine Start',
        'Android Auto', 'ConnectedDrive upgrades', 'Map update', 'My BMW / MINI Portal',
        'Remote interior camera', 'Remote 3D View', 'ConnectedDrive services', 'Apps (smartphone)',
        'Teleservices', "Driver's Guide App", 'Vehicle key', 'Display key', 'Mobile device, wireless charging',
        'Priorities for telephones', 'USB port'
    ]):
        return (
            'Connected Ecosystem',
            '手机与车互联、远程服务、OTA',
            'Smartphone integration, Remote telematics, OTA updates'
        )
        
    # 5. Smart Cabin
    if any(k in vfc2 for k in [
        'Seats', 'Panorama glass roof', 'Vehicle, climatization', 'Blower function',
        'Center console', 'Interior design', 'Air conditioning', 'Seating, ventilate',
        'Sun protection', 'Luggage compartment', 'Side window', 'Heated steering wheel',
        'Storage compartments', 'Seat memory', 'Door, finisher panel', 'Interior acoustics',
        'Seat massage', 'Steering wheel', 'Glove box', 'Center armrest', 'Cupholder',
        'Headrest', 'Interior rearview mirror', 'Adjustment of lower lumbar support',
        'Cooling', 'Space / spatial', 'Upholstery', 'Interior camera', 'Interior',
        'Sun visor', 'Garage door opener', 'Vehicle interior, lighting', '12 V connection',
        'Pedals', 'Panel heating', 'Heated rear window', 'Through-loading', 'Roof function centre',
        'Grab handle', 'Auxiliary heater function', 'Child restraint seat', 'Interior comfort',
        'Headrests, rear'
    ]):
        return (
            'Smart Cabin',
            '温控储物、座椅、空气与舒适',
            'Thermal control, Storage, Smart seating, Air & Comfort'
        )
        
    # 6. Vehicle Dynamics & Safety
    if any(k in vfc2 for k in [
        'Drivetrain', 'My Modes', 'Brake Energy Regeneration', 'Braking', 'Wheels / tires',
        'Seat belts', 'Impression of safety', 'Automatic-hold', 'Engine acoustics', 'Handling',
        'Steering', 'Cushioning / damping', 'Start engine', 'Tire pressure control',
        'Starting engine', 'Anti-theft alarm system', 'Dynamic Stability Control', 'Launch Control',
        'Operate selector lever', 'Fatigue Alert', 'Child safety latch', 'Vehicle safety',
        'Shift paddle', 'Experience Modes', 'Parking brake', 'Self-leveling suspension',
        'Transmission', 'RSC tire', 'Emergency request'
    ]) or ('ground' in vfc2.lower() and 'clearance' in vfc2.lower()):
        return (
            'Vehicle Dynamics & Safety',
            '驾驶控制、底盘、乘员保护',
            'Drive control, Chassis dynamics, Occupant protection'
        )
        
    # 7. Smart Exterior
    if any(k in vfc2 for k in [
        'Body equipment', 'non-contact trunk lid opening', 'Door, open', 'Exterior',
        'Trunk lid', 'Frunk', 'Vehicle, lock / unlock', 'Exterior design', 'Exterior rearview mirror',
        'Door, front', 'Exterior lighting', 'Accessories / Parts',
        'Tirefit', 'Fuel filler flap', 'Vehicle, access and exit', 'Automatic doors',
        'Windshield wiper', 'Radiator grille', 'Horns', 'Trailer, use', 'Bumper',
        'Washer fluid', 'Hood, open', 'Rain sensor mode', 'Flashing', 'Outer door handle',
        'Trunk light', 'Exhaust system', 'Welcome Light Carpet', 'Rear wiper', 'Roof',
        'Light switch operating unit', 'High-beam assistant', 'Windshield', 'Side sill trim panel',
        'Fuel tank', 'Comfort Access', 'Resting state after door opening'
    ]):
        return (
            'Smart Exterior',
            '智能灯光、车门、空气动力学',
            'Smart lighting, Powered doors, Aerodynamics & Body'
        )
        
    return (
        'General & Services',
        '用户手册、售后交车与综合服务',
        'User manual, Dealership delivery & General service'
    )

domain_res = complaints.apply(get_domain_info, axis=1)
complaints['technology_domain'] = [r[0] for r in domain_res]
complaints['aspect_cn'] = [r[1] for r in domain_res]
complaints['aspect_en'] = [r[2] for r in domain_res]

# Cohort determination
def get_cohort(row):
    s = row['Series']
    e = row['Engine Type']
    if s == '5er' and e == 'BEVE':
        return 'i5 BEV'
    elif s == '5er' and e == 'PHEV':
        return '5er PHEV'
    elif s == '7er' and e == 'BEVE':
        return 'i7 BEV'
    elif s == '7er' and e == 'PHEV':
        return '7er PHEV'
    return 'Other'

complaints['cohort'] = complaints.apply(get_cohort, axis=1)
complaints['powertrain'] = complaints['Engine Type'].apply(lambda x: 'BEV' if x == 'BEVE' else 'PHEV')

# Severity scoring
severity_map = {'Defect': 3, 'Difficult to Use': 2, 'Wants': 1}
complaints['severity_score'] = complaints['Feedback Type'].map(severity_map).fillna(1).astype(int)

# Inferred system type
def infer_system_type(row):
    vfc2 = str(row['Vfc level2 Name']).lower()
    text = str(row['Customer Feedback']).lower()
    if any(k in vfc2 or k in text for k in ['app', 'software', 'ota', 'update', 'os', 'screen', 'touch', 'bluetooth', 'wifi', 'carplay', 'esim', 'menu', 'display', 'voice']):
        return 'Software / UX'
    elif any(k in vfc2 or k in text for k in ['door', 'seat', 'gap', 'fit', 'noise', 'rattle', 'climat', 'glass', 'panel', 'paint', 'socket', 'plug', 'tire', 'wheel', 'brake']):
        return 'Hardware / Physical'
    return 'Hybrid / System'

complaints['system_layer'] = complaints.apply(infer_system_type, axis=1)

# Format record CSV
records_df = complaints[[
    'ID', 'Source', 'Brand', 'Series', 'cohort', 'Sales Description', 'Derivate (e-code)',
    'powertrain', 'Engine Type', 'Country', 'Feedback Type', 'severity_score',
    'technology_domain', 'aspect_cn', 'aspect_en', 'system_layer',
    'Vfc level2 Name', 'Vfc level3 Name', 'Customer Feedback'
]].copy()

records_df.columns = [
    'feedback_id', 'data_source', 'brand', 'series', 'cohort', 'sales_model_name', 'derivate_code',
    'powertrain', 'engine_type_code', 'country', 'feedback_type', 'severity_weight',
    'technology_domain', 'aspect_cn', 'aspect_en', 'system_layer',
    'vfc_level2_component', 'vfc_level3_subsystem', 'customer_feedback_verbatim'
]

records_csv_path = '/Users/miao/Desktop/Hackathon/bmw_ev_technology_domain_records.csv'
records_df.to_csv(records_csv_path, index=False, encoding='utf-8')
print(f"Saved records CSV: {records_csv_path} ({len(records_df)} rows)")

# Create Pivot Matrix CSV
matrix_df = pd.crosstab(
    records_df['technology_domain'],
    records_df['cohort'],
    margins=True,
    margins_name='Total'
)
matrix_df['Share_Pct'] = (matrix_df['Total'] / len(records_df) * 100).round(2)
# Sort by Total descending (except 'Total' row at end)
domains_sorted = matrix_df.drop('Total').sort_values('Total', ascending=False)
total_row = matrix_df.loc[['Total']]
matrix_df = pd.concat([domains_sorted, total_row])

matrix_csv_path = '/Users/miao/Desktop/Hackathon/bmw_ev_technology_domain_matrix.csv'
matrix_df.to_csv(matrix_csv_path, encoding='utf-8')
print(f"Saved matrix CSV: {matrix_csv_path}")

# Create Aggregated Summary CSV
domain_summary_list = []
for dom, group in records_df.groupby('technology_domain'):
    top_vfc = group['vfc_level2_component'].value_counts().head(3)
    top_vfc_str = "; ".join([f"{k} ({v})" for k, v in top_vfc.items()])
    
    bev_c = len(group[group['powertrain'] == 'BEV'])
    phev_c = len(group[group['powertrain'] == 'PHEV'])
    
    def_c = len(group[group['feedback_type'] == 'Defect'])
    diff_c = len(group[group['feedback_type'] == 'Difficult to Use'])
    wants_c = len(group[group['feedback_type'] == 'Wants'])
    
    sample_quote = group.iloc[0]['customer_feedback_verbatim']
    if len(str(sample_quote)) > 140:
        sample_quote = str(sample_quote)[:137] + '...'
        
    domain_summary_list.append({
        'technology_domain': dom,
        'aspect_cn': group.iloc[0]['aspect_cn'],
        'aspect_en': group.iloc[0]['aspect_en'],
        'total_complaints': len(group),
        'overall_share_pct': round(len(group) / len(records_df) * 100, 2),
        'bev_count': bev_c,
        'phev_count': phev_c,
        'i5_bev': len(group[group['cohort'] == 'i5 BEV']),
        'i7_bev': len(group[group['cohort'] == 'i7 BEV']),
        '5er_phev': len(group[group['cohort'] == '5er PHEV']),
        '7er_phev': len(group[group['cohort'] == '7er PHEV']),
        'defect_count': def_c,
        'difficult_to_use_count': diff_c,
        'wants_count': wants_c,
        'avg_severity': round(group['severity_weight'].mean(), 2),
        'top_vfc_components': top_vfc_str,
        'representative_customer_feedback': sample_quote
    })

summary_df = pd.DataFrame(domain_summary_list).sort_values('total_complaints', ascending=False).reset_index(drop=True)
summary_csv_path = '/Users/miao/Desktop/Hackathon/bmw_ev_technology_domain_summary.csv'
summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8')
print(f"Saved summary CSV: {summary_csv_path}")

print("CSV data pipelines generated successfully!")
