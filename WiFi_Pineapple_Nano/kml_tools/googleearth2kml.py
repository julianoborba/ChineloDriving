#!/usr/bin/env python3

# # #
# Refers to
# https://www.salecker.org/software/netxml2kml.html
# # #

import optparse
import os
import re
from bs4 import BeautifulSoup


def parse_placemark_node(node):
    
    styleurl = node.find('styleurl').string
    name = node.find('name').string
    desc = node.find('description').string
    coordinates = node.find('coordinates').string
    return {
        'styleurl': styleurl,
        'name': name,
        'description': desc,
        'coordinates': coordinates
    }


def parse_kml(filepath):

    print(f'[*] Parsing {filepath}')

    soup = None
    with open(filepath, encoding='latin-1') as file:
        soup = BeautifulSoup(file, 'lxml')

    placemarks = [parse_placemark_node(p) for p in soup.find_all('placemark')]
    return placemarks


def get_file_list(path):

    pattern = re.compile('.*\.kml$')
    files = [f for f in os.listdir(path) if pattern.match(f)]
    return files


def merge_data(data1, data2):

    raw_lon_1 = data1['coordinates'].split(',')[0]
    raw_lon_2 = data2['coordinates'].split(',')[0]
    raw_lat_1 = data1['coordinates'].split(',')[1]
    raw_lat_2 = data2['coordinates'].split(',')[1]

    raw_lon_1 = "{:.6f}".format(float(raw_lon_1))
    raw_lon_2 = "{:.6f}".format(float(raw_lon_2))
    raw_lat_1 = "{:.6f}".format(float(raw_lat_1))
    raw_lat_2 = "{:.6f}".format(float(raw_lat_2))

    lon = "{:.6f}".format(float(raw_lon_1) + float(raw_lon_2))
    lat = "{:.6f}".format(float(raw_lat_1) + float(raw_lat_2))

    data1['coordinates'] = f'{float(lon)},{float(lat)}'

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


def generate_klm(placemarks, out):

    soup = BeautifulSoup(features='xml')
    kml = soup.new_tag('kml', xmlns='http://www.opengis.net/kml/2.2')
    doc = soup.new_tag('Document')

    # doc.append(generate_style(soup, 'standard', 'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'))
    # doc.append(generate_style(soup, 'open', 'http://maps.google.com/mapfiles/kml/paddle/grn-stars.png'))
    doc.append(generate_style(soup, 'standard', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/WiFi_Pineapple_Nano/kml_tools/closed.png'))
    doc.append(generate_style(soup, 'open', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/WiFi_Pineapple_Nano/kml_tools/open.png'))
    doc.append(generate_style(soup, 'clear', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/WiFi_Pineapple_Nano/kml_tools/clear.png'))
    doc.append(generate_style(soup, 'clients', 'https://raw.githubusercontent.com/julianoborba/ChineloDriving/main/WiFi_Pineapple_Nano/kml_tools/clients.png'))

    for k, p in placemarks.items():
        pm = soup.new_tag('Placemark')

        name = soup.new_tag('name')
        name.string = f'{p["name"]}'

        description = soup.new_tag('description')
        description.string = f'{p["description"]}'

        pt = soup.new_tag('Point')
        coo = soup.new_tag('coordinates')

        split_coordinates = p['coordinates'].split(',')
        raw_lon = split_coordinates[0]
        raw_lat = split_coordinates[1]
        if p['seen'] > 1:
            lon = float(raw_lon) / p['seen']
            lat = float(raw_lat) / p['seen'] 
            coo.string = f'{"{:.6f}".format(lon)},{"{:.6f}".format(lat)}'
        else:
            coo.string = f'{"{:.6f}".format(float(raw_lon))},{"{:.6f}".format(float(raw_lat))}'

        stu = soup.new_tag('styleUrl')
        if '#standard' in f'{p["styleurl"]}':
            stu.string = '#standard'
        if '#open' in f'{p["styleurl"]}':
            stu.string = '#open'
        if '#clear' in f'{p["styleurl"]}':
            stu.string = '#clear'
        if '#clients' in f'{p["styleurl"]}':
            stu.string = '#clients'

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

    parser = optparse.OptionParser('usage%prog -d <kml directory> -o <output file>')
    parser.add_option('-d', dest='dirpath', type='string', help='specify the directory containing the kml file')
    parser.add_option('-o', dest='output', type='string', help='specify the output file name')
    (options, args) = parser.parse_args()

    dirpath = options.dirpath
    out = options.output

    if dirpath == None or out == None:
        print(parser.usage)
        exit(0)

    files = get_file_list(dirpath)
    pmlist = [parse_kml(os.path.join(dirpath, f)) for f in files]

    unique_places = {}
    for pl in pmlist:
        for p in pl:
            if p and 'name' in p and p['name']:
                if p['name'] not in unique_places:
                    unique_places[p['name']] = p
                    unique_places[p['name']]['seen'] = 1
                else:
                    unique_places[p['name']]['seen'] = unique_places[p['name']]['seen'] + 1
                    unique_places[p['name']] = merge_data(
                        unique_places[p['name']], p
                    )

    generate_klm(unique_places, out)


if __name__ == '__main__':
    main()
