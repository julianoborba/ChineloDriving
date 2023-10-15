#!/bin/bash
#
#
COUNTNC=0    # counter for netcat retries
COUNT=0      # counter for gpsd and airodump retries
STEP=1       # step for counters
RETRYNC=10   # limit for netcat retries
RETRY=4      # limit for gpsd and airodump retries
BUTTONED=""  # variable that stores the pressed button state
#
#
ESSID_REGEX='^(?!YOUR_MANAGEMENT_AP)'
BAND='abg'
LOG_FOLDER='/sd/LEET/handshakes/AI-RO-DU-MP-00-00_full.pcap'
C_HOP=250
O_FORMAT='netxml'
W_INTERVAL=5
MON_IF='wlan2mon'
#
#
BUTTON_LOG='/tmp/button.log' # Pineapple button log
#
#
while true; do
    # if pineapple button was pressed, stop the script
    #
    BUTTONED=$(cat $BUTTON_LOG | grep "BUTTONED")
    if [ "BUTTONED" = "$BUTTONED" ]; then
        exit 0
    fi
    /bin/echo 'ok. sending gpsd command...'
    # keep sending WATCH command to gpsd with netcat
    # to WATCH for connected devices
    #
    DEVICES=''
    while true; do
        JSON=$(/usr/bin/nc -c localhost 2947 -w 6 <<EOF
?WATCH={"class":"WATCH","json":true}
EOF
)
        /bin/echo 'json response: '"$JSON"
        # until the netcat limit of retries, check if devices was found
        # a found device means gpsd found at least one gps provider device
        #
        if [ $COUNTNC -lt $RETRYNC ]; then
            DEVICES=$(/bin/echo "$JSON" | /bin/sed -n '2p' | /bin/grep -o '"devices":\[.*\]' | /bin/grep -o '\[.*\]')
            if [ "[]" = "$DEVICES" ] || [ "" = "$DEVICES" ]; then
                COUNTNC=$((COUNTNC+STEP))
                /bin/echo 'netcat attempt '$COUNTNC'/'$RETRYNC'. sleeping for 2s...'
                /bin/sleep 2s
            else
                COUNTNC=0
                break
            fi
        else
            /bin/echo 'netcat max retries exceeded'
            COUNTNC=0
            break
        fi       
    done
    /bin/echo 'got devices: /'$DEVICES'/'
    # at this point, a device was truly found
    # yet a paranoid programmer decide to check that fact anyway
    #
    if [ "[]" = "$DEVICES" ] || [ "" = "$DEVICES" ]; then
        /bin/echo 'no devices found'
        if [ $COUNT -lt $RETRY ]; then
            # if it was the very first attempt
            # a paranoid programmer decide to give
            # one more chance for the first netcat retries
            #
            if [ $COUNT -gt 0 ]; then
                # if in fact there is no devices, maybe we
                # should restart gpsd and airodump
                #
                /bin/echo 'done sending. killing airodump-ng...'
                /usr/bin/killall airodump-ng
                /bin/sleep 4s
                /bin/echo 'killing gpsd...'
                /usr/bin/killall gpsd
                /bin/sleep 4s
                /bin/echo 'done killing'
                /bin/echo 'running gpsd...'
                /sd/usr/sbin/gpsd -F /var/run/gpsd.sock udp://0.0.0.0:1337
                /bin/sleep 6s
                /bin/echo 'running airodump-ng...'
                /usr/sbin/airodump-ng -K 1 --essid-regex $ESSID_REGEX --band $BAND --gpsd --write $LOG_FOLDER -f $C_HOP --output-format $O_FORMAT --write-interval $W_INTERVAL $MON_IF > /dev/null 2>&1 &
                /bin/echo 'done running'
            fi
            COUNT=$((COUNT+STEP))
            /bin/echo 'attempt '$COUNT'/'$RETRY'. sleeping for 1m...'
            /bin/sleep 1m
        else
            # if no device can be found
            # lets rest, some human should bring a device anytime soon
            #
            /bin/echo 'max retries exceeded'
            COUNT=0
            /bin/echo 'sleeping for 5m...'
            /bin/sleep 5m
        fi
    else
        /bin/echo 'devices found'
        COUNT=0
        # in any case, after a while
        # lets just start fresh, tip of the paranoid programmer
        # first we test if the pineapple button was pressed
        # if not, we start fresh
        #
        BUTTONED=$(cat $BUTTON_LOG | grep "BUTTONED")
        if [ "BUTTONED" = "$BUTTONED" ]; then
            exit 0
        fi
        /bin/echo 'sleeping for 10m...'
        /bin/sleep 10m
        /bin/echo 'woke up. just in case, killing airodump-ng...'
        /usr/bin/killall airodump-ng
        /bin/sleep 4s
        /bin/echo 'killing gpsd...'
        /usr/bin/killall gpsd
        /bin/sleep 4s
        /bin/echo 'done killing'
        /bin/echo 'running gpsd...'
        /sd/usr/sbin/gpsd -F /var/run/gpsd.sock udp://0.0.0.0:1337
        /bin/sleep 6s
        /bin/echo 'running airodump-ng...'
        /usr/sbin/airodump-ng -K 1 --essid-regex $ESSID_REGEX --band $BAND --gpsd --write $LOG_FOLDER -f $C_HOP --output-format $O_FORMAT --write-interval $W_INTERVAL $MON_IF > /dev/null 2>&1 &
        /bin/echo 'done running'
    fi
done
