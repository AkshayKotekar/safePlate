"""STUB — future real restaurant/locality data source (Google Places, public
food-safety inspection datasets — spec §27). Not required for the MVP; today
app/services/restaurant_seed.py provides static/mock data instead.
"""


def search_nearby_places(locality: str) -> list[dict]:
    raise NotImplementedError("External places integration is future work — see spec §27")
