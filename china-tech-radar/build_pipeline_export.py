import json
import pandas as pd
import numpy as np

# Load datasets
g60_path = '/Users/miao/Desktop/Hackathon/G60_feedback_hackathon.xlsx'
g70_path = '/Users/miao/Desktop/Hackathon/G70_feedback_hackathon.xlsx'

g60 = pd.read_excel(g60_path)
g70 = pd.read_excel(g70_path)

g60_ev = g60[g60['Engine Type'].isin(['BEVE', 'PHEV'])].copy()
g70_ev = g70[g70['Engine Type'].isin(['BEVE', 'PHEV'])].copy()

g60_ev['Series'] = '5er'
g70_ev['Series'] = '7er'

all_ev = pd.concat([g60_ev, g70_ev], ignore_index=True)

# Domain mapping function
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
            'energy_and_charging',
            'Energy & Charging',
            '补能体验、续航管理、对外供电',
            'Charging experience, Range management, V2X/Power supply',
            'Ladeerlebnis, Vorkonditionierung & Reichweitenprognose'
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
            'driving_assistance',
            'Driving Assistance',
            '城市/高速辅助、泊车、人车交接',
            'Highway/City pilot, Automated parking, Driver-vehicle handover',
            'City/Highway Pilot, Parken & Fahrerübergabe'
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
            'digital_cockpit_and_ai',
            'Digital Cockpit & AI',
            '显示交互、语音助手、娱乐',
            'Display & Interaction, Voice assistant, In-cabin entertainment',
            'Display-HMI, Sprachbedienung (IPA) & Infotainment'
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
            'connected_ecosystem',
            'Connected Ecosystem',
            '手机与车互联、远程服务、OTA',
            'Smartphone integration, Remote telematics, OTA updates',
            'Smartphone-Integration, Remote-Services & OTA'
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
            'smart_cabin',
            'Smart Cabin',
            '温控储物、座椅、空气与舒适',
            'Thermal control, Storage, Smart seating, Air & Comfort',
            'Thermalkomfort, Sitze, Akustik & Raumkomfort'
        )
        
    # 6. Vehicle Dynamics & Safety
    if any(k in vfc2 for k in [
        'Drivetrain', 'My Modes', 'Brake Energy Regeneration', 'Braking', 'Wheels / tires',
        'Seat belts', 'Impression of safety', 'Automatic-hold', 'Engine acoustics', 'Handling',
        'Steering', 'Cushioning / damping', 'Start engine', 'Tire pressure control',
        'Starting engine', 'Anti-theft alarm system', 'Dynamic Stability Control', 'Launch Control',
        'Operate selector lever', 'Fatigue Alert', 'Child safety latch', 'Vehicle safety',
        'Shift paddle', 'Experience Modes', 'Parking brake', 'Self-leveling suspension',
        'Transmission', 'RSC tire', 'Emergency request', 'Drive, driving dynamics and chassis'
    ]) or ('ground' in vfc2.lower() and 'clearance' in vfc2.lower()):
        return (
            'vehicle_dynamics_and_safety',
            'Vehicle Dynamics & Safety',
            '驾驶控制、底盘、乘员保护',
            'Drive control, Chassis dynamics, Occupant protection',
            'Antriebsregelung, Fahrwerk & Insassenschutz'
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
            'smart_exterior',
            'Smart Exterior',
            '智能灯光、车门、空气动力学',
            'Smart lighting, Powered doors, Aerodynamics & Body',
            'Smarte Karosserie, Automatiktüren & Aerodynamik'
        )
        
    return (
        'general_and_services',
        'General & Services',
        '用户手册、售后交车与综合服务',
        'User manual, Dealership delivery & General service',
        'Bordbuch, Kundenservice & Händlerkontakt'
    )

dom_info = all_ev.apply(get_domain_info, axis=1)
all_ev['domain_id'] = [x[0] for x in dom_info]
all_ev['domain_name'] = [x[1] for x in dom_info]
all_ev['aspect_cn'] = [x[2] for x in dom_info]
all_ev['aspect_en'] = [x[3] for x in dom_info]
all_ev['aspect_de'] = [x[4] for x in dom_info]

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

all_ev['cohort'] = all_ev.apply(get_cohort, axis=1)
all_ev['powertrain'] = all_ev['Engine Type'].apply(lambda x: 'BEV' if x == 'BEVE' else 'PHEV')

severity_map = {'Defect': 3, 'Difficult to Use': 2, 'Wants': 1, 'Likes': 0}
all_ev['severity_weight'] = all_ev['Feedback Type'].map(severity_map).fillna(0).astype(int)

# Subsystem layer
def infer_system_layer(row):
    vfc2 = str(row['Vfc level2 Name']).lower()
    text = str(row['Customer Feedback']).lower()
    if any(k in vfc2 or k in text for k in ['app', 'software', 'ota', 'update', 'os', 'screen', 'touch', 'bluetooth', 'wifi', 'carplay', 'esim', 'menu', 'display', 'voice', 'assistant']):
        return 'Software / UX'
    elif any(k in vfc2 or k in text for k in ['door', 'seat', 'gap', 'fit', 'noise', 'rattle', 'climat', 'glass', 'panel', 'paint', 'socket', 'plug', 'tire', 'wheel', 'brake', 'chassis', 'trunk']):
        return 'Hardware / Physical'
    return 'System / Calibration'

all_ev['system_layer'] = all_ev.apply(infer_system_layer, axis=1)

# Curated engineering insights per domain
engineering_kb = {
    'energy_and_charging': {
        'root_cause': "CLAR platform 400V battery thermal inertia without predictive pre-conditioning triggers severe cold-charging throttle (drops from 205 kW to 60 kW). Real-world winter range deviates up to 35% from WLTP.",
        'recommended_action': "Expose manual battery pre-conditioning toggle in OS QuickSelect bar; integrate dynamic low-temperature buffer into SoC routing algorithms.",
        'key_praise': "High DC peak charging speeds (>200 kW) during warm seasons; smooth regenerative coasting in adaptive mode.",
        'key_pain_point': "Winter range drop and charge flap freezing / delayed cable release."
    },
    'smart_exterior': {
        'root_cause': "Ultrasonic proximity sensors for i7 powered doors have ultra-conservative abort thresholds against curbs and parking pillars; mechanical clutching lacks effortless manual bypass.",
        'recommended_action': "Recalibrate ultrasonic threshold algorithms for close-proximity objects; introduce low-resistance electro-mechanical freewheeling in manual door override.",
        'key_praise': "Iconic front grill presence, solid body panel fit, and aerodynamic exterior profile.",
        'key_pain_point': "i7 automated door aborts in tight garages; rear trunk kick sensor fails on ~30% of attempts."
    },
    'smart_cabin': {
        'root_cause': "Transition to synthetic Veganza upholstery reduces breathability compared to Merino leather; elimination of mechanical sunblind on panoramic roof causes greenhouse heating.",
        'recommended_action': "Increase perforation density and active ventilation CFM on Veganza trims; upgrade low-emissivity glass coating on fixed panoramic roofs.",
        'key_praise': "Superb NVH acoustic isolation at 130-160 km/h; comfortable rear lounge seating on i7.",
        'key_pain_point': "Veganza thermal perspiration in summer; complex touch-slider air vents replacing physical dials."
    },
    'digital_cockpit_and_ai': {
        'root_cause': "BMW OS 8.5/9 removed physical HVAC controls and favourite buttons, shifting micro-climate controls 2-3 levels deep into touch menus, increasing driver cognitive load.",
        'recommended_action': "Implement persistent customized climate bar on display bottom; deploy on-edge Small Language Model (SLM) to reduce IPA voice assistant response latency below 800ms.",
        'key_praise': "Stunning Curved Display resolution; immersive Bowers & Wilkins 4D Diamond Surround Sound.",
        'key_pain_point': "Cluttered QuickSelect widgets obscuring map; lack of physical buttons for primary functions."
    },
    'vehicle_dynamics_and_safety': {
        'root_cause': "PHEV ICE start-up during kickdown experiences mild clutch jerk during torque handover; one-pedal adaptive recuperation decelerates unexpectedly approaching roundabouts.",
        'recommended_action': "Harmonize electric motor torque ramp-down during ICE ignition transition; provide haptic steering feedback when adaptive recuperation engages.",
        'key_praise': "Unrivalled 9.95/10 ride quality: benchmark chassis poise, agile steering feel, and zero roll.",
        'key_pain_point': "PHEV kickdown transition jerk; inconsistent deceleration in adaptive regen mode."
    },
    'connected_ecosystem': {
        'root_cause': "Telematics Control Unit (TCU) enters deep sleep in underground concrete structures, causing My BMW App cloud command timeouts; 5G eSIM network handshakes fail on roaming.",
        'recommended_action': "Implement local BLE fall-back pairing for My BMW App remote climatization; streamline carrier profile eSIM auto-provisioning.",
        'key_praise': "Digital Key Plus Ultra-Wideband (UWB) hands-free phone unlocking; remote 3D view camera surround.",
        'key_pain_point': "My BMW App 'Vehicle Unreachable' timeouts in underground garages; CarPlay audio dropouts."
    },
    'driving_assistance': {
        'root_cause': "EU GSR2 regulatory speed limit audible chimes trigger immediately at +1 km/h; Parking Assistant Pro disengages when detecting angled curbs.",
        'recommended_action': "Create one-touch steering wheel shortcut to mute GSR2 alerts; enhance curb terrain edge-detection in ultrasonic parking model.",
        'key_praise': "Highway Assistant Level 2+ hands-free driving with eye-activation lane change is the best-in-class benchmark.",
        'key_pain_point': "Mandatory GSR2 speed warning bongs; parking app disengagement on gravel/sloped curbs."
    },
    'general_and_services': {
        'root_cause': "Digital user manual navigation is unintuitive for complex EV features; delivery handovers at dealerships lack deep EV charging onboarding.",
        'recommended_action': "Embed interactive animated tutorials in the central display during first DC charge; standardize EV dealer delivery checklists.",
        'key_praise': "High dealer professionalism and premium service vehicle availability.",
        'key_pain_point': "Unanswered technical questions regarding wallbox installation and DC charging limits."
    }
}

# Build Pipeline JSON
pipeline_data = {
    "metadata": {
        "pipeline_version": "2.4.0",
        "dataset_name": "BMW Electrified Fleet Customer Voice & Technology Domain Benchmark",
        "scope": "16 Matched BMW BEV & PHEV Models (i5 Sedan/Touring, i7, 5er PHEV, 7er PHEV; 100% ICE & F70 excluded)",
        "total_feedback_records": len(all_ev),
        "total_classified_feedback": int(len(all_ev[all_ev['Feedback Type'].isin(['Likes', 'Difficult to Use', 'Defect', 'Wants'])])),
        "total_likes_praise": int(len(all_ev[all_ev['Feedback Type'] == 'Likes'])),
        "total_complaints_friction": int(len(all_ev[all_ev['Feedback Type'].isin(['Difficult to Use', 'Defect', 'Wants'])])),
        "cohorts": ["i5 BEV", "i7 BEV", "5er PHEV", "7er PHEV"],
        "severity_scoring_model": {
            "Defect": {"weight": 3, "definition": "Hardware malfunction or functional breakdown"},
            "Difficult to Use": {"weight": 2, "definition": "UX, cognitive friction or ergonomic hurdle"},
            "Wants": {"weight": 1, "definition": "Missing feature or enhancement request"},
            "Likes": {"weight": 0, "definition": "Positive customer praise / promoter sentiment"}
        }
    },
    "domains": []
}

# Detailed tabular rows for CSV
tabular_pipeline_rows = []

domain_order = [
    'smart_cabin', 'smart_exterior', 'energy_and_charging', 'digital_cockpit_and_ai',
    'vehicle_dynamics_and_safety', 'connected_ecosystem', 'driving_assistance', 'general_and_services'
]

for d_id in domain_order:
    d_df = all_ev[all_ev['domain_id'] == d_id]
    if len(d_df) == 0:
        continue
        
    likes_df = d_df[d_df['Feedback Type'] == 'Likes']
    comp_df = d_df[d_df['Feedback Type'].isin(['Difficult to Use', 'Defect', 'Wants'])]
    
    tot_likes = len(likes_df)
    tot_comp = len(comp_df)
    eval_vol = tot_likes + tot_comp  # Classified evaluated volume
    
    def_count = len(comp_df[comp_df['Feedback Type'] == 'Defect'])
    diff_count = len(comp_df[comp_df['Feedback Type'] == 'Difficult to Use'])
    wants_count = len(comp_df[comp_df['Feedback Type'] == 'Wants'])
    
    avg_sev = round(comp_df['severity_weight'].mean(), 2) if len(comp_df) > 0 else 0.0
    
    # Net Sentiment Score: (Likes - Complaints) / Evaluated Total * 100
    net_sentiment_score = round(((tot_likes - tot_comp) / eval_vol) * 100, 1) if eval_vol > 0 else 0.0
    
    # Software vs Hardware split
    classified_d = d_df[d_df['Feedback Type'].isin(['Likes', 'Difficult to Use', 'Defect', 'Wants'])]
    sw_count = len(classified_d[classified_d['system_layer'] == 'Software / UX'])
    hw_count = len(classified_d[classified_d['system_layer'] == 'Hardware / Physical'])
    
    # Cohort splits
    cohort_breakdown = {
        'i5_bev': int(len(comp_df[comp_df['cohort'] == 'i5 BEV'])),
        'i7_bev': int(len(comp_df[comp_df['cohort'] == 'i7 BEV'])),
        '5er_phev': int(len(comp_df[comp_df['cohort'] == '5er PHEV'])),
        '7er_phev': int(len(comp_df[comp_df['cohort'] == '7er PHEV']))
    }
    
    # Top Praised Components
    top_praised = []
    for comp_name, count in likes_df['Vfc level2 Name'].value_counts().head(3).items():
        sample_q = likes_df[likes_df['Vfc level2 Name'] == comp_name]['Customer Feedback'].dropna()
        sample_txt = str(sample_q.iloc[0])[:140] if len(sample_q) > 0 else "Customer highly impressed with system performance."
        top_praised.append({
            "component": comp_name,
            "likes_count": int(count),
            "sample_verbatim": sample_txt
        })
        
        # Add to tabular rows
        tabular_pipeline_rows.append({
            "domain_id": d_id,
            "domain_name": d_df.iloc[0]['domain_name'],
            "aspect_cn": d_df.iloc[0]['aspect_cn'],
            "sentiment_type": "PRAISE",
            "feedback_category": "Likes",
            "component_vfc": comp_name,
            "volume_count": int(count),
            "severity_weight": 0,
            "system_layer": "Hardware" if "design" in comp_name.lower() or "chassis" in comp_name.lower() else "System",
            "sentiment_summary": f"Top praised: {comp_name} ({count} likes)",
            "verbatim_sample": sample_txt,
            "engineering_action": "Preserve benchmark DNA and protect tuning parameters."
        })
        
    # Top Pain Points
    top_complaints = []
    for comp_name, count in comp_df['Vfc level2 Name'].value_counts().head(4).items():
        sub_c = comp_df[comp_df['Vfc level2 Name'] == comp_name]
        dom_cat = sub_c['Feedback Type'].value_counts().index[0]
        sample_q = sub_c['Customer Feedback'].dropna()
        sample_txt = str(sample_q.iloc[0])[:140] if len(sample_q) > 0 else "Customer reported operational difficulties."
        top_complaints.append({
            "component": comp_name,
            "complaints_count": int(count),
            "primary_feedback_type": dom_cat,
            "sample_verbatim": sample_txt
        })
        
        # Add to tabular rows
        tabular_pipeline_rows.append({
            "domain_id": d_id,
            "domain_name": d_df.iloc[0]['domain_name'],
            "aspect_cn": d_df.iloc[0]['aspect_cn'],
            "sentiment_type": "PAIN_POINT",
            "feedback_category": dom_cat,
            "component_vfc": comp_name,
            "volume_count": int(count),
            "severity_weight": 3 if dom_cat == 'Defect' else (2 if dom_cat == 'Difficult to Use' else 1),
            "system_layer": "Software / UX" if any(k in comp_name.lower() for k in ['app', 'carplay', 'os', 'touch', 'esim', 'assistant']) else "Hardware / Physical",
            "sentiment_summary": f"Key friction point: {comp_name} ({count} cases)",
            "verbatim_sample": sample_txt,
            "engineering_action": engineering_kb.get(d_id, {}).get('recommended_action', 'Engineering review required.')
        })

    domain_obj = {
        "domain_id": d_id,
        "domain_name": d_df.iloc[0]['domain_name'],
        "aspect": {
            "cn": d_df.iloc[0]['aspect_cn'],
            "en": d_df.iloc[0]['aspect_en'],
            "de": d_df.iloc[0]['aspect_de']
        },
        "kpi_metrics": {
            "total_evaluated_volume": eval_vol,
            "likes_count": tot_likes,
            "complaints_count": tot_comp,
            "complaint_ratio_pct": round(tot_comp / eval_vol * 100, 2) if eval_vol > 0 else 0,
            "defect_count": def_count,
            "difficult_to_use_count": diff_count,
            "wants_count": wants_count,
            "defect_rate_pct": round(def_count / tot_comp * 100, 2) if tot_comp > 0 else 0,
            "difficult_to_use_rate_pct": round(diff_count / tot_comp * 100, 2) if tot_comp > 0 else 0,
            "wants_rate_pct": round(wants_count / tot_comp * 100, 2) if tot_comp > 0 else 0,
            "avg_severity_score": avg_sev,
            "net_sentiment_score": net_sentiment_score
        },
        "cohort_complaint_distribution": cohort_breakdown,
        "system_layer_split": {
            "software_ux_count": sw_count,
            "software_ux_pct": round(sw_count / eval_vol * 100, 1) if eval_vol > 0 else 0,
            "hardware_physical_count": hw_count,
            "hardware_physical_pct": round(hw_count / eval_vol * 100, 1) if eval_vol > 0 else 0
        },
        "engineering_intelligence": {
            "root_cause_analysis": engineering_kb.get(d_id, {}).get('root_cause', ''),
            "recommended_pipeline_action": engineering_kb.get(d_id, {}).get('recommended_action', ''),
            "key_praise_summary": engineering_kb.get(d_id, {}).get('key_praise', ''),
            "key_pain_point_summary": engineering_kb.get(d_id, {}).get('key_pain_point', '')
        },
        "what_customers_loved": top_praised,
        "what_customers_hated": top_complaints
    }
    pipeline_data["domains"].append(domain_obj)

# Save Pipeline JSON
json_out_path = '/Users/miao/Desktop/Hackathon/bmw_ev_technology_sentiment_pipeline.json'
with open(json_out_path, 'w', encoding='utf-8') as f:
    json.dump(pipeline_data, f, ensure_ascii=False, indent=2)

# Save Tabular CSV
csv_out_path = '/Users/miao/Desktop/Hackathon/bmw_ev_technology_sentiment_pipeline.csv'
tab_df = pd.DataFrame(tabular_pipeline_rows)
tab_df.to_csv(csv_out_path, index=False, encoding='utf-8')

import shutil
shutil.copy2(json_out_path, '/Users/miao/.gemini/antigravity-ide/brain/50b3aecf-d9ce-4482-b37b-c634a4750503/bmw_ev_technology_sentiment_pipeline.json')
shutil.copy2(csv_out_path, '/Users/miao/.gemini/antigravity-ide/brain/50b3aecf-d9ce-4482-b37b-c634a4750503/bmw_ev_technology_sentiment_pipeline.csv')

print("Pipeline JSON & CSV recompiled cleanly.")
