#!/bin/bash
# rename files with the date of it's creation
for f in *cap; do mv -n "$f" "$(date -r "$f" +"%Y%m%d_%H%M%S").pcap"; done
