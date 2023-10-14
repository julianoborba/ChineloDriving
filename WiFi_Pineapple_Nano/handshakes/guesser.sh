#!/bin/bash
# sample for guessing data from handshakes
hcxpcapngtool -o HC_DUMP ./*
hashcat -m 22000 HC_DUMP -a 3 -w 3 '?d?d?d?d?d?d?d?d'
