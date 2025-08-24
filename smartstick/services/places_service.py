import requests
from geopy.distance import geodesic
from smartstick.interfaces.gemini import ask_gemini
from smartstick.hardware.get_gps import get_gps_coords
from smartstick.services.osrm_service import get_walking_directions, json_to_route
from smartstick.services.tts_engine import tts_speak

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

def search_place(query, max_distance_km=5):
    """
    Search for a place near the current location using Nominatim.
    If no results, fallback to Gemini.
    
    :param query: str - The place user asked (e.g., "Jollibee")
    :param current_location: tuple(lat, lon) - Current coordinates
    :param max_distance_km: float - Max distance considered "nearby"
    :return: dict with 'name', 'lat', 'lon', 'advice'
    """
    current_location = get_gps_coords()
    # current_location = (120.329134, 16.021163)
    offset = 0.1  # about ~11 km in degrees
    print(f"Current Location: {current_location[0]}, {current_location[1]}" )
    if not current_location:
        return {
            "name": query,
            "lat": None,
            "lon": None,
            "advice": "Walang GPS ngayon. Paki-try ulit sa ibang lugar na may mas malinaw na signal."
        }

    
    params = {
        "q": query,
        "format": "json",
        "limit": 5,
        "bounded": 1,
        "viewbox": f"{current_location[1]-offset},{current_location[0]-offset},{current_location[1]+offset},{current_location[0]+offset}"
    }

    try:
        response = requests.get(NOMINATIM_URL, params=params, headers={"User-Agent": "SmartStick/1.0"})
        results = response.json()
        print(results)
    except Exception as e:
        print(f"Error 0: {e}")
        results = []

    if not results:  # Fallback if Nominatim fails or no matches
        return fallback_to_gemini(query, current_location, reason="no_results")

    # Compute distances for all results
    nearest = None
    nearest_distance = float("inf")

    for place in results:
        lat, lon = float(place["lat"]), float(place["lon"])
        
        distance = geodesic(current_location, (lat, lon)).km

        if distance < nearest_distance:
            nearest_distance = distance
            nearest = {
                "name": place.get("display_name", "Unknown place"),
                "lat": lat,
                "lon": lon,
                "distance_km": round(distance, 2)
            }

    if nearest_distance > max_distance_km:  
        # Too far, let Gemini help
        return fallback_to_gemini(query, current_location, reason="too_far", nearest=nearest)

    return nearest


def fallback_to_gemini(query, current_location, reason, nearest=None):
    """
    Fallback strategy: 
    - No results → hardcoded speech (clear Taglish for blind users).
    - Too far → Gemini commuting guide.
    """
    try:
        # Reverse geocode para human-readable area
        addr = reverse_geocode(current_location[0], current_location[1])
        area = ", ".join(filter(None, [
            addr.get("road"),
            addr.get("suburb") or addr.get("village") or addr.get("neighbourhood"),
            addr.get("city") or addr.get("town") or addr.get("municipality"),
            addr.get("province"),
        ])) or "current location"
        print("AREA:" + area)
        if reason == "no_results":
            # 🚨 Hardcoded speech here
            return {
                "name": query,
                "lat": None,
                "lon": None,
                "advice": (
                    f"Bro, wala talagang '{query}' na makita dito sa map. "
                    f"Nandito ka around {area}. "
                    "Best move is ask locals nearby or ride a tricycle papunta sa pinakamalapit na terminal or mall. "
                    "Mas safe kaysa maghanap mag-isa."
                )
            }

        elif reason == "too_far":
            # Still use Gemini since may reference point
            prompt = (
                f"I'm currently in lat {current_location[0]}, lon {current_location[1]}. "
                f"I found {nearest['name']} about {nearest['distance_km']} km away. "
                "Can you suggest a rough commuting guide (like tricycle/jeep) to get there?"
            )
            advice = ask_gemini(prompt)
            return {
                "name": query,
                "lat": nearest["lat"] if nearest else None,
                "lon": nearest["lon"] if nearest else None,
                "advice": advice or "Try asking locals nearby or take a tricycle to the nearest terminal."
            }

        else:
            return {
                "name": query,
                "lat": nearest["lat"] if nearest else None,
                "lon": nearest["lon"] if nearest else None,
                "advice": "Wala akong makuha na malinaw na info. Ask locals nearby para sure."
            }

    except Exception as e:
        print(f"Error 1: {e}")
        return {
            "name": query,
            "lat": nearest["lat"] if nearest else None,
            "lon": nearest["lon"] if nearest else None,
            "advice": "Try asking locals nearby or take a tricycle to the nearest terminal."
        }



def reverse_geocode(lat, lon):
    """
    Convert lat/lon into a human-readable address using Nominatim reverse geocoding.
    Returns dict with useful parts (province, city, barangay, road, etc).
    """
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1
    }
    try:
        resp = requests.get(
            NOMINATIM_REVERSE_URL,
            params=params,
            headers={"User-Agent": "SmartStick/1.0"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        print("Reverse Geocode:", data)  # ✅ fixed print
        return data.get("address", {})
    except Exception as e:
        print(f"Error 2: {e}")
        return {}

if __name__ == "__main__":
    nearest = search_place("Jollibee")
    dest_lat = nearest["lat"]
    dest_lon = nearest["lon"]
    print(dest_lon)
    if dest_lat:
        steps, summary, error = get_walking_directions(dest_lat, dest_lon)
        if error:
            print("Error:", error)
            tts_speak(error, lang="tl")
        else:
            # Maybe just speak the first instruction for now
            instructions = json_to_route(steps)
            print(instructions)
            tts_speak(instructions, lang="tl")
    else: 
        tts_speak(nearest["advice"], lang="tl")