import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

AGENT_LOGS = []


def log_agent_step(step_name: str, data: dict) -> dict:
    log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "step_name": step_name,
        "data": data
    }
    AGENT_LOGS.append(log)
    print("\n========== TRAVELMATE AI LOG ==========")
    print(log)
    print("=======================================\n")
    return log


def clear_logs() -> dict:
    AGENT_LOGS.clear()
    return {"status": "logs_cleared"}


def get_all_logs() -> list:
    return AGENT_LOGS


def geocode_place(place: str) -> dict:
    log_agent_step("geocoding_started", {"place": place})

    if not GOOGLE_MAPS_API_KEY:
        result = {"success": False, "error": "GOOGLE_MAPS_API_KEY missing in .env"}
        log_agent_step("geocoding_failed", result)
        return result

    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": f"{place}, India",
            "key": GOOGLE_MAPS_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "OK":
            result = {
                "success": False,
                "place": place,
                "error": data.get("status"),
                "message": data.get("error_message", "Geocoding failed")
            }
            log_agent_step("geocoding_failed", result)
            return result

        item = data["results"][0]
        location = item["geometry"]["location"]

        result = {
            "success": True,
            "source": "Google Geocoding API",
            "place": place,
            "formatted_address": item["formatted_address"],
            "latitude": location["lat"],
            "longitude": location["lng"]
        }

        log_agent_step("geocoding_completed", result)
        return result

    except Exception as error:
        result = {"success": False, "place": place, "error": str(error)}
        log_agent_step("geocoding_exception", result)
        return result


def get_weather(city: str, latitude=None, longitude=None) -> dict:
    log_agent_step("weather_tool_started", {"city": city, "latitude": latitude, "longitude": longitude})

    if not OPENWEATHER_API_KEY:
        result = {"success": False, "error": "OPENWEATHER_API_KEY missing in .env"}
        log_agent_step("weather_tool_failed", result)
        return result

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"

        if latitude is not None and longitude is not None:
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            }
        else:
            params = {
                "q": f"{city},Himachal Pradesh,IN",
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200:
            result = {
                "success": False,
                "city": city,
                "error": data.get("message", "Weather API failed")
            }
            log_agent_step("weather_tool_failed", result)
            return result

        result = {
            "success": True,
            "source": "OpenWeather API",
            "city": data.get("name", city),
            "weather": data["weather"][0]["main"],
            "condition": data["weather"][0]["description"],
            "temperature_celsius": data["main"]["temp"],
            "feels_like_celsius": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed_mps": data["wind"]["speed"],
            "latitude": data["coord"]["lat"],
            "longitude": data["coord"]["lon"]
        }

        log_agent_step("weather_tool_completed", result)
        return result

    except Exception as error:
        result = {"success": False, "city": city, "error": str(error)}
        log_agent_step("weather_tool_exception", result)
        return result


def analyze_risk(city: str, month: str, weather: dict) -> dict:
    log_agent_step("risk_analysis_started", {"city": city, "month": month, "weather": weather})

    city_lower = city.lower()
    month_lower = month.lower()

    weather_main = str(weather.get("weather", "")).lower()
    condition = str(weather.get("condition", "")).lower()
    temperature = weather.get("temperature_celsius")
    feels_like = weather.get("feels_like_celsius")
    wind_speed = weather.get("wind_speed_mps")
    humidity = weather.get("humidity")

    risk_level = "Low"
    risk_reasons = []

    if city_lower == "manali" and month_lower in ["december", "january", "february"]:
        risk_level = "High"
        risk_reasons.append("Winter season in Manali has heavy snowfall and roadblock possibility.")

    if "snow" in weather_main or "snow" in condition:
        risk_level = "High"
        risk_reasons.append("Live weather indicates snowfall risk.")

    if "rain" in weather_main or "rain" in condition or "drizzle" in weather_main:
        if risk_level != "High":
            risk_level = "Medium"
        risk_reasons.append("Rain may affect road travel and cause delays.")

    if "storm" in weather_main or "thunderstorm" in condition:
        risk_level = "High"
        risk_reasons.append("Storm or thunderstorm detected.")

    if temperature is not None and temperature <= 3:
        if risk_level != "High":
            risk_level = "Medium"
        risk_reasons.append("Very cold temperature detected.")

    if feels_like is not None and feels_like >= 38:
        if risk_level != "High":
            risk_level = "Medium"
        risk_reasons.append("High heat index may affect outdoor travel.")

    if wind_speed is not None and wind_speed >= 12:
        if risk_level != "High":
            risk_level = "Medium"
        risk_reasons.append("High wind speed detected.")

    if humidity is not None and humidity >= 85:
        risk_reasons.append("High humidity detected.")

    if not risk_reasons:
        risk_reasons.append("No major travel risks detected.")

    result = {
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "recommendation": (
            "Carry backup travel plans, keep buffer time, and verify local road conditions."
            if risk_level in ["High", "Medium"]
            else "Trip looks safe based on current weather and seasonal checks."
        )
    }

    log_agent_step("risk_analysis_completed", result)
    return result


def get_place_photo_url(photo_name: str, max_height: int = 600, max_width: int = 800) -> str:
    if not photo_name or not GOOGLE_MAPS_API_KEY:
        return ""

    return (
        f"https://places.googleapis.com/v1/{photo_name}/media"
        f"?maxHeightPx={max_height}"
        f"&maxWidthPx={max_width}"
        f"&key={GOOGLE_MAPS_API_KEY}"
    )


def get_price_score(price_level: str) -> int:
    scores = {
        "PRICE_LEVEL_FREE": 5,
        "PRICE_LEVEL_INEXPENSIVE": 5,
        "PRICE_LEVEL_MODERATE": 4,
        "PRICE_LEVEL_EXPENSIVE": 2,
        "PRICE_LEVEL_VERY_EXPENSIVE": 1,
        "PRICE_LEVEL_UNSPECIFIED": 3
    }
    return scores.get(price_level, 3)


def get_price_label(price_level: str) -> str:
    labels = {
        "PRICE_LEVEL_FREE": "Very cheap",
        "PRICE_LEVEL_INEXPENSIVE": "Budget friendly",
        "PRICE_LEVEL_MODERATE": "Moderate",
        "PRICE_LEVEL_EXPENSIVE": "Expensive",
        "PRICE_LEVEL_VERY_EXPENSIVE": "Very expensive",
        "PRICE_LEVEL_UNSPECIFIED": "Price not available"
    }
    return labels.get(price_level, "Price not available")


def get_real_hotels(city: str, budget: int) -> list:
    log_agent_step("real_hotels_started", {"city": city, "budget": budget})

    if not GOOGLE_MAPS_API_KEY:
        result = [{"success": False, "error": "GOOGLE_MAPS_API_KEY missing in .env"}]
        log_agent_step("real_hotels_failed", result[0])
        return result

    try:
        url = "https://places.googleapis.com/v1/places:searchText"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": (
                "places.id,"
                "places.displayName,"
                "places.formattedAddress,"
                "places.location,"
                "places.rating,"
                "places.userRatingCount,"
                "places.priceLevel,"
                "places.photos,"
                "places.types,"
                "places.businessStatus"
            )
        }

        body = {
            "textQuery": f"best budget hotels in {city} India",
            "includedType": "lodging",
            "maxResultCount": 10,
            "languageCode": "en"
        }

        response = requests.post(url, headers=headers, json=body, timeout=15)
        data = response.json()

        if response.status_code != 200 or "places" not in data:
            result = [{"success": False, "error": data}]
            log_agent_step("real_hotels_failed", result[0])
            return result

        hotels = []

        for place in data.get("places", []):
            business_status = place.get("businessStatus", "")
            if business_status and business_status != "OPERATIONAL":
                continue

            name = place.get("displayName", {}).get("text", "Unknown Hotel")
            address = place.get("formattedAddress", "Address unavailable")
            rating = place.get("rating", 0)
            reviews = place.get("userRatingCount", 0)
            price_level = place.get("priceLevel", "PRICE_LEVEL_UNSPECIFIED")
            location = place.get("location", {})
            photos = place.get("photos", [])

            image_url = ""
            if photos:
                image_url = get_place_photo_url(photos[0].get("name", ""))

            price_score = get_price_score(price_level)

            ranking_score = (
                float(rating or 0) * 3
                + min(int(reviews or 0), 5000) / 1000
                + price_score
            )

            if rating and rating >= 4.5 and reviews >= 500:
                quality_tag = "Best reviewed"
            elif rating and rating >= 4.2:
                quality_tag = "Highly rated"
            elif price_level in ["PRICE_LEVEL_INEXPENSIVE", "PRICE_LEVEL_MODERATE"]:
                quality_tag = "Budget suitable"
            else:
                quality_tag = "Available option"

            hotels.append({
                "success": True,
                "name": name,
                "location": address,
                "rating": rating,
                "reviews": reviews,
                "price_level": price_level,
                "price_label": get_price_label(price_level),
                "budget_match": price_level in [
                    "PRICE_LEVEL_FREE",
                    "PRICE_LEVEL_INEXPENSIVE",
                    "PRICE_LEVEL_MODERATE",
                    "PRICE_LEVEL_UNSPECIFIED"
                ],
                "quality_tag": quality_tag,
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "image_url": image_url,
                "ranking_score": round(ranking_score, 2),
                "pros": "Real hotel listing with rating, reviews, location, and photo from Google Places.",
                "cons": "Exact live room price is not available from Google Places API."
            })

        hotels = sorted(hotels, key=lambda h: h["ranking_score"], reverse=True)

        if budget < 5000:
            selected_hotels = [hotel for hotel in hotels if hotel["budget_match"]][:5]
            if not selected_hotels:
                selected_hotels = hotels[:5]
        else:
            selected_hotels = hotels[:5]

        log_agent_step("real_hotels_completed", {"count": len(selected_hotels)})
        return selected_hotels

    except Exception as error:
        result = [{"success": False, "error": str(error)}]
        log_agent_step("real_hotels_exception", result[0])
        return result


def get_real_travel_route(origin: str, destination: str, travel_mode: str = "DRIVE") -> dict:
    log_agent_step(
        "real_route_started",
        {
            "origin": origin,
            "destination": destination,
            "travel_mode": travel_mode
        }
    )

    if not GOOGLE_MAPS_API_KEY:
        result = {"success": False, "error": "GOOGLE_MAPS_API_KEY missing in .env"}
        log_agent_step("real_route_failed", result)
        return result

    try:
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": (
                "routes.distanceMeters,"
                "routes.duration,"
                "routes.description,"
                "routes.localizedValues"
            )
        }

        body = {
            "origin": {"address": f"{origin}, India"},
            "destination": {"address": f"{destination}, India"},
            "travelMode": travel_mode,
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": True,
            "languageCode": "en-IN",
            "units": "METRIC"
        }

        response = requests.post(url, headers=headers, json=body, timeout=15)
        data = response.json()

        if response.status_code != 200 or "routes" not in data:
            result = {"success": False, "error": data}
            log_agent_step("real_route_failed", result)
            return result

        routes = []

        for route in data.get("routes", []):
            localized = route.get("localizedValues", {})

            routes.append({
                "distance_meters": route.get("distanceMeters"),
                "distance_text": localized.get("distance", {}).get("text"),
                "duration_text": localized.get("duration", {}).get("text"),
                "description": route.get("description", "")
            })

        result = {
            "success": True,
            "source": "Google Routes API",
            "origin": origin,
            "destination": destination,
            "travel_mode": travel_mode,
            "routes": routes
        }

        log_agent_step("real_route_completed", result)
        return result

    except Exception as error:
        result = {"success": False, "error": str(error)}
        log_agent_step("real_route_exception", result)
        return result


def build_map_view(destination_location: dict, hotels: list, route: dict) -> dict:
    hotel_markers = []

    for hotel in hotels:
        if hotel.get("success") and hotel.get("latitude") and hotel.get("longitude"):
            hotel_markers.append({
                "type": "hotel",
                "name": hotel.get("name"),
                "location": hotel.get("location"),
                "rating": hotel.get("rating"),
                "image_url": hotel.get("image_url"),
                "latitude": hotel.get("latitude"),
                "longitude": hotel.get("longitude")
            })

    map_view = {
        "center": {
            "latitude": destination_location.get("latitude"),
            "longitude": destination_location.get("longitude")
        },
        "destination_marker": {
            "type": "destination",
            "name": destination_location.get("place"),
            "address": destination_location.get("formatted_address"),
            "latitude": destination_location.get("latitude"),
            "longitude": destination_location.get("longitude")
        },
        "hotel_markers": hotel_markers,
        "route_summary": route.get("routes", []) if route.get("success") else []
    }

    log_agent_step("map_view_created", {"hotel_markers_count": len(hotel_markers)})
    return map_view


def build_travel_context(
    user_input: str,
    city: str,
    month: str,
    budget: int,
    origin: str = ""
) -> dict:
    clear_logs()

    log_agent_step(
        "user_input_received",
        {
            "user_input": user_input,
            "city": city,
            "month": month,
            "budget": budget,
            "origin": origin
        }
    )

    destination_location = geocode_place(city)

    if destination_location.get("success"):
        weather = get_weather(
            city,
            latitude=destination_location.get("latitude"),
            longitude=destination_location.get("longitude")
        )
    else:
        weather = get_weather(city)

    risk = analyze_risk(city, month, weather)
    hotels = get_real_hotels(city, budget)

    if origin:
        travel_route = get_real_travel_route(origin=origin, destination=city)
    else:
        travel_route = {
            "success": False,
            "message": "Origin not provided, so route calculation skipped."
        }

    map_view = build_map_view(destination_location, hotels, travel_route)

    result = {
        "weather": weather,
        "risk": risk,
        "destination_location": destination_location,
        "hotels": hotels,
        "travel_route": travel_route,
        "map_view": map_view,
        "logs": get_all_logs()
    }

    log_agent_step("travel_context_ready", result)
    return result


# Backward compatible name, in case old code imports this
def build_member4_context(
    user_input: str,
    city: str,
    month: str,
    budget: int,
    origin: str = ""
) -> dict:
    return build_travel_context(user_input, city, month, budget, origin)