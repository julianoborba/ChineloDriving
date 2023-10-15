#!/usr/bin/env python3

# # #
# Refers to
# https://github.com/dreadnought
# Patrick Salecker <mail@salecker.org>
# https://www.salecker.org/software/netxml2kml.html
# # #

import optparse
import os
import re
from xml.sax.saxutils import escape
# from html import escape
from bs4 import BeautifulSoup


# parse strange wifi names
regex = r'(  )([a-z]|[A-Z]|\d*)([a-z]|[A-Z]|\d*)(;)'
compiler = re.compile(regex, re.I | re.S)
replacer = r'\\x\2\3'
def parse_network_node(node):

    ssid = node.find('ssid', recursive=False)

    bssid = '~Empty~' if not node.find('bssid', recursive=False) else node.find('bssid', recursive=False).string
    
    try:
        is_cloaked = 'true' in ssid.essid.attrs['cloaked']
    except:
        is_cloaked = True

    essid_raw = ssid.essid.string if not is_cloaked else 'CLOAKED'

    try:
        essid_raw = escape(essid_raw)
        essid = compiler.sub(replacer, essid_raw)
    except:
        essid = '~Empty~'
    
    gps_info = node.find('gps-info', recursive=False)

    if not gps_info:
        print(f'\t[*] EMPTY GPS BSSID [{bssid}] ESSID [{essid}]')
        return None

    avg_lat_raw = gps_info.find('avg-lat').string
    round_lat = float(avg_lat_raw) # round(float(avg_lat_raw))
    avg_lon_raw = gps_info.find('avg-lon').string
    round_lon = float(avg_lon_raw) # round(float(avg_lon_raw))

    if round_lat == 0 or round_lon == 0:
        print(f'\t[*] ZERO LAT ZERO LON BSSID [{bssid}] ESSID [{essid}]')
        # centroid of scanned area
        # round_lat = -XX.XXXXXX
        # round_lon = -XX.XXXXXX
        return None

    clients = {}
    for c in node.find_all('wireless-client', {'type': 'established'}):
        client_mac = c.find('client-mac').string

        client_manuf_raw = escape(c.find('client-manuf').string)
        client_manuf_raw = compiler.sub(replacer, client_manuf_raw)
        client_manuf = client_manuf_raw if 'Unknown' not in client_manuf_raw else 'unknown manufacturer'

        min_signal_raw = int(c.find('min_signal_dbm').string)
        max_signal_raw = int(c.find('max_signal_dbm').string)
        avg_signal = float(min_signal_raw + max_signal_raw) / 2
        client_signal = 'near AP' if round(avg_signal) > -70 else 'not so near AP'

        clients[f'client_{c.attrs["number"]}'] = {
            'mac': client_mac,
            'manuf': client_manuf,
            'signal': client_signal
        }

    try:
        last_seen = ssid.attrs['last-time']
    except:
        last_seen = '~Empty~'

    try:
        encryption = [e.string for e in ssid.find_all('encryption', recursive=False)]
    except:
        encryption = ['~Empty~']

    manufacturer = node.find('manuf', recursive=False).string
    
    try:
        captured_packets = int(ssid.packets.string)
    except:
        captured_packets = 0

    return {
        'lastupdate': last_seen,
        'essid': essid,
        'encryption': encryption,
        'bssid': bssid,
        'manuf': manufacturer,
        'packets': captured_packets,
        'gps': {'lat': round_lat, 'lon': round_lon},
        'clients': clients
    }


def parse_netxml(filepath):

    print(f'[*] Parsing {filepath}')

    soup = None
    with open(filepath, encoding='latin-1') as file:
        soup = BeautifulSoup(file, 'lxml')

    networks = [parse_network_node(n) for n in soup.find_all(
        'wireless-network', {'type': 'infrastructure'}
    )]
    return networks


def get_file_list(path):

    pattern = re.compile('.*\.netxml$')
    files = [f for f in os.listdir(path) if pattern.match(f)]
    return files


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

    # doc.append(generate_style(soup, 'standard', 'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'))
    # doc.append(generate_style(soup, 'open', 'http://maps.google.com/mapfiles/kml/paddle/grn-stars.png'))
    doc.append(generate_style(soup, 'standard', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/WiFi_Pineapple_Nano/kml_tools/closed.png'))
    doc.append(generate_style(soup, 'open', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/WiFi_Pineapple_Nano/kml_tools/open.png'))
    doc.append(generate_style(soup, 'clear', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/WiFi_Pineapple_Nano/kml_tools/clear.png'))
    doc.append(generate_style(soup, 'clients', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/WiFi_Pineapple_Nano/kml_tools/clients.png'))

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
            f'PASSW:\n~Empty~\n\n'                                      # estimated shared password in this item
            f'CLIEN:\n{clients}'                                        # clients connected at this iten
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

    parser = optparse.OptionParser('usage%prog -d <netxml directory> -o <output file>')
    parser.add_option('-d', dest='dirpath', type='string', help='specify the directory containing the netxml file')
    parser.add_option('-o', dest='output', type='string', help='specify the output file name')
    (options, args) = parser.parse_args()

    dirpath = options.dirpath
    out = options.output

    if dirpath == None or out == None:
        print(parser.usage)
        exit(0)

    files = get_file_list(dirpath)
    nnlist = [parse_netxml(os.path.join(dirpath, f)) for f in files]

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
