import os
import math
from folium import Map
from folium import Marker
from json import loads


def apply_haversine(lat1, lon1, lat2, lon2):
    radius = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(radius * c, 2)


def filter_coordinates(coordinates, lat1, lon1, max_distance):
    return [(lat, lon) for lat, lon in coordinates if apply_haversine(lat1, lon1, lat, lon) <= max_distance]


def obtain_gps_avg(coordinates):
    if not coordinates:
        return None, None
    lat1, lon1 = coordinates[0]
    coordinates = filter_coordinates(coordinates, lat1, lon1, 0.10)
    total_x = 0
    total_y = 0
    total_z = 0
    for lat, lon in coordinates:
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        total_x += math.cos(lat_rad) * math.cos(lon_rad)
        total_y += math.cos(lat_rad) * math.sin(lon_rad)
        total_z += math.sin(lat_rad)
    avg_x = total_x / len(coordinates)
    avg_y = total_y / len(coordinates)
    avg_z = total_z / len(coordinates)
    avg_lon = math.atan2(avg_y, avg_x)
    hyp = math.sqrt(avg_x**2 + avg_y**2)
    avg_lat = math.atan2(avg_z, hyp)
    return math.degrees(avg_lat), math.degrees(avg_lon)


def plot_coordinates(root_folder):
    coordinates = []
    essid = ''
    bssid = '' # BSSID of choice
    names = sorted(os.listdir(root_folder))
    for folder_name in names:
        folder_path_full = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path_full):
            paths = sorted(os.listdir(folder_path_full))
            for file_name in paths:
                file_path = os.path.join(folder_path_full, file_name)
                if file_name.endswith(".json"):
                    with open(file_path, encoding='latin-1') as file:
                        try:
                            json_data = loads(file.read())
                        except:
                            json_data = {}
                        if bssid not in json_data.get('Mac', ''):
                            continue
                        essid = json_data.get('Hostname', '')
                        coordinates += [(
                            float(json_data.get('Latitude', 0)),
                            float(json_data.get('Longitude', 0))
                        )]
                        avg_latitude, avg_longitude = obtain_gps_avg(
                            coordinates
                        )
    if avg_latitude and avg_longitude:
        map_center = [avg_latitude, avg_longitude]
        my_map = Map(location=map_center, zoom_start=60)
        Marker(
            location=[float(avg_latitude), float(avg_longitude)],
            popup=f"{essid}<br>{bssid}"
        ).add_to(my_map)
        output_file_path = os.path.join(root_folder, 'map.html')
        my_map.save(output_file_path)


if __name__ == "__main__":
    # sample folder structure
    # ROOT_FOLDER/
    # ├── 1
    # │   ├── AAAAMMDD_ESSID_BSSID.gps.json
    # │   └── AAAAMMDD_ESSID_BSSID.gps.json
    # ├── 2
    # │   └── AAAAMMDD_ESSID_BSSID.gps.json
    plot_coordinates('ROOT_FOLDER')
