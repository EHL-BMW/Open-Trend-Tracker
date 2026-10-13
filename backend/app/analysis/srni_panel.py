"""Auditable SRNI-CAR sales panel and independently sourced feature events.

SRNI-CAR is a peer-reviewed monthly China vehicle-series dataset covering
2016-2022.  The raw CSV is not copied into this repository; the manifest in
``data/external/chinese_pairs`` records the immutable download, checksum,
license, and exact aggregation used for the annual rows below.

Feature labels come from dated launch material, never from the sales outcome.
"""

SRNI_SERIES = "srni_car_monthly_2016_2022"
SRNI_DOWNLOAD = "https://ndownloader.figshare.com/files/42438726?private_link=255ef697e8b7e3115087"
SRNI_PAPER = "https://arxiv.org/abs/2401.05395"
SRNI_SHA256 = "bcc2fd0937a2b55447b1f5386e8d4a75b3305dd946f7f436f94ae28820c807da"

# Annual sums of the monthly ``销量`` field for the exact Chinese ``车系``
# shown in the manifest.  No interpolation or extrapolation is used.
SRNI_SALES = {
    "Geely Boyue": {2016: 109209, 2017: 286163, 2018: 255695, 2019: 232327, 2020: 240811, 2021: 224895, 2022: 75396},
    "GAC Trumpchi GS4": {2016: 329531, 2017: 337330, 2018: 235699, 2019: 103373, 2020: 126640, 2021: 95204, 2022: 77448},
    "Dongfeng Fengshen AX7": {2016: 62741, 2017: 40543, 2018: 45882, 2019: 36918, 2020: 23702, 2021: 21367, 2022: 16791},
    "Changan Eado": {2016: 156372, 2017: 91871, 2018: 118378, 2019: 74941, 2020: 160140, 2021: 84059},
    "Geely Emgrand": {2016: 240194, 2017: 170717, 2018: 241591, 2019: 186436, 2020: 223369, 2021: 183491, 2022: 136773},
    "Geely Emgrand GS": {2016: 60521, 2017: 150484, 2018: 157638, 2019: 103666, 2020: 91551, 2021: 15684},
    "BAIC BJ40": {2016: 9141, 2017: 19329, 2018: 22890, 2019: 20392, 2020: 16989, 2021: 22984, 2022: 21743},
    "BYD Tang NEV": {2016: 31396, 2017: 14547, 2018: 31515, 2019: 29104, 2020: 22762, 2021: 50075, 2022: 148585},
    "Geely Emgrand EV": {2017: 21059, 2018: 5867, 2019: 25737, 2020: 9838, 2021: 25980, 2022: 28101},
    "MG6": {2016: 1933, 2017: 8409, 2018: 94592, 2019: 59069, 2020: 61920, 2021: 40708, 2022: 17738},
    "Chery Tiggo 7": {2016: 34177, 2017: 62330, 2018: 27743, 2019: 14146, 2020: 64991, 2021: 91331, 2022: 53659},
    "Baojun 730": {2016: 370169, 2017: 275227, 2018: 111507, 2019: 98912, 2020: 50240, 2021: 25625, 2022: 5965},
    "Dongfeng Fengguang 580": {2016: 86658, 2017: 176309, 2018: 111003, 2019: 79427, 2020: 46271, 2021: 40327, 2022: 18243},
    "BAIC EC": {2017: 78079, 2018: 87489, 2019: 27354, 2020: 5427, 2021: 317, 2022: 3},
    "Haval H9": {2016: 11504, 2017: 12186, 2018: 14635, 2019: 13434, 2020: 22035, 2021: 18415, 2022: 12444},
    "Soueast DX3": {2016: 12447, 2017: 103173, 2018: 61490, 2019: 11760, 2020: 4056, 2021: 2824, 2022: 2387},
    "Soueast DX7": {2016: 84463, 2017: 40586, 2018: 17089, 2019: 4793, 2020: 2083, 2021: 1044, 2022: 493},
    "Changan Oushang CX70": {2016: 80552, 2017: 55164, 2018: 80293, 2019: 53885, 2020: 31202, 2021: 16242, 2022: 3731},
    "Honda CR-V": {2016: 180319, 2017: 188431, 2018: 143689, 2019: 213306, 2020: 249983, 2021: 200502, 2022: 213935},
    "Honda Accord": {2016: 136245, 2017: 150365, 2018: 174023, 2019: 223706, 2020: 210574, 2021: 201329, 2022: 220771},
    "Toyota Camry": {2016: 100611, 2017: 75237, 2018: 163046, 2019: 185245, 2020: 185140, 2021: 216764, 2022: 242225},
    "BMW 5 Series": {2016: 143779, 2017: 120320, 2018: 138837, 2019: 138003, 2020: 134547, 2021: 149153, 2022: 154016},
    "Mazda CX-5": {2016: 49147, 2017: 49555, 2018: 44256, 2019: 33579, 2020: 33317, 2021: 25363, 2022: 17358},
    "Hyundai ix35": {2016: 71938, 2017: 35087, 2018: 139659, 2019: 131894, 2020: 58277, 2021: 82924, 2022: 64148},
    "Buick Regal": {2016: 69300, 2017: 61619, 2018: 100378, 2019: 123587, 2020: 135877, 2021: 96605, 2022: 77473},
    "Volkswagen Lavida": {2016: 478699, 2017: 461062, 2018: 468956, 2019: 526291, 2020: 417332, 2021: 391355, 2022: 351130},
    "Nissan X-Trail": {2016: 180202, 2017: 184612, 2018: 207951, 2019: 207776, 2020: 175177, 2021: 79449, 2022: 27715},
    "Nissan Teana": {2016: 90279, 2017: 113857, 2018: 112694, 2019: 98549, 2020: 121651, 2021: 162010, 2022: 146012},
    "Volkswagen Passat": {2016: 188214, 2017: 160323, 2018: 179028, 2019: 208057, 2020: 129015, 2021: 114769, 2022: 163532},
    "Volkswagen Bora": {2016: 222279, 2017: 248665, 2018: 245818, 2019: 333528, 2020: 326341, 2021: 246528, 2022: 212702},
    "Audi A6L": {2016: 135730, 2017: 143699, 2018: 153273, 2019: 130140, 2020: 173188, 2021: 150054, 2022: 117679},
    "Volkswagen Sagitar": {2016: 341331, 2017: 327062, 2018: 309902, 2019: 307323, 2020: 299839, 2021: 235607, 2022: 227556},
    "Buick LaCrosse": {2016: 80966, 2017: 99609, 2018: 69709, 2019: 39937, 2020: 54975, 2021: 49875, 2022: 33222},
    "Honda Crider": {2016: 87399, 2017: 98930, 2018: 113108, 2019: 154053, 2020: 113379, 2021: 44216, 2022: 27042},
    "Ford Focus": {2016: 223880, 2017: 172126, 2018: 64902, 2019: 50738, 2020: 34506, 2021: 22857, 2022: 16523},
    "Volvo XC60": {2016: 39374, 2017: 38672, 2018: 50237, 2019: 60132, 2020: 60937, 2021: 58837, 2022: 61027},
    "Kia Sportage": {2016: 78176, 2017: 32514, 2018: 89053, 2019: 85708, 2020: 68750, 2021: 31751, 2022: 19586},
    "Nissan Tiida": {2016: 40245, 2017: 78712, 2018: 59738, 2019: 76195, 2020: 60374, 2021: 51448, 2022: 28194},
    "Hyundai Verna": {2016: 116513, 2017: 42917, 2018: 39870, 2019: 50763, 2020: 38345, 2021: 10723},
    "Changan CS15": {2016: 77882, 2017: 61221, 2018: 27868, 2019: 20533, 2020: 8622, 2021: 13099, 2022: 5214},
    "Maxus G10": {2016: 18514, 2017: 26779, 2018: 24361, 2019: 24022, 2020: 18949, 2021: 19645, 2022: 6964},
    "Mercedes-Benz E-Class": {2016: 57439, 2017: 105210, 2018: 146032, 2019: 157504, 2020: 149900, 2021: 134632, 2022: 123876},
    "Honda Odyssey": {2016: 40029, 2017: 35318, 2018: 45498, 2019: 45516, 2020: 42268, 2021: 43384, 2022: 41282},
    "Geely Vision X6": {2016: 49447, 2017: 126999, 2018: 113309, 2019: 81934, 2020: 83911, 2021: 40747, 2022: 32649},
    "Roewe i6": {2017: 63770, 2018: 67847, 2019: 33285, 2020: 27362, 2021: 11551, 2022: 5567},
    "BMW X1": {2016: 49466, 2017: 90574, 2018: 89929, 2019: 92810, 2020: 91858, 2021: 93920, 2022: 83123},
    "Ford Escort": {2016: 294137, 2017: 285029, 2018: 150360, 2019: 62842, 2020: 33049, 2021: 43001, 2022: 22007},
    "Chevrolet Cavalier": {2016: 50786, 2017: 189409, 2018: 252108, 2019: 101765, 2020: 39261, 2021: 15325, 2022: 13223},
    "Skoda Superb": {2016: 41440, 2017: 40384, 2018: 42234, 2019: 23737, 2020: 8328, 2021: 2129, 2022: 2746},
    "Nissan Murano": {2016: 20537, 2017: 25473, 2018: 27865, 2019: 23547, 2020: 15576, 2021: 12109, 2022: 6442},
    "Skoda Rapid": {2016: 67149, 2017: 64853, 2018: 58849, 2019: 45758, 2020: 30157, 2021: 10150, 2022: 7780},
    "Mercedes-Benz GLC": {2016: 56960, 2017: 111805, 2018: 118350, 2019: 142857, 2020: 160900, 2021: 140049, 2022: 148797},
    "Ford Edge": {2016: 124434, 2017: 108525, 2018: 59892, 2019: 32815, 2020: 25709, 2021: 31091, 2022: 22684},
    "Volkswagen Santana": {2016: 282815, 2017: 277994, 2018: 270024, 2019: 255836, 2020: 175728, 2021: 137336, 2022: 111124},
    "Honda Vezel": {2016: 164076, 2017: 146906, 2018: 141600, 2019: 116825, 2020: 150363, 2021: 173899, 2022: 108961},
    "Dongfeng Fengxing Lingzhi": {2016: 91596, 2017: 75272, 2018: 55611, 2019: 62637, 2020: 59288, 2021: 48669, 2022: 38922},
}


def _event(brand, model, powertrain, nameplate_launch, previous, previous_launch, current, launch, source, features):
    return {
        "brand": brand, "model": model, "powertrain": powertrain,
        "nameplate_launch": nameplate_launch, "previous": previous,
        "previous_launch": previous_launch, "current": current, "launch": launch,
        "source": source, "features": features,
    }


# Every tuple is: detail, normalized feature, subcategory, category, evidence.
SRNI_UPDATES = [
    _event("Geely", "Geely Boyue", "ICE", "2016-03", "2017 Boyue", "2016-03", "2018 Boyue", "2018-03-15",
           "https://www.geelyauto.com.hk/wp-content/uploads/2021/pdf-financial/en/2018-02.pdf", [
               ("GKUI cloud, app ecosystem and driver identity", "New infotainment OS", "cockpit_intelligence", "Digital Cockpit & AI", "Geely's annual report states GKUI debuted in the March 2018 Boyue and lists its cloud, app and driver-ID functions"),
               ("Natural-language speech recognition", "AI voice assistant", "cockpit_intelligence", "Digital Cockpit & AI", "The annual report identifies powerful speech recognition as a GKUI capability"),
               ("Exterior, interior and chassis optimization", "Ride and chassis update", "ride_body_control", "Vehicle Dynamics", "The dated launch account describes styling, equipment and chassis tuning updates"),
           ]),
    _event("GAC", "GAC Trumpchi GS4", "ICE", "2015-04", "Trumpchi GS4", "2015-04", "Qiyun GS4 facelift", "2018-06-16",
           "https://www.prnewswire.com/news-releases/gac-motor-upgrades-best-selling-gs4-to-new-smart-suv-300668670.html", [
               ("AVNT connected system with voice services", "Connected cockpit upgrade", "cockpit_intelligence", "Digital Cockpit & AI", "GAC's launch release documents voice controls, social communication, entertainment and connected services"),
               ("10.1-inch touch display", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "The launch specification documents the new high-resolution display"),
               ("Matrix LED lamps and L-shaped daytime running lights", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "The launch release identifies the new LED lighting design"),
               ("Surround-view parking image system", "Parking assistance", "assisted_driving", "Driving Assistance", "The launch release lists the parking imaging system"),
           ]),
    _event("Dongfeng", "Dongfeng Fengshen AX7", "ICE", "2014-10", "first-generation AX7", "2014-10", "second-generation AX7", "2018-09-25",
           "https://auto.people.com.cn/n1/2018/0926/c1005-30315119.html", [
               ("WindLink 3.0 AI infotainment", "New infotainment OS", "cockpit_intelligence", "Digital Cockpit & AI", "Launch coverage identifies the new AI interaction system"),
               ("Digital cluster and large centre display", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "Launch coverage documents the full-digital instruments and centre screen"),
               ("AEB, BSD, FCW and automatic parking", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "People.cn lists emergency braking, blind-spot monitoring, collision warning and parking assistance"),
               ("1.6THP engine with six-speed automatic", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The launch identifies the new standard engine and transmission combination"),
           ]),
    _event("Changan", "Changan Eado", "ICE", "2012-03", "first-generation Eado", "2012-03", "second-generation Eado", "2018-03",
           "https://disc.static.szse.cn/disc/disk01/finalpage/2019-04-23/e15b6f0d-f3bb-4676-a768-9f6ad83fb5c3.PDF", [
               ("AEB and adaptive cruise control", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "Changan's 2018 annual report lists automatic emergency braking and adaptive cruise for the March launch"),
               ("Six-airbag safety package", "Expanded active and passive safety", "passive_safety", "Smart Cabin", "The annual report lists six airbags and the new five-star safety design"),
               ("1.6 GDI and 1.4 TGDI engine range", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The annual report documents the new-generation engine range"),
           ]),
    _event("Geely", "Geely Emgrand", "ICE", "2009-08", "2017 Emgrand", "2016-10", "2018 Emgrand facelift", "2018-03-09",
           "https://autonews.gasgoo.com/articles/news/all-new-geely-emgrand-hits-market-with-starting-price-of-rmb-69800-70014331", [
               ("Large centre-control display", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "The launch describes the larger centre display and redesigned dashboard"),
               ("New steering wheel, dashboard and cabin materials", "Cabin design and material upgrade", "seating_comfort", "Smart Cabin", "The launch documents the revised steering wheel, console and soft-touch cabin"),
               ("Exterior facelift", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "The launch identifies the all-new exterior treatment"),
           ]),
    _event("Geely", "Geely Emgrand GS", "ICE", "2016-05", "Emgrand GS 1.3T", "2016-05", "2018 Emgrand GS", "2018-04-20",
           "https://www.autohome.com.cn/news/201804/915965.html", [
               ("1.4T engine replacing the 1.3T", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "The launch table identifies the replacement 1.4T engine"),
               ("Three distinct exterior style packages", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "The launch documents three styling families including the new Lingchao variants"),
           ]),
    _event("BAIC", "BAIC BJ40", "ICE", "2014-01", "BJ40L", "2016-04", "BJ40 Plus", "2018-05-27",
           "https://auto.people.com.cn/n1/2018/0515/c1005-29990249.html", [
               ("Digital instrument panel and floating centre display", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "People.cn documents both new displays in the redesigned interior"),
               ("Revised coil-spring suspension and steering", "Ride and chassis update", "ride_body_control", "Vehicle Dynamics", "The launch preview describes the front and rear spring and steering revisions"),
               ("Electronic parking brake with auto-hold", "Brake-by-wire control", "by_wire_controls", "Vehicle Dynamics", "The launch preview lists the electronic parking brake and auto-hold"),
           ]),
    _event("BYD", "BYD Tang NEV", "NEV", "2015-06", "first-generation Tang DM", "2015-06", "second-generation Tang DM", "2018-06-26",
           "https://bydeurope.com/article/253", [
               ("DiLink intelligent connected system", "New infotainment OS", "cockpit_intelligence", "Digital Cockpit & AI", "BYD's launch release identifies DiLink at the all-new Tang market debut"),
               ("Open vehicle sensor and controller platform", "Software-defined vehicle platform", "vehicle_compute", "Digital Cockpit & AI", "BYD describes opening DiLink access to 341 sensors and 66 controllers"),
               ("Second-generation dual-mode plug-in-hybrid system", "New hybrid system", "hybrid_powertrain", "Energy & Charging", "The launch presents the new Tang as BYD's renewed dual-mode flagship"),
           ]),
    _event("Geely", "Geely Emgrand EV", "NEV", "2015-11", "Emgrand EV300", "2017-03", "Emgrand EV450", "2018-03-29",
           "https://auto.people.com.cn/n1/2018/0330/c1005-29898782.html", [
               ("52 kWh battery and over 400 km combined range", "Longer-range battery", "battery_range", "Energy & Charging", "The launch report documents battery capacity, density and the 400-km-plus range"),
               ("ITCS battery thermal-management system", "Battery thermal management", "charging_replenishment", "Energy & Charging", "The launch report identifies the new intelligent battery temperature-control system"),
               ("G-Link infotainment and G-Netlink telematics", "Connected cockpit upgrade", "cockpit_intelligence", "Digital Cockpit & AI", "The launch report lists both connected cabin systems"),
           ]),
    _event("SAIC MG", "MG6", "ICE", "2010-12", "second-generation MG6", "2017-11", "MG6 Connected OTA update", "2018-01-29",
           "https://www.saicmotor.com/chinese/xwzx/xwk/2018/49805.shtml", [
               ("Cloud over-the-air infotainment update", "Whole-vehicle OTA capability", "software_lifecycle", "Connected Ecosystem", "SAIC's dated release documents the cloud-delivered OTA upgrade"),
               ("Dual-zone AI voice control", "AI voice assistant", "cockpit_intelligence", "Digital Cockpit & AI", "SAIC documents passenger voice control, easy wake and contextual commands"),
               ("Remote locking, climate and engine control", "Remote vehicle control", "cross_device_ecosystem", "Connected Ecosystem", "SAIC lists app-based remote vehicle functions"),
           ]),
    _event("Chery", "Chery Tiggo 7", "ICE", "2016-09", "Tiggo 7", "2016-09", "Tiggo 7 Fly", "2018-09-27",
           "https://auto.ifeng.com/guonei/20180927/1239987.shtml", [
               ("FLY exterior and cabin redesign", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "The dated launch identifies the FLY facelift as the updated Tiggo 7"),
               ("1.5T with six-speed dual-clutch or manual", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The launch specification documents the 1.5T transmission choices"),
           ]),
    _event("Baojun", "Baojun 730", "ICE", "2014-07", "Baojun 730 1.5T manual", "2017-01", "Baojun 730 1.5T DCT", "2017-11-20",
           "https://info.xcar.com.cn/201711/news_1992227_1.html?viewtype=all", [
               ("Six-speed wet dual-clutch automatic", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The launch report identifies the first 1.5T wet-DCT variants"),
               ("Electronic parking brake and auto-hold", "Brake-by-wire control", "by_wire_controls", "Vehicle Dynamics", "The launch report lists electronic parking and auto-hold"),
               ("360-degree parking camera", "Parking assistance", "assisted_driving", "Driving Assistance", "The launch equipment list includes surround-view parking"),
           ]),
    _event("Dongfeng", "Dongfeng Fengguang 580", "ICE", "2016-06", "Fengguang 580", "2016-06", "Fengguang 580 Intelligent", "2017-09-24",
           "https://auto.sohu.com/20170925/n514303656.shtml", [
               ("Lin OS 3.0 connected system with voice search", "New infotainment OS", "cockpit_intelligence", "Digital Cockpit & AI", "The dated launch describes the Lin OS remote and voice functions"),
               ("App remote unlock, engine, climate and vehicle location", "Remote vehicle control", "cross_device_ecosystem", "Connected Ecosystem", "The launch lists the app-controlled functions"),
               ("360-degree parking camera", "Parking assistance", "assisted_driving", "Driving Assistance", "The same release documents the surround-view upgrade"),
           ]),
    _event("BAIC", "BAIC EC", "NEV", "2016-11", "BAIC EC200", "2017-08", "BAIC EC3", "2018-08-31",
           "https://autonews.gasgoo.com/articles/ev/new-baic-ec-3-officially-launched-priced-from-rmb-65800-70015109", [
               ("261 km combined electric range", "Longer-range battery", "battery_range", "Energy & Charging", "The launch report documents the EC3's 261-km combined range"),
               ("Battery and motor performance upgrade", "High-voltage powertrain upgrade", "high_voltage_powertrain", "Energy & Charging", "The launch describes the EC3 as a performance and range upgrade to the EC series"),
           ]),
]


# A second independently sourced block broadens both brands and feature
# bundles.  These are model-wide updates or new generations, not arbitrary
# trim duplication.
SRNI_UPDATES.extend([
    _event("Haval", "Haval H9", "ICE", "2014-11", "Haval H9 6AT", "2014-11", "2018 model Haval H9", "2017-05-15",
           "https://auto.sina.com.cn/newcar/x/2017-05-15/detail-ifyfeivp5731146.shtml", [
               ("ZF eight-speed automatic transmission", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The facelift launch documents replacement of the six-speed unit with a ZF eight-speed automatic"),
               ("Seven-inch digital instrument display", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "The launch equipment list identifies the new digital instrument display"),
               ("Lane-departure and blind-spot monitoring", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "The model-year safety specification identifies both systems"),
           ]),
    _event("Soueast", "Soueast DX3", "ICE", "2016-11", "2017 Soueast DX3", "2016-11", "2018 Soueast DX3", "2017-10-17",
           "https://auto.people.com.cn/n1/2017/1017/c1005-29592889.html", [
               ("360-degree parking camera", "Parking assistance", "assisted_driving", "Driving Assistance", "People.cn lists the new surround-view system in the model-year update"),
               ("PM2.5 cabin filtration", "Cabin air quality upgrade", "seating_comfort", "Smart Cabin", "The launch lists the newly added PM2.5 filter"),
               ("LED daytime running lights", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "The launch lists LED daytime running lamps among the update"),
           ]),
    _event("Soueast", "Soueast DX7", "ICE", "2015-07", "Soueast DX7", "2015-07", "Soueast DX7 Prime", "2018-04",
           "https://www.chinanews.com/auto/2018/03-30/8479672.shtml", [
               ("ADAS with AEB", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "The launch preview documents the ADAS suite and automatic emergency braking"),
               ("3D surround-view parking", "Parking assistance", "assisted_driving", "Driving Assistance", "The launch preview identifies the 3D AVM system"),
               ("Ten-inch cluster and centre display", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "The launch preview documents both ten-inch displays"),
               ("1.8T engine with six-speed DCT", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "The model-wide Prime update adds the 1.8T and 6DCT combination"),
           ]),
    _event("Changan Oushang", "Changan Oushang CX70", "ICE", "2016-04", "Oushang CX70", "2016-04", "Oushang CX70T", "2017-01-09",
           "https://auto.people.com.cn/n1/2017/0110/c1005-29010637.html", [
               ("1.5T turbo engine and Aisin six-speed automatic", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "The launch identifies the turbo engine and new automatic transmission"),
               ("Automatic parking", "Parking assistance", "assisted_driving", "Driving Assistance", "The launch specification identifies automatic parking"),
               ("Voice-control system", "AI voice assistant", "cockpit_intelligence", "Digital Cockpit & AI", "The launch specification identifies voice control"),
           ]),
    _event("Honda", "Honda CR-V", "ICE", "2004-04", "fourth-generation CR-V", "2012-02", "fifth-generation CR-V", "2017-07-09",
           "https://www.honda.com.cn/news/20170709.html", [
               ("Honda SENSING safety suite", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "Honda's China launch lists Honda SENSING across the redesigned model"),
               ("Honda CONNECT on a seven-inch display", "Connected cockpit upgrade", "cockpit_intelligence", "Digital Cockpit & AI", "Honda's launch identifies the connected seven-inch system"),
               ("SPORT TURBO and i-MMD hybrid powertrains", "New hybrid system", "hybrid_powertrain", "Energy & Charging", "The China launch introduced turbo and two-motor hybrid versions together"),
           ]),
    _event("Honda", "Honda Accord", "ICE", "1999-03", "ninth-generation Accord", "2013-09", "tenth-generation Accord", "2018-04-16",
           "https://www.honda.com.cn/news/20180417_01.html", [
               ("Honda CONNECT and CarPlay on an eight-inch display", "Connected cockpit upgrade", "cockpit_intelligence", "Digital Cockpit & AI", "Honda's China launch documents the connected floating display"),
               ("SPORT TURBO powertrain family", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "The launch identifies the new turbo powertrain line"),
               ("Honda SENSING driver-assistance suite", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "Honda identifies its driver-assistance suite for the new generation"),
           ]),
    _event("Toyota", "Toyota Camry", "ICE", "2006-06", "seventh-generation Camry", "2011-11", "eighth-generation Camry", "2017-11-16",
           "https://global.toyota/en/newsroom/toyota/25091006.html https://www.toyota.com.cn/upload/news/2018/download/5056.pdf", [
               ("Toyota New Global Architecture platform", "Ride and chassis update", "ride_body_control", "Vehicle Dynamics", "Toyota documents the complete redesign on the TNGA platform and confirms the China launch at the end of 2017"),
               ("New powertrain family including hybrid", "New hybrid system", "hybrid_powertrain", "Energy & Charging", "Toyota's redesign release documents the new conventional and hybrid powertrains"),
               ("New HMI and active-safety systems", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "Toyota's redesign release identifies the HMI and active-safety upgrade"),
           ]),
    _event("BMW", "BMW 5 Series", "ICE", "2003-11", "F18 long-wheelbase 5 Series", "2010-08", "G38 long-wheelbase 5 Series", "2017-06-23",
           "https://www.bmw-brilliance.cn/cn/en/news/news/2017-06-23.html", [
               ("Wireless Apple CarPlay", "Cross-device phone integration", "cross_device_ecosystem", "Connected Ecosystem", "BMW Brilliance identifies the China model as its first business sedan with wireless CarPlay"),
               ("Wireless phone charging", "Wireless device charging", "cross_device_ecosystem", "Connected Ecosystem", "The official launch release lists wireless phone charging"),
               ("China-specific long-wheelbase redesign", "Cabin design and material upgrade", "seating_comfort", "Smart Cabin", "BMW identifies the third-generation long-wheelbase model as developed specifically for Chinese customers"),
           ]),
    _event("Mazda", "Mazda CX-5", "ICE", "2013-08", "first-generation CX-5", "2013-08", "second-generation CX-5", "2017-09-21",
           "https://auto.people.com.cn/n1/2017/0922/c1005-29551731.html", [
               ("Fifth-generation HMI with voice control", "New infotainment OS", "cockpit_intelligence", "Digital Cockpit & AI", "People.cn documents the new voice-operated HMI"),
               ("CarPlay and Baidu CarLife integration", "Cross-device phone integration", "cross_device_ecosystem", "Connected Ecosystem", "The launch lists both phone-integration systems"),
               ("Two-stage reclining rear seats", "Seating flexibility upgrade", "seating_comfort", "Smart Cabin", "The launch documents the new two-stage 28-degree rear backrest"),
           ]),
    _event("Hyundai", "Hyundai ix35", "ICE", "2010-04", "first-generation ix35", "2010-04", "second-generation ix35", "2017-11-15",
           "https://auto.people.com.cn/n1/2017/1111/c1005-29640475-3.html", [
               ("China-specific exterior and cabin redesign", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "The China-market new generation received a complete exterior and interior redesign"),
               ("2.0L engine with six-speed automatic", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "People.cn documents the China launch powertrain"),
           ]),
    _event("Buick", "Buick Regal", "ICE", "1999-04", "previous-generation Regal", "2009-01", "new-generation Regal", "2017-07-21",
           "https://carnewschina.com/2017/07/18/official-china-spec-buick-regal-gs/", [
               ("Nine-speed automatic transmission", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The China-spec launch documents the new nine-speed transmission"),
               ("FlexRide adaptive driving and CDC suspension", "Adaptive suspension and AWD", "ride_body_control", "Vehicle Dynamics", "The official China-spec model information lists FlexRide and continuous damping control"),
               ("Brembo performance braking system", "Brake-by-wire control", "by_wire_controls", "Vehicle Dynamics", "The launch specification identifies the upgraded braking package"),
           ]),
    _event("Volkswagen", "Volkswagen Lavida", "ICE", "2008-06", "second-generation Lavida", "2012-08", "third-generation Lavida Plus", "2018-05",
           "https://www.volkswagen-newsroom.com/en/press-releases/market-overview-compact-notchback-models-are-one-of-volkswagens-key-segments-in-china-5954", [
               ("MQB modular platform", "Ride and chassis update", "ride_body_control", "Vehicle Dynamics", "Volkswagen documents that the third-generation China model moved to MQB"),
               ("China-specific third-generation body", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "Volkswagen identifies the May 2018 model as a China-specific new generation"),
           ]),
])

SRNI_UPDATES.extend([
    _event("Nissan", "Nissan X-Trail", "ICE", "2008-11", "pre-facelift X-Trail", "2014-03", "2017 X-Trail facelift", "2017-04-06",
           "https://global.nissannews.com/en/releases/new-nissan-x-trail-launched-in-china-to-shake-up-fast-growing-suv-segment?origin=channel-NNG1466", [
               ("Intelligent emergency braking and cross-traffic alert", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "Nissan's China launch documents the expanded intelligent-safety suite"),
               ("Intelligent cruise control", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "The official launch identifies distance-maintaining intelligent cruise control"),
               ("Smartphone-connected seven-inch interface", "Cross-device phone integration", "cross_device_ecosystem", "Connected Ecosystem", "Nissan documents the new phone interface and steering-wheel operation"),
               ("V-motion grille and LED lighting redesign", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "Nissan documents the updated grille, lamps and wheels"),
           ]),
    _event("Nissan", "Nissan Teana", "ICE", "2004-09", "sixth-generation Teana", "2013-03", "seventh-generation Teana Altima", "2018-12-18",
           "https://global.nissannews.com/en/releases/all-new-nissan-altima-debuts-at-guangzhou-motor-show-2018?origin=channel-4d8a00a17213f4aa5e4c5f3aa20031b9", [
               ("ProPILOT lane-centering and adaptive cruise", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "Nissan's China debut identifies the first China-market ProPILOT application"),
               ("Variable-compression VC-Turbo engine", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "Nissan documents the world-first production variable-compression engine"),
               ("Advanced drive-assist display", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "The official debut describes the redesigned information display and instrument cluster"),
           ]),
    _event("Volkswagen", "Volkswagen Passat", "ICE", "2000-06", "previous-generation Passat", "2011-04", "new-generation Passat", "2018-10-31",
           "https://www.csvw.com/campaign/mediadownload-allnewpassat-news01.html", [
               ("Traffic-jam assist, lane keeping and adaptive cruise", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "SAIC Volkswagen's launch lists the three driver-assistance systems"),
               ("Digital cluster, HUD and 9.2-inch MIB display", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "The launch documents the 180-degree multi-display cockpit"),
               ("First domestic Passat plug-in-hybrid version", "New hybrid system", "hybrid_powertrain", "Energy & Charging", "The launch introduced the 63-km electric-range PHEV alongside the new generation"),
               ("New EA888 and DQ381 powertrain", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The launch documents the new engine and transmission family"),
           ]),
    _event("Volkswagen", "Volkswagen Bora", "ICE", "2001-08", "third-generation Bora", "2015-03", "fourth-generation Bora", "2018-06-29",
           "https://autonews.gasgoo.com/articles/market-industry/faw-volkswagen-qingdao-base-starts-production-with-debut-of-all-new-bora-70014689", [
               ("MQB modular platform", "Ride and chassis update", "ride_body_control", "Vehicle Dynamics", "FAW-Volkswagen's launch coverage identifies the move to MQB"),
               ("1.5L and 1.4T engine family with DSG option", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The launch coverage documents the new-generation engine and transmission range"),
           ]),
])

# Fourth block (2026-10-13): further SRNI series with a dated launch article each; joint-venture nameplates also serve as controls.
SRNI_UPDATES.extend([
    _event("Audi", "Audi A6L", "ICE", "2005", "A6L C7 (facelifted)", "2012", "all-new A6L (C8), new generation", "2019-01-15",
           "https://auto.ifeng.com/c/7jU5HJ5Nf1c", [
               ("Moves to MLB Evo platform shared with A4L/A8L; larger body, 3024 mm wheelbase", "Ride and chassis update", "ride_body_control", "Vehicle Dynamics", "ifeng (2019-01-15) says the C8 A6L is built on the MLB Evo platform and is larger than the previous generation."),
               ("12.3in digital cluster plus 10.1in MMI touchscreen and 8.6in lower touchscreen for climate/handwriting", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "ifeng lists the three screens and calls them a qualitative upgrade over the previous model."),
               ("Matrix LED headlights, HD matrix lights on top trims, new triangular tail lamps", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "ifeng states matrix LED headlights with HD matrix on high trims and redesigned rear lights."),
               ("First A6L offered with two exterior styles (sport 动感版 and elegant 致雅版)", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "ifeng says this is the first time the A6L offers two exterior designs."),
           ]),
    _event("Volkswagen", "Volkswagen Sagitar", "ICE", "2006-04", "Sagitar 2nd gen (PQ35-based, facelifted)", "2016", "All-new Sagitar (MQB, Jetta Mk7 based, long-wheelbase)", "2019-03-18",
           "https://www.autohome.com.cn/news/201903/931359.html", [
               ("Move to MQB platform, wheelbase +80 mm, multi-link rear suspension standard", "Ride and chassis update", "ride_body_control", "Vehicle Dynamics", "Autohome launch report (2019-03-18) says the new Sagitar moves to MQB with a 2,731 mm wheelbase, 80 mm longer than before."),
               ("Full LCD instrument cluster plus central touchscreen", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "Article lists a full LCD instrument cluster and central screen in the new interior."),
               ("Standard LED headlights and LED taillights", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "Article states LED headlights are standard across the range, with LED taillights."),
               ("Front Assist pre-collision system standard", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "Article says the Front Assist pre-collision system is standard."),
           ]),
    _event("Buick", "Buick LaCrosse", "ICE", "2006", "Third-generation LaCrosse (20T/28T, 30H hybrid)", "2016-03", "2019款 LaCrosse mid-cycle facelift (incl. LaCrosse Avenir)", "2019-03-28",
           "https://www.autohome.com.cn/news/201903/932181.html", [
               ("Larger wing-shaped grille (diamond-weave on Avenir), redesigned tail with new lamps, dual exhausts and integrated spoiler", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "Autohome (2019-03-29) describes the enlarged front grille and redesigned rear as the facelift's exterior changes."),
               ("Buick eConnect 2.0 with standard 8-inch HD touchscreen, new UI and four personalised user accounts", "Connected cockpit upgrade", "cockpit_intelligence", "Digital Cockpit & AI", "Autohome says the car carries the newly upgraded eConnect 2.0 and a standard 8-inch touchscreen with a new UI."),
               ("OTA remote updates of OnStar module and infotainment", "Whole-vehicle OTA capability", "software_lifecycle", "Connected Ecosystem", "Autohome states the car supports remote OTA upgrades of the OnStar module and head unit."),
               ("New 2.0T turbo with cylinder deactivation (240 hp), 9-speed automatic, China 6", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "Autohome says the car first launches with a new 2.0T variable-cylinder turbo engine paired with a 9-speed automatic."),
           ]),
    _event("Honda", "Honda Crider", "ICE", "2013-06", "First-generation Crider 1.8L", "2013-06", "All-new second-generation Crider (全新凌派, 180Turbo)", "2018-09-27",
           "https://www.autohome.com.cn/news/201809/922903.html", [
               ("1.8L NA engine replaced by P10A3 1.0T three-cylinder turbo (122 hp, 173 N·m) with 6MT or CVT; CVT gets auto start-stop", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "Autohome (2018-09-27) says the whole range switched to the P10A3 1.0T inline-three turbo engine."),
               ("Honda SENSING on top two trims: ACC, lane keeping assist, collision-mitigation braking, traffic sign recognition", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "Autohome says the two higher trims offer Honda SENSING with adaptive cruise, lane keeping and pre-collision braking."),
               ("7-inch digital instrument display and 6-inch floating centre touchscreen on higher trims", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "Autohome lists a 7-inch LCD instrument display and 6-inch floating touchscreen on higher trims."),
               ("Accord-inspired exterior with U-shaped grille, full-LED headlights, fastback body; 80 mm longer wheelbase", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "Autohome says styling borrows the new Accord design language with full-LED headlights and an 80 mm longer wheelbase."),
           ]),
    _event("Ford", "Ford Focus", "ICE", "2005", "Focus 2nd-gen-based third generation (2018 model year)", "2017-11", "All-new fourth-generation Focus (Changan Ford)", "2018-11-08",
           "https://auto.ifeng.com/c/7haqJ4Q7dmS", [
               ("Co-Pilot360-type ADAS: AEB, ACC, lane keeping, lane-centering, traffic sign recognition, FCW", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "The ifeng launch article (2018-11-06) lists AEB, adaptive cruise, lane keeping and lane-centering assist on the new Focus."),
               ("One-touch parking assist", "Parking assistance", "assisted_driving", "Driving Assistance", "Article lists one-touch automatic parking assist among new-car equipment."),
               ("New 1.0T/1.5L/1.5T three-cylinder engines with 8-speed automatic", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "Article states 1.0T 127hp, 1.5L 122hp and 1.5T 184hp three-cylinder engines with an 8AT."),
               ("Rotary E-shifter, EPB with auto hold", "Brake-by-wire control", "by_wire_controls", "Vehicle Dynamics", "Article lists rotary shifter, electronic parking brake and auto hold."),
           ]),
    _event("Volvo", "Volvo XC60", "ICE", "2009-04", "First-generation XC60 (Chengdu-built domestic version)", "2014-11", "All-new second-generation XC60 (SPA platform, domestic, T4/T5/T8, 36.99-60.99万)", "2017-12-20",
           "https://auto.sohu.com/20171220/n525839262.shtml", [
               ("T8 twin-charged 2.0T plug-in hybrid, 407 hp / 640 Nm", "New hybrid system", "hybrid_powertrain", "Energy & Charging", "Sohu 2017-12-20 launch report lists a T8 plug-in hybrid ('双增压插电混动') alongside T4/T5 petrol versions."),
               ("12.3-inch digital instrument cluster plus 9-inch central touchscreen", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "Launch report lists a 12.3in full digital cluster and 9in vertical central touchscreen."),
               ("Head-up display", "Head-up display (HUD/AR-HUD)", "displays_hmi", "Digital Cockpit & AI", "Launch report lists a HUD together with the digital cluster."),
               ("Bowers & Wilkins audio (by trim)", "Premium audio system", "cabin_entertainment", "Smart Cabin", "Launch report says Bowers & Wilkins audio is available depending on trim."),
           ]),
    _event("Kia", "Kia Sportage", "ICE", "2010", "智跑 (SL) facelift, 2015-2017款", "2014-09", "全新一代智跑 (2018款, China redesign)", "2018-04-16",
           "https://www.autohome.com.cn/news/201804/915802.html", [
               ("Restyled body with squarer lines and large 'big-mouth' grille; height +35 mm", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "Autohome (2018-04-17) says the styling changed substantially, with a large grille and revised dimensions."),
               ("Four-element LED fog lamps and LED tail lamps", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "Autohome highlights the grid of four LED fog lamps and the new LED tail-lamp structure."),
               ("8in floating screen with Baidu voice interaction", "AI voice assistant", "cockpit_intelligence", "Digital Cockpit & AI", "Autohome lists an 8-inch floating screen whose system supports Baidu voice interaction."),
               ("Forward collision warning, lane departure warning/keeping and fatigue reminder on some trims", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "Autohome lists FCW, lane departure warning/keeping and driver fatigue reminder on some versions."),
           ]),
    _event("Nissan", "Nissan Tiida", "ICE", "2005", "Tiida (C13, launched 2016)", "2016-05", "2019 model-year Tiida with 智行+ connected system", "2018-11-15",
           "https://www.autohome.com.cn/news/201811/925215.html", [
               ("智行+ connected system: Amap online navigation, 4G Wi-Fi hotspot, 10 years free data", "Connected cockpit upgrade", "cockpit_intelligence", "Digital Cockpit & AI", "Autohome (2018-11-15) says the 2019 Tiida adds the 智行+ connected system with online Amap maps and 4G Wi-Fi."),
               ("iFlytek speech recognition", "AI voice assistant", "cockpit_intelligence", "Digital Cockpit & AI", "Article states the system uses iFlytek speech recognition."),
               ("Phone app to check vehicle status and locate the car", "Remote vehicle control", "cross_device_ecosystem", "Connected Ecosystem", "Article says owners can monitor status and locate the car via a phone app."),
           ]),
    _event("Hyundai", "Hyundai Verna", "ICE", "2010", "First-generation Verna (2014 mid-cycle facelift)", "2014-03", "All-new second-generation Verna", "2017-09-19",
           "https://www.autohome.com.cn/news/201709/907265.html", [
               ("Smart connected system on upper trims (chat, navigation, apps, payment, services)", "Connected cockpit upgrade", "cockpit_intelligence", "Digital Cockpit & AI", "Autohome (2017-09-19) says higher trims get a smart connected system with six function groups."),
               ("Apple CarPlay and Baidu CarLife support", "Cross-device phone integration", "cross_device_ecosystem", "Connected Ecosystem", "Article states the new Verna offers CarPlay and CarLife with USB ports."),
               ("Fluid Sculpture 2.0 styling with new trapezoid chrome grille and headlamps", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "Article describes Fluid Sculpture 2.0 design with an inverted-trapezoid chrome grille and sharper headlamps."),
           ]),
])

# Fifth block (2026-10-13): Chinese-brand and premium SRNI series with dated launch material.
SRNI_UPDATES.extend([
    _event("Changan", "Changan CS15", "ICE", "2016-04", "CS15 (first version, 1.5L, launched 2016-04, sold through 2018)", "2016-04", "New CS15 facelift (2019款, 1.5L 5MT/5DCT, 5.59-7.89万)", "2019-03-21",
           "https://www.autohome.com.cn/news/201903/931466.html", [
               ("Full-LED headlights (second-highest trim and above) with new 蝶翼式 family front face", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "Autohome 2019-03-21 launch report says the facelift adopts the butterfly-wing family face and adds full-LED headlights on upper trims."),
               ("LCD instrument cluster (液晶仪表盘)", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "Launch report lists a new LCD instrument cluster in the updated, family-style interior."),
               ("in Call 3.0 infotainment system", "New infotainment OS", "cockpit_intelligence", "Digital Cockpit & AI", "Launch report states the infotainment now runs Changan's in Call 3.0 system."),
               ("Panoramic sunroof", "Panoramic sunroof", "seating_comfort", "Smart Cabin", "Launch report lists a panoramic sunroof among the newly added equipment."),
           ]),
    _event("SAIC Maxus", "Maxus G10", "ICE", "2014-03", "G10 (2014 launch, 2016 model years)", "2014-03", "2018款 G10 Plus (renamed update with Alibaba Zebra system)", "2017-09",
           "https://www.saicmotor.com/chinese/xwzx/xwk/2017/49014.shtml", [
               ("Alibaba Zebra (斑马) connected system with 10.1-inch screen and voice navigation/control", "New infotainment OS", "cockpit_intelligence", "Digital Cockpit & AI", "SAIC Motor release (2017-08-22) says the G10 Plus gets the Alibaba Zebra smart connected system with a 10.1-inch screen and voice control."),
               ("Smartphone app remote unlocking, vehicle locating and maintenance reminders", "Remote vehicle control", "cross_device_ecosystem", "Connected Ecosystem", "The SAIC release lists app functions including remote unlocking and vehicle location as part of the new Zebra connectivity."),
               ("ESP and rear camera made standard plus four additional airbags", "Expanded active and passive safety", "passive_safety", "Smart Cabin", "The SAIC release states ESP stability control and reversing camera are standard and four airbags were added."),
               ("Upgraded interior panel and steering-wheel materials; brown seat with black interior option on upper trims", "Cabin design and material upgrade", "seating_comfort", "Smart Cabin", "The SAIC release says interior panel and steering wheel materials were upgraded across the range, with a new brown/black colour scheme."),
           ]),
    _event("Mercedes-Benz", "Mercedes-Benz E-Class", "ICE", "2005", "W213 E-Class L (E200 L / E300 L / E320 L)", "2016-08", "新款E级 2019款 powertrain update (E 260 L / E 300 L / E 350 L, M264 + 48V)", "2019-03",
           "https://auto.news18a.com/news/storys_131112.html", [
               ("New 1.5T and 2.0T engines (135-220 kW) with 9-speed automatic, meeting China 6; E200 L renamed E 260 L, E320 L renamed E 350 L", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "news18a (2019-03-13) says the new E-Class gets three new powertrains (1.5T+48V, 2.0T, 2.0T+48V) meeting China 6."),
               ("48V mild-hybrid system on 1.5T and 2.0T versions", "New hybrid system", "hybrid_powertrain", "Energy & Charging", "news18a lists 1.5T+48V轻混 and 2.0T+48V轻混 among the new powertrains."),
               ("Tire pressure monitoring added", "Expanded active and passive safety", "passive_safety", "Smart Cabin", "news18a states the car 增配了胎压监测 (added tire pressure monitoring)."),
           ]),
    _event("Honda", "Honda Odyssey", "ICE", "2002", "Fifth-generation Odyssey (RC), pre-facelift", "2014-07", "Fifth-generation Odyssey mid-cycle facelift (新款奥德赛)", "2018-07-15",
           "https://www.autohome.com.cn/news/201807/919526.html", [
               ("Redesigned front end (four-bar grille linked to headlamps, revised bumper), new 17-inch multi-spoke wheels, new flat rear spoiler", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "Autohome (2018-07-09) says the front end changes significantly with new grille bars, adjusted bumper and new 17-inch wheels."),
               ("Redesigned LED fog-lamp area with five dot-style elements", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "Autohome says the fog-lamp area is redesigned with five dot-style LED elements."),
               ("Dual sunroof added for the first time", "Panoramic sunroof", "seating_comfort", "Smart Cabin", "Autohome says the facelift adds a dual sunroof design for the first time (首次增加双天窗设计)."),
           ]),
    _event("Geely", "Geely Vision X6", "ICE", "2016-08", "Vision SUV (远景SUV) 1.8L/1.3T launch version", "2016-08", "New Vision SUV facelift (新远景SUV, 1.4T + 8CVT)", "2018-06-01",
           "https://auto.news18a.com/news/storys_122708.html", [
               ("New Geely 1.4T turbo engine (98 kW, 215 Nm) with CVT, plus new 1.8L", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "Wangtongshe (2018-05-23) says the refreshed Vision SUV launching June 1 gets a new 1.4T turbo and a 1.8L engine."),
               ("Redesigned grille, sharper headlamps, new bumpers, vertical LED taillights", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "Article describes a new water-ripple grille, sharper headlamps, new bumpers and vertical LED taillights."),
               ("Electronic handbrake buttons in redesigned console", "Brake-by-wire control", "by_wire_controls", "Vehicle Dynamics", "Article notes electronic handbrake buttons in the new interior layout."),
           ]),
    _event("Roewe", "Roewe i6", "ICE", "2017", "Roewe i6 2018 model year (1.0T/1.5T)", "2017-11", "Roewe i6 PLUS facelift", "2019-03-29",
           "https://www.autohome.com.cn/advice/201906/936970.html", [
               ("1.6L naturally aspirated engine with CVT replaces 1.0T three-cylinder and DCT", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "Autohome (2019-06-06) says the 1.6L NA engine and CVT replace the previous 1.0T three-cylinder and dual-clutch."),
               ("Revised front: honeycomb grille, Y-shaped lower bumper accents", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "Article lists updated details such as Y-shaped lower bumper accents and a honeycomb grille."),
           ]),
    _event("BMW", "BMW X1", "ICE", "2012-03", "2018 model-year X1 long-wheelbase (F49)", "2017-07", "2019 model-year X1 (F49, equipment update)", "2018-10-15",
           "http://auto.sina.com.cn/newcar/x/2018-10-16/detail-ihmhafir9973985.shtml", [
               ("8.8-inch centre screen with new-generation HMI on xDrive20Li 尊享型", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "Sina (2018-10-16) says xDrive20Li 尊享型 adds an 8.8-inch centre screen with new-generation HMI."),
               ("Rear-view camera added to entry sDrive18Li 时尚型; optional parking assist package", "Parking assistance", "assisted_driving", "Driving Assistance", "Article says the entry trim gains a reversing camera and a new optional package with parking assist."),
               ("Optional entertainment package with wireless Apple CarPlay", "Cross-device phone integration", "cross_device_ecosystem", "Connected Ecosystem", "Article lists a new 6,500-yuan entertainment package including wireless Apple CarPlay."),
           ]),
])

# Sixth block (2026-10-13): model-year and powertrain updates of long-running SRNI series; thinner bundles are kept as documented.
SRNI_UPDATES.extend([
    _event("Ford", "Ford Escort", "ICE", "2014-11", "2017款 Escort minor update (8-inch screen)", "2017-03", "新福睿斯 facelift (2019款)", "2018-10-22",
           "https://auto.sina.cn/newcar/x/2018-10-22/detail-ifxeuwws7014390.d.html", [
               ("1.0L EcoBoost three-cylinder turbo (94 kW, EcoBoost 125) added alongside 1.5L; new 6-speed manual", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "Sina (2018-10-22) says the facelift offers 1.5L and 1.0T engines, the EcoBoost 125 top trim at 11.98万."),
               ("Redesigned rounder headlamps with lens low/high beam, LED daytime running lights and automatic headlights", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "Article lists rounder headlamps with integrated lenses, LED DRL and auto headlights as part of the equipment upgrade."),
               ("New front face with rounder upper grille, new lower grille, chrome door trim, 17-inch wheels (was 16), shark-fin antenna", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "Article states the grille became rounder, wheels grew from 16 to 17 inches and a shark-fin antenna was added."),
           ]),
    _event("Chevrolet", "Chevrolet Cavalier", "ICE", "2016-09", "科沃兹 1.5L (MT/AT), launched 2016", "2016-09", "科沃兹 325T (1.0T three-cylinder + 6-speed wet DCT, 10.49-11.49万)", "2018-03",
           "https://www.autohome.com.cn/news/201803/914836.html", [
               ("1.0T three-cylinder turbo engine, 120 hp / 165 Nm, 5.0 L/100km", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "Autohome 2018-03-27: the biggest change is 'carrying a 1.0T three-cylinder engine' in the new 325T versions."),
               ("6-speed wet dual-clutch transmission paired with the new 1.0T", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "Same article states the 1.0T is matched to a 6-speed wet dual-clutch gearbox; exterior/interior unchanged."),
           ]),
    _event("Skoda", "Skoda Superb", "ICE", "2013-08", "Superb third generation (China 5)", "2015-10", "速派 国六版 (China 6 version)", "2019-02-27",
           "https://www.autohome.com.cn/news/201902/930398.html", [
               ("1.8T TSI 330 replaced by 2.0T low-power TSI 330 (186 hp, 320 N·m)", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "Autohome (2019-02-27) says the China 6 Superb swaps the 1.8T TSI330 for a 2.0T low-power TSI330."),
               ("Engines upgraded from China 5 to China 6 emissions standard", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "Autohome (2019-02-27) reports the China 6 emissions version of the Superb as officially launched in six variants."),
           ]),
    _event("Nissan", "Nissan Murano", "ICE", "2011-09", "2017款 楼兰 (2.5L / 2.5 S/C HEV)", "2017-02", "2019款 楼兰 (model-year update)", "2018-07",
           "https://auto.sina.cn/newcar/x/2018-07-27/detail-ihfvkitx5354013.d.html?vt=4", [
               ("Adds Dongfeng Nissan '智行+' connected system: navigation, vehicle location, remote monitoring, status check, in-car Wi-Fi hotspot with 10 years free basic data", "Connected cockpit upgrade", "cockpit_intelligence", "Digital Cockpit & AI", "Sina auto (2018-07-27) says the car adds the latest '智行+' connected system with Wi-Fi hotspot and remote monitoring."),
               ("Voice control via 智行+ covering navigation, entertainment, weather and communication", "AI voice assistant", "cockpit_intelligence", "Digital Cockpit & AI", "Sina lists voice control as a function of the newly added 智行+ system."),
           ]),
    _event("Skoda", "Skoda Rapid", "ICE", "2013", "2018款 昕锐 1.4L/1.6L", "2017-10", "2019款 昕锐 1.5L (model-year update)", "2018-09-17",
           "https://www.autohome.com.cn/news/201809/922575.html", [
               ("Whole range switches to EA211 1.5L NA engine (110 hp, 150 N·m) with 5MT/6AT, replacing 1.4L/1.6L; start-stop standard", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "Autohome (2018-09-17) says '新车全系换装了1.5L发动机' and that exterior and interior are unchanged."),
           ]),
    _event("Mercedes-Benz", "Mercedes-Benz GLC", "ICE", "2015-11", "GLC SUV standard wheelbase (2017款/2018款), first launched 2015-11", "2015-11", "GLC L long-wheelbase version (GLC 260 L / 300 L 4MATIC)", "2018-10-17",
           "https://www.autohome.com.cn/news/201810/923778.html", [
               ("Wheelbase lengthened by 100 mm to 2973 mm; length +104 mm, height -16 mm", "Ride and chassis update", "ride_body_control", "Vehicle Dynamics", "Autohome 2018-10-17 (launch evening) says the GLC L wheelbase is 100mm longer than the current model; styling and interior largely unchanged."),
               ("Visibly larger rear legroom; rear door storage tray with two dividers", "Seating flexibility upgrade", "seating_comfort", "Smart Cabin", "Same article: lengthening gives clearly more rear legroom and the rear door tray gains an extra divider."),
           ]),
    _event("Ford", "Ford Edge", "ICE", "2015", "2017款 Edge (EcoBoost 245 / 2.7T V6)", "2016-07", "2018款 Edge model-year update", "2017-10",
           "https://www.autohome.com.cn/news/201710/907965.html", [
               ("Panoramic sunroof added on EcoBoost 245 2WD 铂锐型 7-seat", "Panoramic sunroof", "seating_comfort", "Smart Cabin", "Autohome (2017-10-12) says the EcoBoost 245 2WD 铂锐型 7-seat 新增全景天窗."),
               ("Auto start-stop made standard across EcoBoost 245 range", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "Autohome says the EcoBoost 245 versions will get auto start-stop as standard across the range."),
           ]),
    _event("Volkswagen", "Volkswagen Santana", "ICE", "1983", "2016/2017款 Santana 1.4L/1.6L", "2015-12", "Santana 1.5L (EA211) powertrain update", "2018-08",
           "https://www.kingautos.net/218837", [
               ("New EA211 1.5L naturally aspirated engine (110 hp) with 5MT/6AT replaces the 1.4L and 1.6L units", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "Article (2018-08-14) says SAIC VW announced in early August 2018 that the EA211 1.5L NA engine replaces the old 1.4L/1.6L, 4 versions RMB 88,900-113,800."),
           ]),
    _event("Honda", "Honda Vezel", "ICE", "2014-10", "2017款 Binzhi (incl. 1.8L CVT 智享型 added 2017-03)", "2016", "2018款 缤智 (model-year update, new 1.5L CVT 科技精英型)", "2017-09-10",
           "https://www.autohome.com.cn/news/201709/906823.html", [
               ("LED headlamp elements with lenses and LED tail-lamp strip on the 1.5L trim", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "Autohome (2017-09-10) says the new 1.5L trim gets LED lens headlamp units and a revised tail lamp with LED strip."),
           ]),
    _event("Dongfeng", "Dongfeng Fengxing Lingzhi", "ICE", "2001", "2018款 Lingzhi M3L/M5L 1.6L", "2017-10", "Lingzhi M3L/M5L 2.0L versions (4 new 2.0L models)", "2018-09",
           "https://www.autohome.com.cn/news/201809/922102.html", [
               ("New 2.0L naturally aspirated engine (147 hp) with 6-speed manual; M3L previously offered only with 1.6L", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "Autohome (2018-09-04) says the four new 2.0L models use a 147 hp 2.0L NA engine with 6MT, and the M3L previously had only a 1.6L."),
           ]),
])
