#!/bin/bash
# rename files with the date of it's creation
for f in PW-NA-GO-TC-HI*.pcap; do mv -n "$f" "$(date -r "$f" +"%Y%m%d_%H%M%S").pcap"; done
for f in AI-RO-DU-MP*.netxml; do mv -n "$f" "$(date -r "$f" +"%Y%m%d_%H%M%S").netxml"; done
