import os
from pandas import DataFrame
from folium import Map
from folium.plugins import HeatMap
from json import loads


def build_heatmap(root_folder):
    columns = ['BSSID', 'Latitude', 'Longitude', 'ESSID']
    df = DataFrame(columns=columns)
    essid = ''
    bssid = '' # BSSID of choice
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.json'):
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, encoding='latin-1') as file:
                        try:
                            json_data = loads(file.read())
                        except:
                            json_data = {}
                        if bssid not in json_data.get('Mac', ''):
                            continue
                        df = df._append(
                            {
                                'BSSID': json_data.get('Mac', ''),
                                'Latitude': json_data.get('Latitude', 0),
                                'Longitude': json_data.get('Longitude', 0),
                                'ESSID': json_data.get('Hostname', '')
                            },
                            ignore_index=True
                        )
    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    heatmap_map = Map(location=map_center, zoom_start=16)
    heat_data = [
        [row['Latitude'], row['Longitude']]
        for index, row in df.iterrows()
    ]
    HeatMap(heat_data).add_to(heatmap_map)
    output_file_path = os.path.join(root_folder, 'heatmap.html')
    heatmap_map.save(output_file_path)


if __name__ == "__main__":
    # sample folder structure
    # ROOT_FOLDER/
    # ├── 1
    # │   ├── AAAAMMDD_ESSID_BSSID.gps.json
    # │   └── AAAAMMDD_ESSID_BSSID.gps.json
    # ├── 2
    # │   └── AAAAMMDD_ESSID_BSSID.gps.json
    build_heatmap('ROOT_FOLDER')
