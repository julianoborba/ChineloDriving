#!/bin/bash
# zip in a way to be downloadable in PineAP interface
zip -r BE-TT-ER-CA-PZ-IP_full.pcap bettercap_gps_json
zip -r AI-RO-DU-MP-ZI-P0_full.pcap airodump_ng_netxml
rm -rf bettercap_gps_json/*
rm -rf airodump_ng_netxml/*
