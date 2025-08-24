# services/osrm_service.py
import requests
import time
import re
from geopy.distance import geodesic
from smartstick.hardware.get_gps import get_gps_coords
from smartstick.interfaces.gemini import summarize_route
from smartstick.services.tts_engine import tts_speak

def get_walking_directions(end_lat, end_lon):
    """
    Get walking directions from OSRM between current GPS and destination coordinates.
    Also summarizes the route using Gemini (fallback: hardcoded json_to_route).
    
    Returns:
        tuple: (steps_list, summary, error_message)
    """
    # Get starting GPS
    start_lat, start_lon = get_gps_coords()
    # start_lat = 120.329134
    # start_lon = 16.021163
    if start_lat is None or start_lon is None:
        return [], None, "Walang GPS signal, hindi makuha ang location mo."

    url = (
        f"http://router.project-osrm.org/route/v1/foot/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        f"?overview=false&steps=true"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return [], None, f"Network error sa pagkuha ng ruta: {e}"
    except ValueError:
        return [], None, "Mali o hindi mabasa ang response ng server."

    if data.get("code") != "Ok":
        return [], None, f"OSRM error: {data.get('message', 'unknown error')}"

    try:
        steps_list = []
        for leg in data["routes"][0]["legs"]:
            for step in leg["steps"]:
                maneuver = step["maneuver"]
                instruction_type = maneuver.get("type", "")
                modifier = maneuver.get("modifier", "")
                street_name = step.get("name", "")
                distance = step.get("distance", 0)
                duration = step.get("duration", 0)
                location = (maneuver["location"][1], maneuver["location"][0])  # lat, lon

                # Build instruction
                if modifier:
                    instruction = f"{instruction_type} {modifier} onto {street_name}"
                else:
                    instruction = f"{instruction_type} onto {street_name}"

                steps_list.append({
                    "instruction": instruction.strip(),
                    "distance_m": distance,
                    "duration_s": duration,
                    "location": location
                })

        # 🔊 Summarize route here (Gemini → fallback to json_to_route)
        try:
            summary = summarize_route(steps_list)
            print(f"Summary: {summary}")
            if not summary or summary.startswith("Error"):
                print(f"Error summary")
                raise Exception("Gemini failed.")
        except Exception as e:
            print(f"[Gemini Error] {e}. Falling back to hardcoded summary.")
            summary = json_to_route(steps_list)

        return steps_list, summary, None
    except (KeyError, IndexError) as e:
        return [], None, f"Invalid route data format: {e}"



# Optional: placeholder for compass reading
def get_heading():
    """
    Returns heading in degrees (0-360).  
    Replace with actual HMC5883L reading when available.
    """
    return None  # None means no compass yet

TURN_RADIUS = 10  # meters

def navigate_osrm(destination_lat, destination_lon):
    # Get OSRM steps + summary
    steps, summary, error = get_walking_directions(destination_lat, destination_lon)
    if error:
        print("Error:", error)
        tts_speak(error, lang="tl")
        return

    # 🔊 Speak route summary
    print("Route summary:", summary)
    tts_speak(summary, lang="tl")

    # 🔄 Live navigation loop (hardcoded instructions)
    current_step = 0
    print("Starting navigation...")
    while current_step < len(steps):
        lat, lon = get_gps_coords(timeout=5)
        if lat is None:
            print("Waiting for GPS fix...")
            time.sleep(1)
            continue

        step = steps[current_step]
        maneuver_location = step["location"]
        distance_to_turn = geodesic((lat, lon), maneuver_location).meters

        if distance_to_turn <= TURN_RADIUS:
            instruction = step['instruction']
            print(f"Step {current_step+1}: {instruction} ({distance_to_turn:.1f} m)")
            tts_speak(instruction, lang="tl")
            current_step += 1
            time.sleep(2)

        time.sleep(1)

    tts_speak("Nakarating ka na sa destination mo!", lang="tl")
    print("Navigation finished.")

def json_to_route(steps):
    """
    Convert cleaned steps (list of dict) into a hardcoded-style summary.
    Removes broken instructions like 'turn right onto' with no street name.
    """
    if not steps:
        return "Walang nahanap na ruta."

    parts = []
    for step in steps:
        instr = step["instruction"].strip()

        # Special handling for arrive
        if instr.startswith("arrive"):
            if "right" in instr:
                instr = "Nakarating ka na, nasa kanan side"
            elif "left" in instr:
                instr = "Nakarating ka na, nasa kaliwa side"
            else:
                instr = "Nakarating ka na sa destination mo"

            parts.append(instr)
            continue

        # Remove "onto" if it’s hanging with no street name
        instr = re.sub(r"\s*onto\s*$", "", instr, flags=re.IGNORECASE)

        dist = round(step.get("distance_m", 0))
        if dist > 0:
            parts.append(f"{instr}, mga {dist} metro")
        else:
            parts.append(instr)

    return "Narito ang ruta mo: " + ". ".join(parts) + "."

# Example usage
if __name__ == "__main__":
    # Example destination
    dest_lat, dest_lon = 16.021138, 120.324259
    # navigate_osrm(dest_lat, dest_lon)
    steps, summary, error = get_walking_directions(dest_lat, dest_lon)
    if error:
        print("Error:", error)
        tts_speak(error, lang="tl")
    else:
        # Maybe just speak the first instruction for now
        # instructions = json_to_route(steps)
        # print(instructions)
        # tts_speak(instructions, lang="tl")
        tts_speak(summary, lang="tl")
