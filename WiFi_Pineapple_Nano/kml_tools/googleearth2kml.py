#!/usr/bin/env python3

import optparse
import os
import re
import math
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


def parse_placemark_node(node):
    
    styleurl = node.find('styleurl').string
    name = node.find('name').string
    description = node.find('description').string
    coordinates = node.find('coordinates').string
    return {
        'styleurl': styleurl,
        'name': name,
        'description': description,
        'coordinates': coordinates
    }


def parse_kml(filepath):

    print(f'[*] Parsing {filepath}')

    soup = None
    with open(filepath, encoding='latin-1') as file:
        soup = BeautifulSoup(file, 'lxml')

    return [parse_placemark_node(placemark) for placemark in soup.find_all('placemark')]


def get_file_list(path):

    pattern = re.compile('.*\.kml$')
    return [f for f in os.listdir(path) if pattern.match(f)]


def merge_data(data1, data2):

    print(f'[*] Merging [{data1["name"]}] AP data seen {data1["seen"]} times')
    raw_lon_1 = data1['coordinates'].split(',')[0]
    raw_lon_2 = data2['coordinates'].split(',')[0]
    raw_lat_1 = data1['coordinates'].split(',')[1]
    raw_lat_2 = data2['coordinates'].split(',')[1]
    coordinates = [
        (float(raw_lat_1), float(raw_lon_1)),
        (float(raw_lat_2), float(raw_lon_2))
    ]
    avg_latitude, avg_longitude = obtain_gps_avg(coordinates)
    data1['coordinates'] = f'{float(avg_longitude)},{float(avg_latitude)}'
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

    for k, placemark in placemarks.items():
        new_placemark = soup.new_tag('Placemark')

        name = soup.new_tag('name')
        name.string = f'{placemark["name"]}'

        description = soup.new_tag('description')
        description.string = f'{placemark["description"]}'

        point = soup.new_tag('Point')
        coordinates = soup.new_tag('coordinates')

        coordinates.string = placemark['coordinates']

        style_url = soup.new_tag('styleUrl')
        if '#standard' in f'{placemark["styleurl"]}':
            style_url.string = '#standard'
        if '#open' in f'{placemark["styleurl"]}':
            style_url.string = '#open'
        if '#clear' in f'{placemark["styleurl"]}':
            style_url.string = '#clear'
        if '#clients' in f'{placemark["styleurl"]}':
            style_url.string = '#clients'

        point.append(coordinates)
        new_placemark.append(style_url)
        new_placemark.append(name)

        # set placemark visibitily, 0 is invisible
        visibility = soup.new_tag('visibility')
        visibility.string = '0'
        # pm.append(visibility)

        new_placemark.append(description)
        new_placemark.append(point)
        doc.append(new_placemark)

    kml.append(doc)
    soup.append(kml)

    with open(f'{out}.kml', 'w') as file:
       file.write(str(soup))


# Refers to
# https://github.com/dreadnought
# Patrick Salecker <mail@salecker.org>
# https://www.salecker.org/software/netxml2kml.html
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
    placemark_list = [parse_kml(os.path.join(dirpath, file)) for file in files]

    unique_placemark = {}
    for placemarks in placemark_list:
        for placemark in placemarks:
            if placemark and 'name' in placemark and placemark['name']:
                if placemark['name'] not in unique_placemark:
                    unique_placemark[placemark['name']] = placemark
                    unique_placemark[placemark['name']]['seen'] = 1
                else:
                    unique_placemark[placemark['name']]['seen'] = unique_placemark[placemark['name']]['seen'] + 1
                    unique_placemark[placemark['name']] = merge_data(
                        unique_placemark[placemark['name']], placemark
                    )

    generate_klm(unique_placemark, out)


if __name__ == '__main__':
    main()
