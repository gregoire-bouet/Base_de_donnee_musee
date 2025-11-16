import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from pathlib import Path

# -----------------------------
# 🔹 Chargement du CSV
# -----------------------------
csv_path = Path(r"C:\Users\noahb\Documents\Base_de_donnee_musee\data\cleaned\cleaneddata.csv")
df = pd.read_csv(csv_path, sep=";", encoding="utf-8")

# -----------------------------
# 🔹 Extraction de la ville
# -----------------------------
def extract_city(loc):
    if pd.isna(loc):
        return None
    # Supprimer le type (musée >, palais >, etc.)
    if ">" in loc:
        loc = loc.split(">", 1)[1].strip()
    parts = [p.strip() for p in loc.split(",")]
    if len(parts) >= 2:
        return parts[1]  # On garde la ville
    return None

df["ville"] = df["lieu de conservation"].apply(extract_city)

# -----------------------------
# 🔹 Dictionnaire manuel pour villes célèbres ou ambiguës
# -----------------------------
manual_fix_villes = {
    "Versailles": (48.804865, 2.120355),
    "Paris": (48.856613, 2.352222),
    "Nancy": (48.692054, 6.184417),
    "Bayonne": (43.49255, -1.47443),
    "Stockholm": (59.329323, 18.068581),
    "Berlin": (52.520008, 13.404954),
    "Mulhouse": (47.747, 7.335),
    "Meudon": (48.8147, 2.2518),
    "Amiens": (49.895, 2.295),
    "Monaco": (43.7384, 7.4246),  # Important pour corriger la localisation
    # Ajouter d'autres villes si besoin
}

# -----------------------------
# 🔹 Setup Geocoder
# -----------------------------
geolocator = Nominatim(user_agent="musee_geocoder", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=5)

# -----------------------------
# 🔹 Fonction pour géocoder une ville
# -----------------------------
def get_city_coordinates(city, country=None):
    if city is None:
        return None, None
    key = f"{city}, {country}" if country else city
    # Vérifier dans le dictionnaire manuel
    if city in manual_fix_villes:
        lat, lon = manual_fix_villes[city]
        print(f"MANUAL FIX: {city} => {lat}, {lon}")
        return lat, lon
    try:
        query = key
        location = geocode(query)
        if location:
            print(f"OK: {city} => {location.latitude}, {location.longitude}")
            return location.latitude, location.longitude
        else:
            print(f"NOT FOUND: {city}")
            return None, None
    except Exception as e:
        print(f"ERROR: {city} => {e}")
        return None, None

# -----------------------------
# 🔹 Géocodage des villes uniques
# -----------------------------
villes_unique = df["ville"].dropna().unique()
coords_dict = {}

for ville in villes_unique:
    lat, lon = get_city_coordinates(ville)  # pas besoin de forcer France
    coords_dict[ville] = (lat, lon)

# -----------------------------
# 🔹 Ajouter les coordonnées de la ville à chaque musée
# -----------------------------
df["latitude"] = df["ville"].map(lambda x: coords_dict.get(x, (None, None))[0])
df["longitude"] = df["ville"].map(lambda x: coords_dict.get(x, (None, None))[1])

# -----------------------------
# 🔹 Sauvegarde
# -----------------------------
output_csv = Path(r"C:\Users\noahb\Documents\Base_de_donnee_musee\data\cleaned\cleaneddata_geocoded_villes.csv")
df.to_csv(output_csv, index=False, sep=";", encoding="utf-8")
print(f"✅ CSV sauvegardé : {output_csv}")
