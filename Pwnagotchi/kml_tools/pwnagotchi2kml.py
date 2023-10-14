#!/usr/bin/env python3

# # #
# Refers to
# https://www.salecker.org/software/netxml2kml.html
# # #

import optparse
import os
import re
from json import loads
from datetime import datetime
from xml.sax.saxutils import escape
# from html import escape
from bs4 import BeautifulSoup


# parse strange wifi names
regex = r'(  )([a-z]|[A-Z]|\d*)([a-z]|[A-Z]|\d*)(;)'
replacer = r'\\x\2\3'
def parse_json(filepath):

    print(f'[*] Parsing {filepath}')

    networks = None
    with open(filepath) as file:
        json_data = loads(file.read())

        file_basename = os.path.basename(filepath)
        file_splitext = os.path.splitext(file_basename)
        file_splitext = os.path.splitext(file_splitext[0])

        essid_bssid_arr = file_splitext[0].split('_')
        
        essid_raw = essid_bssid_arr[0]
        essid_raw = escape(essid_raw)
        essid = re.sub(regex, replacer, essid_raw)
        
        bssid_raw = essid_bssid_arr[1]
        bssid = (':'.join(bssid_raw[i:i+2] for i in range(0, len(bssid_raw), 2))).upper()

        last_update_raw = datetime.strptime(
            f'{json_data["Updated"][:-14]}{json_data["Updated"][28:]}', '%Y-%m-%dT%H:%M:%S%z'
        )
        last_update = last_update_raw.strftime("%a %b %d %H:%M:%S %Y")

        networks = [{
            'lastupdate': last_update,
            'essid': essid,
            'encryption': ['Unspecified'],
            'bssid': bssid,
            'manuf': 'Unspecified',
            'packets': 1,
            'gps': {'lat': json_data['Latitude'], 'lon': json_data['Longitude']},
            'clients': None
        }]

    return networks


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

    # float() for ValueError: Unknown format code 'f' for object of type 'NavigableString'
    raw_lat_1 = "{:.6f}".format(float(data1['gps']['lat']))
    raw_lon_1 = "{:.6f}".format(float(data1['gps']['lon']))

    raw_lat_2 = "{:.6f}".format(float(data2['gps']['lat']))
    raw_lon_2 = "{:.6f}".format(float(data2['gps']['lon']))

    lat = "{:.6f}".format(float(raw_lat_1) + float(raw_lat_2))
    lon = "{:.6f}".format(float(raw_lon_1) + float(raw_lon_2))

    data1['gps']['lat'] = float(lat)
    data1['gps']['lon'] = float(lon)
    data1['packets'] = data1['packets'] + data2['packets']

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
    label_style.append(label_scale)

    style.append(label_style)
    style.append(icon_style)

    return style


def generate_klm(networks, out):

    soup = BeautifulSoup(features='xml')
    kml = soup.new_tag('kml', xmlns='http://www.opengis.net/kml/2.2')
    doc = soup.new_tag('Document')

    doc.append(generate_style(soup, 'standard', 'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'))
    doc.append(generate_style(soup, 'open', 'http://maps.google.com/mapfiles/kml/paddle/grn-stars.png'))
    #doc.append(generate_style(soup, 'standard', 'https://XXXXXXXXXXXXXXXX/closed.png'))
    #doc.append(generate_style(soup, 'open', 'https://XXXXXXXXXXXXXXXX/open.png'))
    #doc.append(generate_style(soup, 'clear', 'https://XXXXXXXXXXXXXXXX/clear.png'))
    #doc.append(generate_style(soup, 'clients', 'https://XXXXXXXXXXXXXXXX/clients.png'))

    for k, n in networks.items():
        if int(n['packets']) <= 0:
            continue

        pm = soup.new_tag('Placemark')
        
        name = soup.new_tag('name')
        name.string = f'[{n["essid"]}][{n["bssid"]}]'
        # name.string = ''
        # limit = 8
        # if f'{n["essid"]}' and len(f'{n["essid"]}') > limit:
        #    name.string = f'[{n["essid"][:limit]} ...][{n["bssid"]}]'
        # else:
        #    name.string = f'[{n["essid"]}][{n["bssid"]}]'

        clients = ''
        if n['clients']:
            for k, c in n['clients'].items():
                clients += f'- {c["mac"]}, from {c["manuf"]}, is {c["signal"]}\n'

        description = soup.new_tag('description')
        description.string = (
            f'LAUPD:\n{n["lastupdate"]}\n\n'                            # last known update date on this item
            f'SEENT:\n{n["seen"]}\n\n'                                  # how many times this item was met
            f'ESSID:\n{n["essid"]}\n\n'                                 # ESSID for that item
            f'BSSID:\n{n["bssid"]}\n\n'                                 # BSSID for that item
            f'MANUF:\n{n["manuf"]}\n\n'                                 # identified manufacturer of this item
            f'PACKE:\n{n["packets"]}\n\n'                               # estimative of how many packets was collected since last known update
            f'ENCRY:\n{" ".join(str(x) for x in n["encryption"])}\n\n'  # cipher used by that item
            f'PASSW:\~Empty~\n\n'                                       # estimated shared password in this item
            f'CLIEN:\~Empty~'                                           # clients connected at this item
        )

        pt = soup.new_tag('Point')
        coo = soup.new_tag('coordinates')

        if n['seen'] > 1:
            lon = n["gps"]["lon"] / n['seen'] 
            lat = n["gps"]["lat"] / n['seen']
            coo.string = f'{"{:.6f}".format(lon)},{"{:.6f}".format(lat)}'
        else:
            coo.string = f'{n["gps"]["lon"]},{n["gps"]["lat"]}'

        stu = soup.new_tag('styleUrl')
        if n['encryption'] == ['None'] or n['encryption'] == []:
            stu.string = '#open'
        else:
            if n['clients']:
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

    files = get_file_list(dirpath)
    nnlist = [parse_json(file) for file in files]

    unique_net = {}

    for nl in nnlist:
        for n in nl:
            if n and 'bssid' in n and n['bssid']:
                if n['bssid'] not in unique_net:
                    unique_net[n['bssid']] = n
                    unique_net[n['bssid']]['seen'] = 1
                else:
                    unique_net[n['bssid']]['seen'] = unique_net[n['bssid']]['seen'] + 1
                    unique_net[n['bssid']] = merge_data(
                        unique_net[n['bssid']], n
                    )

    generate_klm(unique_net, out)


if __name__ == '__main__':
    main()
