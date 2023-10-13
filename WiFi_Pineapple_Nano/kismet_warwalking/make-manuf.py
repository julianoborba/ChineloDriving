#!/usr/bin/env python3

# # #
# Refers to
# https://github.com/wireshark/wireshark/blob/master/tools/make-manuf.py
# # #

import time
import csv
import html
import io
import os
import re
import sys
import urllib.request, urllib.error, urllib.parse

have_icu = False
try:
    import icu
    have_icu = True
except ImportError:
    pass

def exit_msg(msg=None, status=1):
    if msg is not None:
        sys.stderr.write(msg + '\n\n')
    sys.stderr.write(__doc__ + '\n')
    sys.exit(status)

def open_url(url):

    if len(sys.argv) > 1:
        url_path = os.path.join(sys.argv[1], url[1])
        url_fd = open(url_path)
        body = url_fd.read()
        url_fd.close()
    else:
        url_path = '/'.join(url)

        req_headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0' }
        try:
            req = urllib.request.Request(url_path, headers=req_headers)
            response = urllib.request.urlopen(req)
            body = response.read().decode('UTF-8', 'replace')
        except Exception:
            exit_msg('Error opening ' + url_path)

        time.sleep(60)
    return body

general_terms = '|'.join([
    ' a +s\\b', # A/S and A.S. but not "As" as in "Connect As".
    ' ab\\b', # Also follows "Oy", which is covered below.
    ' ag\\b',
    ' b ?v\\b',
    ' closed joint stock company\\b',
    ' co\\b',
    ' company\\b',
    ' corp\\b',
    ' corporation\\b',
    ' corporate\\b',
    ' de c ?v\\b', # Follows "S.A.", which is covered separately below.
    ' gmbh\\b',
    ' holding\\b',
    ' inc\\b',
    ' incorporated\\b',
    ' jsc\\b',
    ' kg\\b',
    ' k k\\b', # "K.K." as in "kabushiki kaisha", but not "K+K" as in "K+K Messtechnik".
    ' limited\\b',
    ' llc\\b',
    ' ltd\\b',
    ' n ?v\\b',
    ' oao\\b',
    ' of\\b',
    ' open joint stock company\\b',
    ' ooo\\b',
    ' oü\\b',
    ' oy\\b',
    ' oyj\\b',
    ' plc\\b',
    ' pty\\b',
    ' pvt\\b',
    ' s ?a ?r ?l\\b',
    ' s ?a\\b',
    ' s ?p ?a\\b',
    ' sp ?k\\b',
    ' s ?r ?l\\b',
    ' systems\\b',
    '\\bthe\\b',
    ' zao\\b',
    ' z ?o ?o\\b'
    ])

skip_start = [
    'shengzen',
    'shenzhen',
    'beijing',
    'shanghai',
    'wuhan',
    'hangzhou',
    'guangxi',
]

special_case = {
    "Advanced Micro Devices": "AMD",
}

def shorten(manuf):
    '''Convert a long manufacturer name to abbreviated and short names'''
    manuf = ' '.join(manuf.split())
    orig_manuf = manuf
    if manuf.isupper():
        manuf = manuf.title()
    manuf = re.sub(r"\(.*\)", '', manuf)
    manuf = manuf.replace(" a ", " ")
    manuf = re.sub(r"[\"',./:()+-]", ' ', manuf)
    manuf = manuf.replace(" & ", " ")
    plain_manuf = re.sub(general_terms, '', manuf, flags=re.IGNORECASE)
    if not all(s == ' ' for s in plain_manuf):
        manuf = plain_manuf

    manuf = manuf.strip()

    if manuf in special_case.keys():
        manuf = special_case[manuf]

    split = manuf.split()
    if len(split) > 1 and split[0].lower() in skip_start:
        manuf = ' '.join(split[1:])

    manuf = re.sub(r'\s+', '', manuf)

    if len(manuf) < 1:
        sys.stderr.write('Manufacturer "{}" shortened to nothing.\n'.format(orig_manuf))
        sys.exit(1)

    trunc_len = 12

    if have_icu:
        bi_ci = icu.BreakIterator.createCharacterInstance(icu.Locale('en_US'))
        bi_ci.setText(manuf)
        bounds = list(bi_ci)
        bounds = bounds[0:trunc_len]
        trunc_len = bounds[-1]

    manuf = manuf[:trunc_len]

    if manuf.lower() == orig_manuf.lower():
        return [manuf, None]

    mixed_manuf = orig_manuf
    mixed_manuf = re.sub(r'\s+\.', '.', mixed_manuf)
    if mixed_manuf.upper() == mixed_manuf:
        mixed_manuf = mixed_manuf.title()

    return [manuf, mixed_manuf]

MA_L = 'MA_L'
MA_M = 'MA_M'
MA_S = 'MA_S'

def prefix_to_oui(prefix, prefix_map):
    pfx_len = int(len(prefix) * 8 / 2)
    prefix24 = prefix[:6]
    oui24 = ':'.join(hi + lo for hi, lo in zip(prefix24[0::2], prefix24[1::2]))

    if pfx_len == 24:
        return oui24, MA_L

    oui = prefix.ljust(12, '0')
    oui = ':'.join(hi + lo for hi, lo in zip(oui[0::2], oui[1::2]))
    if pfx_len == 28:
        kind = MA_M
    elif pfx_len == 36:
        kind = MA_S
    prefix_map[oui24] = kind

    return '{}/{:d}'.format(oui, int(pfx_len)), kind

def main():
    this_dir = os.path.dirname(__file__)
    manuf_path = os.path.join('epan', 'manuf')

    ieee_d = {
        'OUI':   { 'url': ["https://standards-oui.ieee.org/oui/", "oui.csv"], 'min_entries': 1000 },
        'CID':   { 'url': ["https://standards-oui.ieee.org/cid/", "cid.csv"], 'min_entries': 75 },
        'IAB':   { 'url': ["https://standards-oui.ieee.org/iab/", "iab.csv"], 'min_entries': 1000 },
        'OUI28': { 'url': ["https://standards-oui.ieee.org/oui28/", "mam.csv"], 'min_entries': 1000 },
        'OUI36': { 'url': ["https://standards-oui.ieee.org/oui36/", "oui36.csv"], 'min_entries': 1000 },
    }
    oui_d = {
        MA_L: {},
        MA_M: {},
        MA_S: {},
    }

    min_total = 35000; # 35830 as of 2018-09-05
    total_added = 0

    ieee_db_l = ['OUI', 'OUI28', 'OUI36', 'CID', 'IAB']

    prefix_map = {}

    for db in ieee_db_l:
        db_url = ieee_d[db]['url']
        ieee_d[db]['skipped'] = 0
        ieee_d[db]['added'] = 0
        ieee_d[db]['total'] = 0
        print('Merging {} data from {}'.format(db, db_url))
        body = open_url(db_url)
        ieee_csv = csv.reader(body.splitlines())

        next(ieee_csv)
        for ieee_row in ieee_csv:
            oui, kind = prefix_to_oui(ieee_row[1].upper(), prefix_map)
            manuf = ieee_row[2].strip()
            manuf = html.unescape(manuf)
            manuf = manuf.replace('\\', '/')
            if manuf == 'IEEE Registration Authority':
                continue
            if manuf == 'Private':
                continue
            if oui in oui_d[kind]:
                action = 'Skipping'
                print('{} - {} IEEE "{}" in favor of "{}"'.format(oui, action, manuf, oui_d[kind][oui]))
                ieee_d[db]['skipped'] += 1
            else:
                oui_d[kind][oui] = shorten(manuf)
                ieee_d[db]['added'] += 1
            ieee_d[db]['total'] += 1

        if ieee_d[db]['total'] < ieee_d[db]['min_entries']:
            exit_msg("Too few {} entries. Got {}, wanted {}".format(db, ieee_d[db]['total'], ieee_d[db]['min_entries']))
        total_added += ieee_d[db]['total']

    if total_added < min_total:
        exit_msg("Too few total entries ({})".format(total_added))

    try:
        manuf_fd = io.open(manuf_path, 'w', encoding='UTF-8')
    except Exception:
        exit_msg("Couldn't open manuf file for reading ({}) ".format(manuf_path))

    keys = list(prefix_map.keys())
    keys.sort()
    for oui in keys:
        manuf_fd.write("{}:{}:{}\t{}\n".format(oui[0:2], oui[3:5], oui[6:8], prefix_map[oui]))

    keys = list(oui_d[MA_L].keys())
    keys.sort()
    for oui in keys:
        short = oui_d[MA_L][oui][0]
        if oui_d[MA_L][oui][1]:
            long = oui_d[MA_L][oui][1]
        else:
            long = short
        line = "{}:{}:{}\t{}".format(oui[0:2], oui[3:5], oui[6:8], short)
        sep = 44 - len(line)
        if sep <= 0:
            sep = 0
        line += sep * ' '
        line += "# {}\n".format(long.replace('"', '\\"'))
        manuf_fd.write(line)

    keys = list(oui_d[MA_M].keys())
    keys.sort()
    for oui in keys:
        short = oui_d[MA_M][oui][0]
        if oui_d[MA_M][oui][1]:
            long = oui_d[MA_M][oui][1]
        else:
            long = short
        line = "{}:{}:{}:{}\t{}".format(oui[0:2], oui[3:5], oui[6:8], oui[9:11], short)
        sep = 50 - len(line)
        if sep <= 0:
            sep = 0
        line += sep * ' '
        line += "# {}\n".format(long.replace('"', '\\"'))
        manuf_fd.write(line)

    keys = list(oui_d[MA_S].keys())
    keys.sort()
    for oui in keys:
        short = oui_d[MA_S][oui][0]
        if oui_d[MA_S][oui][1]:
            long = oui_d[MA_S][oui][1]
        else:
            long = short
        line = "{}:{}:{}:{}:{}\t{}".format(oui[0:2], oui[3:5], oui[6:8], oui[9:11], oui[12:14], short)
        sep = 56 - len(line)
        if sep <= 0:
            sep = 0
        line += sep * ' '
        line += "# {}\n".format(long.replace('"', '\\"'))
        manuf_fd.write(line)

    manuf_fd.close()

    for db in ieee_d:
        print('{:<20}: {}'.format('IEEE ' + db + ' added', ieee_d[db]['added']))
    print('{:<20}: {}'.format('Total added', total_added))

    print()
    for db in ieee_d:
        print('{:<20}: {}'.format('IEEE ' + db + ' total', ieee_d[db]['total']))

    print()
    for db in ieee_d:
        print('{:<20}: {}'.format('IEEE ' + db + ' skipped', ieee_d[db]['skipped']))

if __name__ == '__main__':
    main()

