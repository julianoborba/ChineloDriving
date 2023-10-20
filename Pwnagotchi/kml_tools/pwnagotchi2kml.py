#!/usr/bin/env python3

import optparse
import os
import re
import math
from json import loads
from datetime import datetime
from bs4 import BeautifulSoup


# GPT generated
def obtain_gps_avg(coordinates):

    if not coordinates:
        return None, None

    total_x = 0
    total_y = 0
    total_z = 0

    for lat, lon in coordinates:
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        # Convert latitude and longitude to Cartesian coordinates
        total_x += math.cos(lat_rad) * math.cos(lon_rad)
        total_y += math.cos(lat_rad) * math.sin(lon_rad)
        total_z += math.sin(lat_rad)

    avg_x = total_x / len(coordinates)
    avg_y = total_y / len(coordinates)
    avg_z = total_z / len(coordinates)

    # Convert the average Cartesian coordinates back to latitude and longitude
    avg_lon = math.atan2(avg_y, avg_x)
    hyp = math.sqrt(avg_x**2 + avg_y**2)
    avg_lat = math.atan2(avg_z, hyp)

    # Convert latitude and longitude back to degrees and return
    return math.degrees(avg_lat), math.degrees(avg_lon)


def parse_json(filepath):

    print(f'[*] Parsing {filepath}')

    with open(filepath, encoding='latin-1') as file:
        
        try:
            json_data = loads(file.read())
        except:
            print(f'\t[*] Problem parsing file {filepath}')
            return {}

        # expected filename format {essid}_{bssid}.{plugin}-gps.json
        file_basename = os.path.basename(filepath)
        file_splitext = os.path.splitext(file_basename)
        file_splitext = os.path.splitext(file_splitext[0])

        essid_bssid_arr = file_splitext[0].split('_')
        
        essid = essid_bssid_arr[0]
        
        bssid_raw = essid_bssid_arr[1]
        bssid = (':'.join(bssid_raw[i:i+2] for i in range(0, len(bssid_raw), 2))).upper()

        last_update_raw = datetime.strptime(
            f'{json_data["Updated"][:-14]}{json_data["Updated"][28:]}', '%Y-%m-%dT%H:%M:%S%z'
        )
        last_update = last_update_raw.strftime("%a %b %d %H:%M:%S %Y")

        clients = {}
        #for c in json_data['Clients']:
        #    client_mac = c['mac']
        #    client_manuf = c['vendor'] if c['vendor'] else 'unknown manufacturer'
        #    client_signal = 'near AP' if c['rssi'] > -70 else 'not so near AP'
        #    clients[f'{client_mac.upper()}'] = {
        #        'mac': client_mac.upper(),
        #        'manuf': client_manuf,
        #        'signal': client_signal
        #    }

        return {
            'lastupdate': last_update,
            'essid': essid,
            'encryption': '~Empty~',
            'bssid': bssid,
            'manuf': '~Empty~',
            'packets': 0,
            'gps': {'lat': json_data['Latitude'], 'lon': json_data['Longitude']},
            'clients': clients
        }


found_files = []
def get_file_list(location):

    pattern = re.compile('.*\.json$')
    paths = os.listdir(location)
    for artifact in paths:
        if os.path.isfile(os.path.join(location,artifact)):
            if pattern.match(artifact):
                found_files.append(os.path.join(location,artifact))
        elif os.path.isdir(os.path.join(location,artifact)):
            get_file_list(os.path.join(location,artifact))
        else:
            print(f'artifact neither directory nor file {os.path.join(location,artifact)}')
    return found_files


def merge_data(data1, data2):

    print(f'[*] Merging [{data1["essid"]}] AP data seen {data1["seen"]} times')
    data1['lastupdate'] = data2['lastupdate']
    data1['packets'] = data1['packets'] + data2['packets']
    data1['clients'].update(data2['clients'])
    if data2['essid']:
        data1['essid'] = data2['essid'] + ' [U]'
    if data2['manuf']:
        data1['manuf'] = data2['manuf'] + ' [U]'
    if '~Empty~' not in data2['encryption']:
        data1['encryption'] = data2['encryption'] + ' [U]'
    coordinates = [
        (float(data1['gps']['lat']), float(data1['gps']['lon'])),
        (float(data2['gps']['lat']), float(data2['gps']['lon']))
    ]
    avg_latitude, avg_longitude = obtain_gps_avg(coordinates)
    data1['gps']['lat'] = float(avg_latitude)
    data1['gps']['lon'] = float(avg_longitude)
    return data1


def generate_style(soup, id, icon_src):

    style = soup.new_tag('Style', id=id)

    icon_style = soup.new_tag('IconStyle')
    icon_scale = soup.new_tag('scale')
    icon_scale.string = '0.4'
    icon = soup.new_tag('Icon')
    href = soup.new_tag('href')
    href.string = icon_src
    icon.append(href)
    icon_style.append(icon_scale)
    icon_style.append(icon)

    label_style = soup.new_tag('LabelStyle')
    label_scale = soup.new_tag('scale')
    label_scale.string = '0.6'
    label_color = soup.new_tag('color')
    label_color.string = 'ff5ac3ff'
    label_style.append(label_scale)
    label_style.append(label_color)

    style.append(label_style)
    style.append(icon_style)

    return style


def generate_klm(networks, out):

    soup = BeautifulSoup(features='xml')
    kml = soup.new_tag('kml', xmlns='http://www.opengis.net/kml/2.2')
    doc = soup.new_tag('Document')

    #doc.append(generate_style(soup, 'standard', 'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'))
    #doc.append(generate_style(soup, 'open', 'http://maps.google.com/mapfiles/kml/paddle/grn-stars.png'))
    doc.append(generate_style(soup, 'standard', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/Pwnagotchi/kml_tools/closed.png'))
    doc.append(generate_style(soup, 'open', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/Pwnagotchi/kml_tools/open.png'))
    doc.append(generate_style(soup, 'clear', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/Pwnagotchi/kml_tools/clear.png'))
    doc.append(generate_style(soup, 'clients', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/Pwnagotchi/kml_tools/clients.png'))

    for k, network in networks.items():
        pm = soup.new_tag('Placemark')
        
        name = soup.new_tag('name')
        name.string = f'[{network["essid"]}][{network["bssid"]}]'
        # name.string = ''
        # limit = 8
        # if f'{n["essid"]}' and len(f'{n["essid"]}') > limit:
        #    name.string = f'[{n["essid"][:limit]} ...][{n["bssid"]}]'
        # else:
        #    name.string = f'[{n["essid"]}][{n["bssid"]}]'

        clients = ''
        if network['clients']:
            for k, c in network['clients'].items():
                clients += f'- {c["mac"]}, from {c["manuf"]}, is {c["signal"]}\n'
        if not clients:
            clients = '~Empty~'

        manuf = network['manuf']
        if not manuf:
            manuf = '~Empty~'

        description = soup.new_tag('description')
        description.string = (
            f'LAUPD:\n{network["lastupdate"]}\n\n'         # last known update date on this item
            f'SEENT:\n{network["seen"]}\n\n'               # how many times this item was met
            f'ESSID:\n{network["essid"]}\n\n'              # ESSID for that item
            f'BSSID:\n{network["bssid"]}\n\n'              # BSSID for that item
            f'MANUF:\n{manuf}\n\n'                         # identified manufacturer of this item
            f'PACKE:\n{network["packets"]}\n\n'            # estimative of how many packets was collected since last known update
            f'ENCRY:\n{network["encryption"]}\n\n'         # cipher used by that item
            f'PASSW:\n~Empty~\n\n'                         # estimated shared password in this item
            f'CLIEN:\n{clients}'                           # clients connected at this item
        )

        pt = soup.new_tag('Point')
        coo = soup.new_tag('coordinates')
        coo.string = f'{network["gps"]["lon"]},{network["gps"]["lat"]}'

        stu = soup.new_tag('styleUrl')
        is_open_network = not network['encryption'] or 'OPEN' in network['encryption']
        is_possibly_open_network = '~Empty~' in network['encryption'] and network["packets"] > 0
        if is_open_network or is_possibly_open_network:
            stu.string = '#open'
        else:
            if network['clients']:
                stu.string = '#clients'
            else:
                stu.string = '#standard'

        pt.append(coo)
        pm.append(stu)
        pm.append(name)

        # set placemark visibitily, 0 is invisible
        visibility = soup.new_tag('visibility')
        visibility.string = '0'
        # pm.append(visibility)

        pm.append(description)
        pm.append(pt)
        doc.append(pm)

    kml.append(doc)
    soup.append(kml)

    with open(f'{out}.kml', 'w') as file:
        file.write(str(soup))


# Refers to
# https://github.com/dreadnought
# Patrick Salecker <mail@salecker.org>
# https://www.salecker.org/software/netxml2kml.html
def main():

    parser = optparse.OptionParser('usage%prog -d <json directory> -o <output file>')
    parser.add_option('-d', dest='dirpath', type='string', help='specify the directory containing the json file')
    parser.add_option('-o', dest='output', type='string', help='specify the output file name')
    (options, args) = parser.parse_args()

    dirpath = options.dirpath
    out = options.output

    if dirpath == None or out == None:
        print(parser.usage)
        exit(0)

    files = sorted(get_file_list(dirpath))
    networks = [parse_json(file) for file in files]

    unique_network = {}

    for network in networks:
        if network and 'bssid' in network and network['bssid']:
            if network['bssid'] not in unique_network:
                unique_network[network['bssid']] = network
                unique_network[network['bssid']]['seen'] = 1
            else:
                unique_network[network['bssid']]['seen'] = unique_network[network['bssid']]['seen'] + 1
                unique_network[network['bssid']] = merge_data(
                    unique_network[network['bssid']], network
                )

    generate_klm(unique_network, out)


if __name__ == '__main__':
    main()
