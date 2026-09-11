from geopy.geocoders import Nominatim


geolocator = Nominatim(
    user_agent="photo-agent"
)


def coordinates_to_location(latitude, longitude):

    if latitude is None or longitude is None:
        return None

    try:
        location = geolocator.reverse(
            (latitude, longitude),
            exactly_one=True
        )

        if location is None:
            return None

        address = location.raw.get("address", {})

        return {
            "city": (
                address.get("city")
                or address.get("town")
                or address.get("village")
            ),
            "state": address.get("state"),
            "country": address.get("country"),
            "country_code": address.get("country_code"),
            "source": "gps",
            "confidence": 1.0,
        }

    except Exception as error:
        print(f"Geocoding failed: {error}")
        return None