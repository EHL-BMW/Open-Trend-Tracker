/**
 * Plain-language explanation of each Feature Radar term, AI-generated in the chat session
 * (no LLM call in the pipeline). Keys are the Feature Radar feature ids.
 */
export const FEATURE_EXPLANATIONS: Record<string, string> = {
  solid_state:
    "Batteries that replace the liquid electrolyte with a solid one. They promise higher energy density (more range for the same weight), better fire safety and faster charging, but cost and mass production are still unsolved; Chinese makers and CATL are racing to industrialize them around 2027–2030.",
  sodium_ion:
    "Batteries that use abundant sodium instead of lithium. They are cheaper and work better in cold weather, but store less energy, so they suit entry-level cars, commercial vehicles and stationary storage rather than long-range premium EVs.",
  ultra_charging:
    "Very high-power DC charging (4C–6C cell rates up to megawatt chargers) that adds hundreds of kilometres of range in 5–10 minutes. It needs matching batteries, high-voltage architecture and a dense network of high-power chargers.",
  battery_swap:
    "Instead of charging, the empty battery is swapped for a full one at an automated station in a few minutes. NIO runs thousands of such stations in China, and CATL pushes the model for heavy trucks; it also enables battery leasing.",
  v2g:
    "Vehicle-to-grid: a parked EV feeds electricity back into the grid or the home through a bidirectional charger. Owners can earn money by selling power at peak times, and grid operators use fleets of EVs as a virtual power plant.",
  hv_800v:
    "Electrical architecture running at 800 V or more instead of the usual 400 V, usually with silicon-carbide (SiC) power electronics. It allows faster charging, thinner cables and higher efficiency, and is becoming standard even in mid-priced Chinese EVs.",
  urban_noa:
    "Navigate on Autopilot in cities: the car follows the navigation route through urban streets, handling turns, traffic lights and lane changes, while the driver must still supervise. It is the headline driver-assistance feature in China today.",
  e2e_vla:
    "End-to-end driving models replace hand-written rules with one neural network that maps camera and sensor input directly to driving actions. VLA (vision-language-action) models add language understanding so the system can reason about the scene and explain its choices.",
  l3_autonomy:
    "SAE Level 3 conditional automation: in defined conditions the car drives itself and the driver may look away, but must take over when asked. Responsibility shifts to the manufacturer while the system is active, which is why licences and national standards matter.",
  lidar:
    "Laser sensors that measure distances in 3D to build a precise point cloud of the surroundings, also in darkness. Prices have fallen so far that Chinese cars around ¥120k now carry LiDAR for driver assistance.",
  adas_chips:
    "Car makers designing their own driver-assistance processors (e.g. NIO Shenji, XPeng Turing, Li Auto Mach) instead of buying Nvidia or Horizon chips. In-house chips cut cost and let software and hardware be optimized together.",
  robotaxi:
    "Driverless ride-hailing cars without a safety driver. Baidu Apollo Go, Pony.ai, WeRide and now XPeng and Tesla are scaling fleets, and Chinese players are starting tests in Europe and the Middle East.",
  cockpit_llm:
    "Large language models and AI agents built into the infotainment system. They understand free speech, remember preferences and can act across apps and vehicle functions, for example planning a trip, booking parking and adjusting the cabin in one request.",
  central_compute:
    "One central computer that runs both driver assistance and the cockpit (cockpit-driving fusion) instead of many separate control units. It reduces cost and wiring and makes over-the-air updates of the whole car easier.",
  ota:
    "Over-the-air software updates delivered wirelessly to the car. Chinese brands ship frequent updates that add features after purchase, so the car improves over time; regulations such as UN R156 and GB 44496 govern how updates are managed.",
  phone_car_eco:
    "Connected ecosystems let cars work with phones, wearables, smart homes and compatible in-car accessories. Shared software and hardware capabilities allow apps, services and controls to continue across devices, from a phone-to-car handoff to a car-home routine or a modular accessory.",
  smart_seats:
    "Comfort-focused seating and cabin features: zero-gravity reclining seats, massage, heating and ventilation, six- or seven-seat layouts and climate that adapts to each passenger. Chinese family SUVs compete heavily on this rear-seat comfort.",
  active_suspension:
    "Suspension that actively controls each wheel with air springs, adjustable or magnetorheological dampers, or fully active actuators. It reads the road (sometimes with cameras) to keep the body flat and the ride smooth.",
  steer_by_wire:
    "Steering and braking controlled electronically, with no mechanical link between the steering wheel or pedal and the wheels. It enables variable steering ratios and new interior layouts, but needs full redundancy, as recent pedal incidents in China show.",
  giga_casting:
    "Casting large sections of the car body as one aluminium piece with huge die-casting machines, replacing dozens of stamped and welded parts. It cuts weight, cost and factory space, and is part of China's speed and cost advantage.",
  smart_lighting:
    "Intelligent exterior lighting and body features: adaptive matrix and projector headlights that can show signals or images on the road, light signatures, and powered or flush door handles. China plans to ban fully hidden door handles for safety.",
  market_dynamics:
    "Market-level news rather than one technology: price wars, affordability, model launches and regulation that shape demand for electric vehicles in China and change the competitive position of foreign brands.",
};
