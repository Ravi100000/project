import requests
from django.conf import settings

def get_route_info(destination):
    """
    Returns (distance_km, duration_mins) for a route from Ahmedabad to destination.
    Uses OpenRouteService API.
    """
    api_key = settings.ORS_API_KEY
    if not api_key:
        return 0, 0

    # Geocode Ahmedabad (fixed origin)
    # Ahmedabad coordinates: 72.5714, 23.0225 (lon, lat)
    origin_coords = [72.5714, 23.0225]

    # Geocode destination
    geocode_url = f"https://api.openrouteservice.org/geocode/search?api_key={api_key}&text={destination}"
    try:
        response = requests.get(geocode_url)
        data = response.json()
        if not data.get('features'):
            return 0, 0
        dest_coords = data['features'][0]['geometry']['coordinates']
    except Exception:
        return 0, 0

    # Get route
    route_url = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={api_key}&start={origin_coords[0]},{origin_coords[1]}&end={dest_coords[0]},{dest_coords[1]}"
    try:
        response = requests.get(route_url)
        data = response.json()
        if not data.get('features'):
            return 0, 0
        
        # distance is in meters, duration in seconds
        summary = data['features'][0]['properties']['summary']
        distance_km = summary['distance'] / 1000.0
        duration_mins = summary['duration'] / 60.0
        return round(distance_km, 2), int(duration_mins)
    except Exception:
        return 0, 0
