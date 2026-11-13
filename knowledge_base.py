"""
KNOWLEDGE BASE - Car Fault Diagnosis Expert System
---------------------------------------------------
Contains:
  * SYMPTOMS : every fact the user can report  (key -> (category, description))
  * RULES    : 78 weighted IF-THEN rules       (symptoms + weights -> fault + fix)

Each rule's weights add up to 1.0, so
    confidence = (sum of weights of the reported symptoms) x 100
"""

# settings 
THRESHOLD = 40          # a fault is shown only if confidence >= 40 %
MULTI_THRESHOLD = 50    # confidence needed for a 2nd/3rd independent fault
CRITICAL_ALERT = 60     # confidence at which a Critical fault triggers a warning

SEVERITY_RANK = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

CATEGORIES = [
    "Engine & Fuel",
    "Cooling",
    "Brakes",
    "Steering, Suspension & Tires",
    "Transmission & Clutch",
    "Electrical & Battery",
    "Exhaust & Emissions",
    "Climate Control",
    "Hybrid & Electric Drivetrain",
]

#  symptoms (facts) -
SYMPTOMS = {
    # ---- Engine & Fuel ----
    "wont_start":        ("Engine & Fuel", "Engine does not start at all"),
    "cranks_no_start":   ("Engine & Fuel", "Engine cranks but will not start"),
    "hard_start":        ("Engine & Fuel", "Engine is hard / slow to start"),
    "rough_idle":        ("Engine & Fuel", "Engine shakes or idles roughly"),
    "stalling":          ("Engine & Fuel", "Engine stalls while driving or at stops"),
    "sputtering":        ("Engine & Fuel", "Engine sputters or jerks while driving"),
    "hesitation":        ("Engine & Fuel", "Hesitation when pressing the accelerator"),
    "loss_power":        ("Engine & Fuel", "Car feels weak / slow to accelerate"),
    "knocking":          ("Engine & Fuel", "Knocking or tapping noise from the engine"),
    "oil_light":         ("Engine & Fuel", "Oil pressure warning light is on"),
    "check_engine":      ("Engine & Fuel", "Check-engine light is on"),
    "poor_mileage":      ("Engine & Fuel", "Fuel economy has dropped"),
    "fuel_smell":        ("Engine & Fuel", "Strong petrol smell around the car"),
    "fuel_puddle":       ("Engine & Fuel", "Fuel is dripping under the car"),
    "oil_leak":          ("Engine & Fuel", "Oil spots or puddles under the engine"),
    "burning_oil_smell": ("Engine & Fuel", "Burning-oil smell from the engine bay"),
    "high_idle":         ("Engine & Fuel", "Engine idles too high (revs stay up)"),
    "rattle_timing":     ("Engine & Fuel", "Rattling / ticking from the front of the engine"),
    "hiss_engine":       ("Engine & Fuel", "Hissing sound from the engine bay"),
    "backfire":          ("Engine & Fuel", "Popping or backfiring sounds"),

    #  Cooling 
    "temp_high":         ("Cooling", "Temperature gauge is high (overheating)"),
    "steam":             ("Cooling", "Steam coming from under the hood"),
    "coolant_low":       ("Cooling", "Coolant level is low"),
    "coolant_leak":      ("Cooling", "Coloured liquid puddle under the car"),
    "sweet_smell":       ("Cooling", "Sweet smell from the engine or cabin"),
    "temp_swings":       ("Cooling", "Temperature gauge fluctuates up and down"),
    "heater_cold":       ("Cooling", "Heater blows cold air"),
    "temp_low":          ("Cooling", "Engine never warms up (gauge stays low)"),
    "fan_not_running":   ("Cooling", "Radiator fan does not spin when hot"),
    "whine_pump":        ("Cooling", "Whining / grinding at the front of the engine"),
    "milky_oil":         ("Cooling", "Milky / creamy oil on the dipstick"),
    "gurgling":          ("Cooling", "Gurgling noise from the dashboard"),

    # ---- Brakes ----
    "squeal_brakes":     ("Brakes", "Brakes squeal when pressed"),
    "grinding_brakes":   ("Brakes", "Grinding noise when braking"),
    "long_stopping":     ("Brakes", "Car takes longer to stop"),
    "brake_light":       ("Brakes", "Brake warning light is on"),
    "pedal_vibration":   ("Brakes", "Brake pedal pulsates when braking"),
    "soft_pedal":        ("Brakes", "Brake pedal feels soft or spongy"),
    "hard_pedal":        ("Brakes", "Brake pedal feels very hard"),
    "pedal_sinks":       ("Brakes", "Brake pedal slowly sinks to the floor"),
    "brake_fluid_low":   ("Brakes", "Brake fluid level is low"),
    "brakes_serviced":   ("Brakes", "Brakes were serviced recently"),
    "brake_pull":        ("Brakes", "Car pulls to one side when braking"),
    "brake_drag":        ("Brakes", "Burning smell / one wheel very hot after driving"),
    "hiss_pedal":        ("Brakes", "Hissing sound when pressing the brake"),
    "abs_light":         ("Brakes", "ABS warning light is on"),
    "wheel_lock":        ("Brakes", "Wheels lock up when braking on wet roads"),

    # ---- Steering, Suspension & Tires ----
    "vibration_wheel":   ("Steering, Suspension & Tires", "Steering wheel vibrates at speed"),
    "vibration_seat":    ("Steering, Suspension & Tires", "Vibration felt in the seat / floor"),
    "pulls_side":        ("Steering, Suspension & Tires", "Car pulls to one side while driving"),
    "uneven_tires":      ("Steering, Suspension & Tires", "Tires are wearing unevenly"),
    "steering_off_center": ("Steering, Suspension & Tires", "Steering wheel is off-centre when driving straight"),
    "bouncy_ride":       ("Steering, Suspension & Tires", "Car bounces a lot over bumps"),
    "nose_dive":         ("Steering, Suspension & Tires", "Car nose-dives when braking"),
    "clunk_bumps":       ("Steering, Suspension & Tires", "Clunking noise over bumps"),
    "steering_play":     ("Steering, Suspension & Tires", "Steering feels loose (too much play)"),
    "wandering":         ("Steering, Suspension & Tires", "Car wanders on a straight road"),
    "whine_steering":    ("Steering, Suspension & Tires", "Whining noise when turning the wheel"),
    "steering_heavy":    ("Steering, Suspension & Tires", "Steering is heavy / stiff"),
    "ps_leak":           ("Steering, Suspension & Tires", "Fluid leak near the steering system"),
    "cv_click":          ("Steering, Suspension & Tires", "Clicking noise when turning sharply"),
    "grease_splatter":   ("Steering, Suspension & Tires", "Grease splattered inside the wheel area"),
    "low_tire":          ("Steering, Suspension & Tires", "A tire keeps losing air"),
    "tire_bulge":        ("Steering, Suspension & Tires", "Bulge or cut visible on a tire"),
    "hum_wheel":         ("Steering, Suspension & Tires", "Humming / roaring noise that rises with speed"),

    #  Transmission & Clutch 
    "clutch_slip":       ("Transmission & Clutch", "Clutch slips (revs rise, car does not speed up)"),
    "clutch_hard":       ("Transmission & Clutch", "Clutch pedal is hard or sticky"),
    "clutch_soft":       ("Transmission & Clutch", "Clutch pedal goes soft / stays on the floor"),
    "burning_clutch_smell": ("Transmission & Clutch", "Burning smell from clutch / transmission"),
    "trans_fluid_leak":  ("Transmission & Clutch", "Red / brown fluid under the car"),
    "hard_shift":        ("Transmission & Clutch", "Hard or delayed gear shifts"),
    "gear_slip":         ("Transmission & Clutch", "Gears slip or revs jump without speed"),
    "trans_whine":       ("Transmission & Clutch", "Whining / humming noise in gear"),
    "stuck_gear":        ("Transmission & Clutch", "Car will not go into gear"),
    "grind_gear":        ("Transmission & Clutch", "Grinding noise when changing gears"),
    "shudder":           ("Transmission & Clutch", "Shudder at 40-60 km/h"),
    "diff_hum":          ("Transmission & Clutch", "Humming from the front / rear axle"),
    "clunk_gear":        ("Transmission & Clutch", "Clunk when shifting or on / off throttle"),

    #  Electrical & Battery 
    "clicking":          ("Electrical & Battery", "Clicking sound when turning the key"),
    "dim_lights":        ("Electrical & Battery", "Headlights / dashboard are dim or weak"),
    "battery_light":     ("Electrical & Battery", "Battery warning light is on"),
    "slow_crank":        ("Electrical & Battery", "Engine cranks slowly"),
    "corroded_terminals": ("Electrical & Battery", "White / green corrosion on battery terminals"),
    "battery_old":       ("Electrical & Battery", "Battery is more than 3-4 years old"),
    "electrics_flaky":   ("Electrical & Battery", "Windows / radio / lights work intermittently"),
    "grinding_start":    ("Electrical & Battery", "Grinding noise when starting the engine"),
    "silent_key":        ("Electrical & Battery", "Complete silence when turning the key"),
    "blown_fuses":       ("Electrical & Battery", "Fuses keep blowing"),
    "burning_wire_smell": ("Electrical & Battery", "Burning plastic / wire smell"),

    # Exhaust & Emissions 
    "white_smoke":       ("Exhaust & Emissions", "White smoke from the exhaust"),
    "black_smoke":       ("Exhaust & Emissions", "Black smoke from the exhaust"),
    "blue_smoke":        ("Exhaust & Emissions", "Blue / grey smoke from the exhaust"),
    "loud_exhaust":      ("Exhaust & Emissions", "Exhaust is unusually loud"),
    "rotten_egg":        ("Exhaust & Emissions", "Rotten-egg (sulfur) smell from the exhaust"),
    "rattle_exhaust":    ("Exhaust & Emissions", "Rattling noise from underneath the car"),
    "exhaust_smell_cabin": ("Exhaust & Emissions", "Exhaust fumes smell inside the cabin"),
    "failed_emissions":  ("Exhaust & Emissions", "Car failed an emissions test"),
    "oil_consumption":   ("Exhaust & Emissions", "Oil level drops quickly between changes"),
    "tick_cold":         ("Exhaust & Emissions", "Ticking on cold start that fades as it warms"),

    # Climate Control 
    "ac_warm":           ("Climate Control", "AC blows warm air"),
    "ac_hiss":           ("Climate Control", "Hissing from the dashboard when AC is on"),
    "ac_cycling":        ("Climate Control", "AC switches on and off rapidly"),
    "ac_noise":          ("Climate Control", "Rattle / squeal when the AC is on"),
    "ac_weak_flow":      ("Climate Control", "Weak airflow from the vents"),
    "musty_smell":       ("Climate Control", "Musty smell from the vents"),
    "blower_noise":      ("Climate Control", "Humming / squeal from the dashboard blower"),
    "no_air":            ("Climate Control", "No air from vents at some fan speeds"),
    "fogged_windows":    ("Climate Control", "Windows fog up and will not clear"),
    "wet_carpet":        ("Climate Control", "Wet carpet / water inside the cabin"),

    # ---- Hybrid & Electric Drivetrain (advanced / scan-tool level faults) ----
    "hybrid_warning":    ("Hybrid & Electric Drivetrain", "Hybrid system warning light is on"),
    "ev_range_drop":     ("Hybrid & Electric Drivetrain", "Battery range or charge level drops unusually fast"),
    "engine_runs_constantly": ("Hybrid & Electric Drivetrain", "Petrol engine runs constantly and rarely switches off"),
    "hv_cooling_fan":    ("Hybrid & Electric Drivetrain", "Hybrid battery cooling fan is unusually loud"),
    "soc_jumps":         ("Hybrid & Electric Drivetrain", "Battery charge level jumps or fluctuates suddenly"),
    "dtc_p0a80":         ("Hybrid & Electric Drivetrain", "Scan tool shows code P0A80 (replace hybrid battery)"),
    "dtc_cell_imbalance": ("Hybrid & Electric Drivetrain", "Scan tool shows large cell-voltage imbalance"),
    "reduced_power":     ("Hybrid & Electric Drivetrain", "Vehicle enters reduced-power (limp) mode"),
    "hv_battery_hot":    ("Hybrid & Electric Drivetrain", "Battery temperature warning is displayed"),
    "inverter_whine":    ("Hybrid & Electric Drivetrain", "High-pitched whine from the motor / inverter"),
    "inverter_temp":     ("Hybrid & Electric Drivetrain", "Inverter or motor temperature warning"),
    "dtc_inverter":      ("Hybrid & Electric Drivetrain", "Scan tool shows inverter fault code (P0A78 / P0A7A)"),
    "motor_judder":      ("Hybrid & Electric Drivetrain", "Judder when pulling away on electric power"),
    "dcdc_drain":        ("Hybrid & Electric Drivetrain", "12V battery drains repeatedly even after driving"),
    "ready_not_on":      ("Hybrid & Electric Drivetrain", "Vehicle will not enter READY / drive mode"),
    "hv_isolation":      ("Hybrid & Electric Drivetrain", "High-voltage isolation / ground-fault warning"),
    "dtc_isolation":     ("Hybrid & Electric Drivetrain", "Scan tool shows insulation fault code (P0AA6)"),
    "ready_clunk":       ("Hybrid & Electric Drivetrain", "Loud clunk from the battery area when starting"),
    "charging_fails":    ("Hybrid & Electric Drivetrain", "Vehicle will not charge from the charger"),
    "charge_port_hot":   ("Hybrid & Electric Drivetrain", "Charging port or cable becomes very hot"),
    "charging_slow":     ("Hybrid & Electric Drivetrain", "Charging is much slower than normal"),
    "charge_error_light": ("Hybrid & Electric Drivetrain", "Charging indicator flashes an error"),
    "hv_burning_smell":  ("Hybrid & Electric Drivetrain", "Burning smell near the charging port or battery"),
    "regen_weak":        ("Hybrid & Electric Drivetrain", "Regenerative braking feels weak or inconsistent"),
    "brake_pedal_odd":   ("Hybrid & Electric Drivetrain", "Brake pedal feels unusual on a hybrid / electric car"),
}

# ------------------------- rules -------------------------
RULES = []


def rule(name, category, severity, symptoms, fix):
    RULES.append({"name": name, "category": category, "severity": severity,
                  "symptoms": symptoms, "fix": fix})


# ======== Engine & Fuel (13) ========
rule("Fuel pump failure", "Engine & Fuel", "High",
     {"cranks_no_start": .35, "sputtering": .20, "loss_power": .20, "hard_start": .15, "stalling": .10},
     "Test fuel pressure and replace the fuel pump.")
rule("Clogged fuel filter", "Engine & Fuel", "Medium",
     {"loss_power": .30, "hesitation": .25, "sputtering": .20, "poor_mileage": .15, "hard_start": .10},
     "Replace the fuel filter.")
rule("Worn spark plugs", "Engine & Fuel", "Low",
     {"rough_idle": .30, "poor_mileage": .20, "hesitation": .20, "check_engine": .15, "hard_start": .15},
     "Replace the spark plugs (every 30,000-50,000 km).")
rule("Faulty ignition coil", "Engine & Fuel", "Medium",
     {"rough_idle": .30, "sputtering": .25, "check_engine": .25, "backfire": .10, "loss_power": .10},
     "Scan for misfire codes and replace the faulty coil.")
rule("Clogged air filter", "Engine & Fuel", "Low",
     {"black_smoke": .30, "loss_power": .25, "poor_mileage": .25, "rough_idle": .10, "hesitation": .10},
     "Clean or replace the air filter.")
rule("Dirty / faulty MAF sensor", "Engine & Fuel", "Medium",
     {"stalling": .25, "check_engine": .25, "rough_idle": .20, "poor_mileage": .15, "hesitation": .15},
     "Clean the mass-airflow sensor with MAF cleaner, or replace it.")
rule("Low oil / oil pressure failure", "Engine & Fuel", "Critical",
     {"oil_light": .50, "knocking": .30, "temp_high": .10, "oil_leak": .10},
     "STOP the engine now. Check the oil level and tow the car to a mechanic.")
rule("Engine oil leak", "Engine & Fuel", "Medium",
     {"oil_leak": .50, "burning_oil_smell": .20, "oil_light": .15, "blue_smoke": .15},
     "Find the leak (gasket / seal), repair it and top up the oil.")
rule("Fuel leak", "Engine & Fuel", "Critical",
     {"fuel_smell": .55, "fuel_puddle": .20, "poor_mileage": .15, "check_engine": .10},
     "FIRE RISK! Stop driving and have the fuel line / tank inspected.")
rule("Faulty idle control / throttle body", "Engine & Fuel", "Low",
     {"high_idle": .35, "rough_idle": .25, "stalling": .25, "check_engine": .15},
     "Clean the throttle body or replace the idle air control valve.")
rule("Timing belt / chain failure", "Engine & Fuel", "Critical",
     {"rattle_timing": .30, "cranks_no_start": .30, "rough_idle": .20, "check_engine": .20},
     "Do NOT run the engine. Inspect / replace the timing belt or chain immediately.")
rule("Dirty / bad fuel injectors", "Engine & Fuel", "Medium",
     {"rough_idle": .25, "poor_mileage": .25, "check_engine": .20, "hesitation": .20, "fuel_smell": .10},
     "Use injector cleaner or have the injectors cleaned / replaced.")
rule("Vacuum leak", "Engine & Fuel", "Low",
     {"hiss_engine": .30, "high_idle": .30, "rough_idle": .20, "check_engine": .20},
     "Inspect vacuum hoses and intake gaskets; replace cracked parts.")

# ======== Cooling (9) ========
rule("Low coolant", "Cooling", "High",
     {"temp_high": .35, "steam": .25, "coolant_low": .40},
     "Let the engine cool, refill coolant and check for leaks.")
rule("Radiator leak", "Cooling", "High",
     {"coolant_leak": .40, "coolant_low": .30, "temp_high": .20, "sweet_smell": .10},
     "Repair or replace the radiator and hoses.")
rule("Thermostat stuck closed", "Cooling", "High",
     {"temp_high": .40, "temp_swings": .25, "heater_cold": .20, "steam": .15},
     "Replace the thermostat.")
rule("Thermostat stuck open", "Cooling", "Low",
     {"temp_low": .50, "heater_cold": .30, "poor_mileage": .20},
     "Replace the thermostat.")
rule("Radiator fan failure", "Cooling", "High",
     {"fan_not_running": .50, "temp_high": .30, "ac_warm": .20},
     "Check the fan fuse / relay / motor and replace the faulty part.")
rule("Failing water pump", "Cooling", "High",
     {"temp_high": .30, "whine_pump": .25, "coolant_leak": .25, "steam": .20},
     "Replace the water pump (and the timing belt if it drives the pump).")
rule("Blown head gasket", "Cooling", "Critical",
     {"white_smoke": .30, "milky_oil": .30, "temp_high": .20, "coolant_low": .20},
     "Do NOT drive. The engine needs head-gasket repair.")
rule("Heater core leak", "Cooling", "Medium",
     {"sweet_smell": .30, "fogged_windows": .25, "wet_carpet": .25, "coolant_low": .20},
     "Replace the heater core.")
rule("Air lock in cooling system", "Cooling", "Low",
     {"heater_cold": .40, "gurgling": .30, "coolant_low": .30},
     "Bleed the cooling system and top up coolant.")

# ======== Brakes (8) ========
rule("Worn brake pads", "Brakes", "High",
     {"squeal_brakes": .40, "grinding_brakes": .30, "long_stopping": .20, "brake_light": .10},
     "Replace the brake pads (and check the discs).")
rule("Warped brake rotors", "Brakes", "Medium",
     {"pedal_vibration": .50, "vibration_wheel": .25, "long_stopping": .15, "squeal_brakes": .10},
     "Resurface or replace the brake rotors.")
rule("Low brake fluid / leak", "Brakes", "Critical",
     {"soft_pedal": .35, "brake_fluid_low": .35, "brake_light": .20, "long_stopping": .10},
     "Do NOT drive. Find the leak, refill and bleed the brake system.")
rule("Air in brake lines", "Brakes", "Critical",
     {"soft_pedal": .50, "long_stopping": .30, "brakes_serviced": .20},
     "Bleed the brakes before driving.")
rule("Stuck brake caliper", "Brakes", "High",
     {"brake_drag": .35, "brake_pull": .30, "pulls_side": .15, "squeal_brakes": .10, "poor_mileage": .10},
     "Free or replace the seized caliper and check the pads.")
rule("Faulty brake booster", "Brakes", "High",
     {"hard_pedal": .50, "long_stopping": .25, "hiss_pedal": .25},
     "Test the vacuum booster and replace it if leaking.")
rule("ABS sensor fault", "Brakes", "Medium",
     {"abs_light": .60, "brake_light": .20, "wheel_lock": .20},
     "Scan ABS codes; clean or replace the wheel-speed sensor.")
rule("Master cylinder failure", "Brakes", "Critical",
     {"soft_pedal": .40, "pedal_sinks": .35, "brake_fluid_low": .25},
     "Do NOT drive. Replace the brake master cylinder.")

# ======== Steering, Suspension & Tires (10) ========
rule("Wheel imbalance", "Steering, Suspension & Tires", "Low",
     {"vibration_wheel": .60, "vibration_seat": .20, "uneven_tires": .20},
     "Get the wheels balanced.")
rule("Wheel misalignment", "Steering, Suspension & Tires", "Low",
     {"pulls_side": .45, "uneven_tires": .35, "steering_off_center": .20},
     "Get a wheel alignment.")
rule("Worn shock absorbers", "Steering, Suspension & Tires", "Medium",
     {"bouncy_ride": .40, "nose_dive": .25, "uneven_tires": .20, "clunk_bumps": .15},
     "Replace the shocks / struts in pairs.")
rule("Worn ball joints / bushings", "Steering, Suspension & Tires", "High",
     {"clunk_bumps": .35, "steering_play": .30, "uneven_tires": .15, "pulls_side": .10, "vibration_wheel": .10},
     "Replace the worn ball joints / bushings.")
rule("Worn tie-rod ends", "Steering, Suspension & Tires", "High",
     {"steering_play": .40, "wandering": .20, "vibration_wheel": .20, "uneven_tires": .20},
     "Replace the tie-rod ends and align the wheels.")
rule("Power steering fluid low / pump failure", "Steering, Suspension & Tires", "Medium",
     {"whine_steering": .40, "steering_heavy": .40, "ps_leak": .20},
     "Top up fluid, find the leak, or replace the power steering pump.")
rule("Worn CV joint", "Steering, Suspension & Tires", "Medium",
     {"cv_click": .60, "grease_splatter": .20, "vibration_wheel": .20},
     "Replace the CV joint / drive-shaft boot.")
rule("Slow puncture / valve leak", "Steering, Suspension & Tires", "Low",
     {"low_tire": .70, "pulls_side": .15, "poor_mileage": .15},
     "Find and repair the puncture or replace the valve.")
rule("Damaged tire (bulge / sidewall)", "Steering, Suspension & Tires", "Critical",
     {"tire_bulge": .60, "low_tire": .20, "vibration_wheel": .20},
     "Do NOT drive at speed. Replace the tire immediately.")
rule("Worn wheel bearing", "Steering, Suspension & Tires", "High",
     {"hum_wheel": .50, "vibration_wheel": .20, "steering_play": .15, "pulls_side": .15},
     "Replace the wheel bearing.")

# ======== Transmission & Clutch (7) ========
rule("Worn clutch", "Transmission & Clutch", "Medium",
     {"clutch_slip": .40, "burning_clutch_smell": .25, "loss_power": .20, "clutch_hard": .15},
     "Replace the clutch kit.")
rule("Low transmission fluid", "Transmission & Clutch", "High",
     {"trans_fluid_leak": .30, "hard_shift": .25, "gear_slip": .25, "trans_whine": .20},
     "Top up / change the fluid and fix any leak.")
rule("Failing automatic transmission", "Transmission & Clutch", "High",
     {"gear_slip": .30, "hard_shift": .25, "stuck_gear": .15, "trans_fluid_leak": .10,
      "check_engine": .10, "burning_clutch_smell": .10},
     "Have the transmission diagnosed / rebuilt by a specialist.")
rule("Clutch hydraulic (master / slave) fault", "Transmission & Clutch", "Medium",
     {"clutch_hard": .35, "stuck_gear": .30, "grind_gear": .20, "clutch_soft": .15},
     "Check clutch fluid; replace the master or slave cylinder.")
rule("Worn gearbox synchronizers", "Transmission & Clutch", "Medium",
     {"grind_gear": .50, "hard_shift": .25, "stuck_gear": .25},
     "Gearbox overhaul / synchronizer replacement.")
rule("Bad torque converter", "Transmission & Clutch", "High",
     {"shudder": .35, "gear_slip": .25, "trans_whine": .20, "loss_power": .10, "temp_high": .10},
     "Replace the torque converter.")
rule("Worn differential / driveshaft joint", "Transmission & Clutch", "Medium",
     {"diff_hum": .40, "clunk_gear": .35, "vibration_seat": .25},
     "Inspect the differential and driveshaft joints; replace worn parts.")

# ======== Electrical & Battery (9) ========
rule("Dead battery", "Electrical & Battery", "Medium",
     {"dim_lights": .30, "wont_start": .25, "clicking": .25, "battery_old": .20},
     "Jump-start the car or replace the battery.")
rule("Weak / ageing battery", "Electrical & Battery", "Medium",
     {"slow_crank": .40, "battery_old": .30, "dim_lights": .20, "hard_start": .10},
     "Load-test and replace the battery.")
rule("Corroded battery terminals", "Electrical & Battery", "Low",
     {"corroded_terminals": .50, "slow_crank": .20, "dim_lights": .15, "electrics_flaky": .15},
     "Clean the terminals with baking soda and apply grease.")
rule("Loose battery connection", "Electrical & Battery", "Low",
     {"electrics_flaky": .35, "slow_crank": .20, "clicking": .15, "wont_start": .15, "corroded_terminals": .15},
     "Tighten the battery clamps and check cables.")
rule("Faulty alternator", "Electrical & Battery", "High",
     {"battery_light": .35, "dim_lights": .25, "stalling": .20, "electrics_flaky": .20},
     "Test and replace the alternator; the battery will drain soon.")
rule("Bad starter motor", "Electrical & Battery", "Medium",
     {"clicking": .35, "wont_start": .30, "grinding_start": .20, "slow_crank": .15},
     "Test and replace the starter motor.")
rule("Faulty ignition switch / solenoid", "Electrical & Battery", "Medium",
     {"silent_key": .50, "wont_start": .25, "electrics_flaky": .25},
     "Replace the ignition switch or starter solenoid.")
rule("Blown fuse / short circuit", "Electrical & Battery", "Medium",
     {"blown_fuses": .45, "burning_wire_smell": .30, "electrics_flaky": .25},
     "Find the short before replacing the fuse.")
rule("Damaged wiring harness", "Electrical & Battery", "High",
     {"burning_wire_smell": .40, "electrics_flaky": .30, "blown_fuses": .15, "check_engine": .15},
     "Inspect and repair / replace the harness (fire risk).")

# ======== Exhaust & Emissions (6) ========
rule("Clogged catalytic converter", "Exhaust & Emissions", "High",
     {"loss_power": .30, "rotten_egg": .25, "check_engine": .20, "failed_emissions": .15, "temp_high": .10},
     "Replace the catalytic converter after fixing the root cause.")
rule("Exhaust leak / broken muffler", "Exhaust & Emissions", "Low",
     {"loud_exhaust": .50, "rattle_exhaust": .25, "exhaust_smell_cabin": .25},
     "Weld or replace the exhaust section.")
rule("Faulty oxygen sensor", "Exhaust & Emissions", "Low",
     {"check_engine": .35, "poor_mileage": .25, "failed_emissions": .25, "rough_idle": .15},
     "Replace the oxygen (lambda) sensor.")
rule("Burning engine oil (worn rings / seals)", "Exhaust & Emissions", "Medium",
     {"blue_smoke": .50, "burning_oil_smell": .20, "oil_consumption": .20, "poor_mileage": .10},
     "Engine inspection; may need valve-seal or piston-ring work.")
rule("Rich fuel mixture", "Exhaust & Emissions", "Medium",
     {"black_smoke": .40, "poor_mileage": .25, "fuel_smell": .20, "failed_emissions": .15},
     "Check sensors, injectors and air filter.")
rule("Cracked exhaust manifold", "Exhaust & Emissions", "Medium",
     {"tick_cold": .40, "loud_exhaust": .30, "exhaust_smell_cabin": .30},
     "Replace the manifold or its gasket.")

# ======== Climate Control (5) ========
rule("Low AC refrigerant", "Climate Control", "Low",
     {"ac_warm": .55, "ac_cycling": .30, "ac_hiss": .15},
     "Leak-test and recharge the AC system.")
rule("Faulty AC compressor", "Climate Control", "Medium",
     {"ac_warm": .40, "ac_noise": .40, "ac_cycling": .20},
     "Inspect and replace the AC compressor.")
rule("Clogged cabin air filter", "Climate Control", "Low",
     {"ac_weak_flow": .50, "musty_smell": .25, "fogged_windows": .25},
     "Replace the cabin air filter.")
rule("Blower motor failure", "Climate Control", "Low",
     {"ac_weak_flow": .40, "blower_noise": .30, "no_air": .30},
     "Replace the blower motor or its resistor.")
rule("Blocked evaporator drain / mould", "Climate Control", "Low",
     {"musty_smell": .40, "wet_carpet": .35, "fogged_windows": .25},
     "Clear the AC drain and disinfect the evaporator.")


# ======== Hybrid & Electric Drivetrain (11) - advanced faults that need a scan tool / specialist ========
rule("Hybrid battery pack degradation", "Hybrid & Electric Drivetrain", "High",
     {"ev_range_drop": .25, "engine_runs_constantly": .20, "soc_jumps": .20, "hv_cooling_fan": .15,
      "hybrid_warning": .10, "dtc_p0a80": .10},
     "Load-test the hybrid battery; recondition weak modules or replace the pack.")
rule("Hybrid battery cell imbalance", "Hybrid & Electric Drivetrain", "Medium",
     {"soc_jumps": .30, "dtc_cell_imbalance": .30, "ev_range_drop": .20, "reduced_power": .20},
     "Run a module balance test and replace the weak modules.")
rule("Hybrid battery cooling fan / duct blockage", "Hybrid & Electric Drivetrain", "Low",
     {"hv_cooling_fan": .45, "hv_battery_hot": .25, "ev_range_drop": .15, "hybrid_warning": .15},
     "Clean the battery air intake filter and ducts; test the cooling fan.")
rule("Inverter / motor-generator fault", "Hybrid & Electric Drivetrain", "High",
     {"inverter_whine": .30, "reduced_power": .25, "inverter_temp": .20, "dtc_inverter": .15, "motor_judder": .10},
     "Read the inverter codes, then inspect the inverter and motor-generator.")
rule("Inverter coolant pump failure", "Hybrid & Electric Drivetrain", "High",
     {"inverter_temp": .40, "reduced_power": .25, "coolant_low": .20, "hybrid_warning": .15},
     "Test the inverter coolant pump, replace it and bleed the loop.")
rule("DC-DC converter failure", "Hybrid & Electric Drivetrain", "High",
     {"dcdc_drain": .35, "battery_light": .20, "dim_lights": .15, "hybrid_warning": .15, "ready_not_on": .15},
     "Test the DC-DC output (about 13.5-14.5 V) and replace the converter.")
rule("High-voltage insulation (isolation) fault", "Hybrid & Electric Drivetrain", "Critical",
     {"hv_isolation": .45, "dtc_isolation": .25, "hybrid_warning": .15, "ready_not_on": .15},
     "Do NOT touch the orange HV cables. Have a certified HV technician locate the leakage.")
rule("HV contactor / system main relay fault", "Hybrid & Electric Drivetrain", "High",
     {"ready_not_on": .35, "ready_clunk": .25, "hybrid_warning": .20, "reduced_power": .20},
     "Test the system main relays and replace the faulty contactor.")
rule("Charging port / cable overheating", "Hybrid & Electric Drivetrain", "Critical",
     {"charge_port_hot": .50, "hv_burning_smell": .25, "charging_slow": .25},
     "Stop charging at once; inspect the charge-port contacts and cable for damage.")
rule("On-board charger / charging control fault", "Hybrid & Electric Drivetrain", "Medium",
     {"charging_fails": .40, "charge_error_light": .30, "charging_slow": .15, "hybrid_warning": .15},
     "Test the charging station first, then the on-board charger and charge-port module.")
rule("Regenerative braking system fault", "Hybrid & Electric Drivetrain", "High",
     {"regen_weak": .35, "brake_pedal_odd": .25, "brake_light": .20, "abs_light": .10, "hybrid_warning": .10},
     "Scan the brake-control ECU; inspect the brake actuator and regen calibration.")


# ------------------------- demo scenarios (for live presentation) -------------------------
DEMO_SCENARIOS = {
    "Overheating engine": ["temp_high", "steam", "coolant_low"],
    "Spongy brake pedal": ["soft_pedal", "brake_fluid_low", "brake_light", "long_stopping"],
    "Won't start + worn brakes (2 faults)": ["wont_start", "clicking", "dim_lights", "battery_old",
                                              "squeal_brakes", "grinding_brakes", "long_stopping"],
    "Shaky steering wheel": ["vibration_wheel", "vibration_seat", "uneven_tires"],
    "Blue exhaust smoke": ["blue_smoke", "burning_oil_smell", "oil_consumption"],
    "Hybrid battery trouble": ["ev_range_drop", "engine_runs_constantly", "soc_jumps", "hv_cooling_fan"],
}


# ------------------------- self-check (runs on import) -------------------------
def _validate():
    names = set()
    for r in RULES:
        assert r["name"] not in names, f"duplicate rule: {r['name']}"
        names.add(r["name"])
        assert r["severity"] in SEVERITY_RANK, r["name"]
        assert r["category"] in CATEGORIES, r["name"]
        assert abs(sum(r["symptoms"].values()) - 1.0) < 1e-6, f"weights != 1.0 in {r['name']}"
        for s in r["symptoms"]:
            assert s in SYMPTOMS, f"unknown symptom '{s}' in {r['name']}"
    used = {s for r in RULES for s in r["symptoms"]}
    assert used == set(SYMPTOMS), f"unused symptoms: {set(SYMPTOMS) - used}"
    for demo in DEMO_SCENARIOS.values():
        for s in demo:
            assert s in SYMPTOMS, s


_validate()
