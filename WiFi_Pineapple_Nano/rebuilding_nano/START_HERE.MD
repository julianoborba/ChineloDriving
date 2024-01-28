## Put Pineapple Nano in recovery mode

* [https://docs.hak5.org/wifi-pineapple-6th-gen-nano-tetra/faq-troubleshooting/firmware-recovery](https://docs.hak5.org/wifi-pineapple-6th-gen-nano-tetra/faq-troubleshooting/firmware-recovery)

```
sudo ifconfig YOUR_PINE_ETH 192.168.1.2 netmask 255.255.255.0 up
```

Enter 192.168.1.1, use browser incognito mode.

## Rebuilding Pineapple Nano firmware, with Pineapple Termidor

* Complete document and important notes by xchwarze at [https://github.com/xchwarze/wifi-pineapple-cloner/blob/master/build.md](https://github.com/xchwarze/wifi-pineapple-cloner/blob/master/build.md)
* [https://github.com/xchwarze/wifi-pineapple-cloner](https://github.com/xchwarze/wifi-pineapple-cloner)

The commands below are self explanatory. Follow the order.

```
sudo apt install binwalk
```

Install sasquatch to extract non-standard SquashFS images.

```
sudo apt-get install zlib1g-dev liblzma-dev liblzo2-dev
git clone https://github.com/devttys0/sasquatch
(cd sasquatch && ./build.sh)
```

From inside the sasquatch directory apply the fix for sasquatch (I had problems in Linux Mint at first).

```
wget https://raw.githubusercontent.com/devttys0/sasquatch/82da12efe97a37ddcd33dba53933bc96db4d7c69/patches/patch0.txt
mv patch0.txt patches
./build.sh
```

The steps below are from Pineapple Termidor documentation.

You can build your own Wifi Pineapple with other hardware, but here I'm rebuilding the Nano itself.

```
sudo apt install php-cli
```

```
git clone https://github.com/xchwarze/wifi-pineapple-cloner.git
cd wifi-pineapple-cloner/
```

```
wget https://www.wifipineapple.com/downloads/nano/latest -O basefw.bin
binwalk basefw.bin -e --preserve-symlinks
mv _basefw.bin.extracted/squashfs-root/ rootfs-base
```

```
php tools/opkg-parser.php rootfs-base/usr/lib/opkg/status
```

```
chmod +x tools/copier.sh
tools/copier.sh lists/nano.filelist rootfs-base rootfs
chmod +x tools/fs-patcher.sh
tools/fs-patcher.sh mips nano rootfs
```

Download de oficial imagebuilder from OpenWRT.

* [https://downloads.openwrt.org/releases/19.07.9/targets/ar71xx/generic/](https://downloads.openwrt.org/releases/19.07.9/targets/ar71xx/generic/)

```
tar xJf openwrt-imagebuilder-19.07.9-ar71xx-generic.Linux-x86_64.tar.xz
cd openwrt-imagebuilder-19.07.9-ar71xx-generic.Linux-x86_64/
```

```
export SOURCE_DATE_EPOCH=1
make image PROFILE=wifi-pineapple-nano PACKAGES="at autossh base-files block-mount ca-certificates chat dnsmasq e2fsprogs ethtool firewall hostapd-utils ip6tables iperf3 iwinfo kmod-crypto-manager kmod-fs-ext4 kmod-fs-nfs kmod-fs-vfat kmod-gpio-button-hotplug kmod-ipt-offload kmod-leds-gpio kmod-ledtrig-default-on kmod-ledtrig-netdev kmod-ledtrig-timer kmod-mt76x2u kmod-nf-nathelper kmod-rt2800-usb kmod-rtl8187 kmod-rtl8192cu kmod-scsi-generic kmod-usb-acm kmod-usb-net-asix kmod-usb-net-asix-ax88179 kmod-usb-net-qmi-wwan kmod-usb-net-rndis kmod-usb-net-sierrawireless kmod-usb-net-smsc95xx kmod-usb-ohci kmod-usb-storage-extras kmod-usb-uhci kmod-usb2 libbz2-1.0 libcurl4 libelf1 libffi libgmp10 libiconv-full2 libintl libltdl7 libnet-1.2.x libnl200 libreadline8 libustream-mbedtls20150806 libxml2 logd macchanger mtd nano ncat netcat nginx odhcp6c odhcpd-ipv6only openssh-client openssh-server openssh-sftp-server openssl-util php7-cgi php7-fpm php7-mod-hash php7-mod-json php7-mod-mbstring php7-mod-openssl php7-mod-session php7-mod-sockets php7-mod-sqlite3 ppp ppp-mod-pppoe procps-ng-pkill procps-ng-ps python-logging python-openssl python-sqlite3 rtl-sdr ssmtp tcpdump uci uclibcxx uclient-fetch urandom-seed urngd usb-modeswitch usbreset usbutils wget wireless-tools wpad busybox libatomic1 libstdcpp6 opkg uboot-envtools kmod-usb2 kmod-usb-storage-uas -wpad-basic" FILES=../rootfs
```

```
cp bin/targets/ar71xx/generic/openwrt-19.07.9-ar71xx-generic-wifi-pineapple-nano-squashfs-sysupgrade.bin ../wifi-pineapple-nano.bin
```

Now you have the custom firmware.

Reset Pineapple Nano by flashing the oficial recovery image first.

* [https://downloads.hak5.org/api/devices/wifipineapplenano/firmwares/recovery](https://downloads.hak5.org/api/devices/wifipineapplenano/firmwares/recovery)

Flash the oficial OpenWRT 19.07.9 for Pineapple Nano after.

* [https://downloads.openwrt.org/releases/19.07.9/targets/ar71xx/generic/openwrt-19.07.9-ar71xx-generic-wifi-pineapple-nano-squashfs-sysupgrade.bin](https://downloads.openwrt.org/releases/19.07.9/targets/ar71xx/generic/openwrt-19.07.9-ar71xx-generic-wifi-pineapple-nano-squashfs-sysupgrade.bin)

In LuCi interface from OpenWRT fresh install, upgrade the firmware with your custom one, check the option to erase any previous data.

And wait... You can do this how many times you feel you want to.

## After get the rebuild up and running

* Use WiFi Pineapple Connector for Linux, [https://github.com/hak5darren/wp6](https://github.com/hak5darren/wp6)

Enter Nano's shell by ssh, run the commands below.

```
ln -s /lib/libubus.so.20210603 /lib/libubus.so
```

Optional, to make handshakes folder persistent. To persist on boot you have to edit `/etc/init.d/boot` file.

```
rm -rf /tmp/handshakes/
ln -s /sd/LEET/handshakes /tmp/
```

```
nano /etc/init.d/boot
```

`/etc/init.d/boot` content.

```
        ## CUSTOM ##

        rm -rf /tmp/handshakes/
        ln -s /sd/LEET/handshakes /tmp

        ## CUSTOM ##
```

Optional, make sure to install GPSd, Aircrack suite, Bettercap suite, Kismet and Reaver suite.

Optional, place an updated OUI aircrack-ng database in external storage as replacement for the builtin file.

```
rm /etc/aircrack-ng/oui.txt
ln -s /sd/LEET/airodump_warwalking/airodump-ng-oui.txt /etc/aircrack-ng/oui.txt
ln -s /sd/LEET/airodump_warwalking/airodump-ng-oui.txt /etc/aircrack-ng/airodump-ng-oui.txt
```

Optional, setup your `/etc/rc.local` file for start on boot tasks.

```
nano /etc/rc.local
```

See `/etc/rc.local` content below.

```
/bin/sleep 25

# /tmp/uci-set-wireless-country.log
# /sbin/uci set wireless.radio0.country=BR > /dev/null 2>&1 &
# /sbin/uci set wireless.radio1.country=BR > /dev/null 2>&1 &
# /sbin/uci set wireless.radio2.country=BR > /dev/null 2>&1 &
# /sbin/uci commit wireless > /dev/null 2>&1 &
# /bin/sleep 10

# /tmp/airmon-ng-wlan1.log
/bin/echo -e "n\nn" | /usr/sbin/airmon-ng start wlan1 > /dev/null 2>&1 &
/bin/sleep 25

# /tmp/airmon-ng-wlan2.log
/bin/echo -e "n\nn" | /usr/sbin/airmon-ng start wlan2 > /dev/null 2>&1 &
/bin/sleep 25

# /tmp/airmon-ng-wlan3.log
/bin/echo -e "n\nn" | /usr/sbin/airmon-ng start wlan3 > /dev/null 2>&1 &
/bin/sleep 25

## /tmp/run-ntpd.log
/usr/sbin/ntpd > /dev/null 2>&1 &
/bin/sleep 10
# /sbin/uci set system.@system[0].timezone='BRT3BRST,M10.3.0/0,M2.3.0/0' > /dev/null 2>&1 &

## /tmp/gpsd-172-16-42-107.log
/sd/usr/sbin/gpsd -F /var/run/gpsd.sock udp://0.0.0.0:1337 > /dev/null 2>&1 &
/bin/sleep 10

## /tmp/bettercap-wlan1mon-pwnagotchi.log
# /sd/usr/bin/bettercap -no-history -iface wlan1mon -caplet /sd/LEET/bettercap_wardriving/pwnagotchi.cap -script /sd/LEET/bettercap_wardriving/script.js > /dev/null 2>&1 &
# /sd/usr/bin/bettercap -no-history -iface wlan1mon -script /sd/LEET/bettercap_wardriving/security_monitor/main.js > /dev/null 2>&1 &
# /bin/sleep 10

## /tmp/airodump-ng-wlan2mon.log
# /usr/sbin/airodump-ng -K 1 --essid-regex '^(?!YOUR_MANAGEMENT_AP)' --band abg --gpsd --write /sd/LEET/handshakes/airodump_ng_netxml/AI-RO-DU-MP-00 -f 250 --output-format netxml --write-interval 5 wlan2mon > /dev/null 2>&1 &
# /bin/sleep 30

/bin/echo '' > /tmp/button.log 2>&1 &

# /tmp/airodump-run.log
# /sd/LEET/airodump_wardriving/run.sh > /dev/null 2>&1 &

# Enter commands above this line
exit 0
```

Just a reminder that this exists, take a look.

```
nano /etc/rc.d/S99pineapd
```

Just a reminder that this exists, take a look.

```
nano /etc/config/system
```

## A reminder to don't use SDCARD with Pineapple Nano

* SWAP is 61,0352 MiB;
* Don't use SDCARD, use a USB HUB with pendrive instead. Leave a swap partition of same size as Nano.

Configure external storage. This works nice.

* [https://openwrt.org/docs/guide-user/storage/fstab](https://openwrt.org/docs/guide-user/storage/fstab)
* [https://openwrt.org/docs/techref/block_mount](https://openwrt.org/docs/techref/block_mount)
* [https://openwrt.org/docs/guide-user/storage/usb-installing](https://openwrt.org/docs/guide-user/storage/usb-installing)

```
nano /etc/fstab
```

`/etc/fstab` content.

```
# <file system> <mount point> <type> <options> <dump> <pass>
UUID=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX /dev/sda1 ext4 errors=remount-ro 0 1
UUID=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX /dev/sda2 swap sw 0 0
```

```
config global
	option	anon_swap	'0'
	option	anon_mount	'0'
	option	auto_swap	'1'
	option	auto_mount	'1'
	option	delay_root	'5'
	option	check_fs	'1'

config mount
	option	target	'/sd'
	option	uuid		'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
	option	device	'/dev/sdcard/sd1'
	option	fstype	'ext4'
	option	options	'rw,sync'
	option	enabled	'1'

config swap
	option	uuid		'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
	option	device	'/dev/sdcard/sd2'
	option	enabled	'0'
```

Just a reminder that this exists, take a look.

```
/etc/rc.d/S99wpc-tools
wpc-tools 

Available commands:
    format_sd            Format SD/pendrive for use with Pineapple
    correct_sd_mount     Fix ghost SD/pendrive issues
    missing_packages     Install the missing OpenWRT packages
    theme_install        Deploys the tool to change panel theme
    set_panel_port       Change the port used by panel
    set_router_ip        Change the IP used by the hardware
    set_pineap_interface Change the interface used by PineAP 
    handle_lost_phys     Fix unrecognized wifi interfaces
```

## Tips, I had to install WPS modules from community manually

```
touch /tmp/wps.progress
opkg update
ln -s /sd/modules/wps /pineapple/modules/
opkg --dest sd install reaver bully pixiewps libpcap
wget https://github.com/xchwarze/wifi-pineapple-community/raw/main/modules/src/wps/scripts/wps.sh
mv wps.sh /sd/modules/wps/scripts/wps.sh
chmod +x /sd/modules/wps/scripts/wps.sh
touch /etc/config/wps
echo "config wps 'module'" > /etc/config/wps
uci set wps.module.installed=1
uci commit wps.module.installed
rm /tmp/wps.progress
```

## Tips, Kismet did not work for me, APs don't show up, but this is usefull

* Wardriving with WIFI Pineapple Nano in Mobile World Congress 2016 at Barcelona, posted on 2016/02/27 by Roger Carhuatocto
* [https://holisticsecurity.wordpress.com/2016/02/27/wardriving-wifi-pineapple-nano-mobile-world-congress-2016-barcelona/](https://holisticsecurity.wordpress.com/2016/02/27/wardriving-wifi-pineapple-nano-mobile-world-congress-2016-barcelona/)

```
touch manuf
python3 make-manuf.py
mv manuf /sd/LEET/kismet_warwalking
```

```
iwconfig wlan1 mode monitor
ifconfig wlan1 up
```

```
iwconfig wlan1
```

```
opkg --dest sd install libgps gpsd gpsd-clients
```

```
nano /etc/init.d/gpsd 
nano /etc/config/gpsd 
```

From br-lan, find GPS server
```
nc -nv 172.16.42.107 1337
```

```
gpsd -F /var/run/gpsd.sock -N tcp://172.16.42.107:1337
gpsd -F /var/run/gpsd.sock tcp://172.16.42.107:1337
```

```
cgps
```

```
sudo iwlist scanning
```

```
ln -s /sd/usr/bin/kismet_server /usr/bin/kismet_server
```

```
kismet_server
```

```
kismet_client
```

## Tips, Easy GPS for the Pineapple

* [https://github.com/tiagoshibata/Android-GPSd-Forwarder](https://github.com/tiagoshibata/Android-GPSd-Forwarder)

Install GPSd Forwarder in Android, enable your GPS.

Connect to your Nano with management AP.

In GPSd Forwarder, set your Nano IP (172.16.42.1) and GPSd listenning port (1337).

Hit start. Done here.

## Tips, the pwnagotchi.cap

* Automatic handshake and PMKID capture from all access points, posted on September 19, 2019 by Alex
* [https://miloserdov.org/?p=3500](https://miloserdov.org/?p=3500)
* Project PITA Writeup - build a mini mass deauther using Bettercap and a Raspberry Pi Zero, posted on July 28, 2018 by Evilsocket
* [https://www.evilsocket.net/2018/07/28/Project-PITA-Writeup-build-a-mini-mass-deauther-using-bettercap-and-a-Raspberry-Pi-Zero-W/](https://www.evilsocket.net/2018/07/28/Project-PITA-Writeup-build-a-mini-mass-deauther-using-bettercap-and-a-Raspberry-Pi-Zero-W/)

Let's build our own pwnagotchi-godzilla, mine is huge.

## Tips, the Pineapple button script

```
#!/bin/bash

# User configurable button script

/usr/bin/killall airodump-ng
/usr/bin/killall bettercap
/usr/bin/killall gpsd

/usr/sbin/airmon-ng stop wlan1mon
/usr/sbin/airmon-ng stop wlan2mon
#/usr/sbin/airmon-ng stop wlan3mon

#/bin/chmod -x /etc/rc.d/S99pineapd
#/bin/chmod +x /etc/rc.d/S99pineapd
#/etc/rc.d/S99pineapd start > /tmp/pineapd-stop.log 2>&1 &
#/etc/rc.d/S99pineapd stop > /tmp/pineapd-stop.log 2>&1 &

/bin/echo "BUTTONED" > /tmp/button.log
/bin/sleep 300

/bin/echo "REBOOT" > /dev/console
/bin/sync
/sbin/reboot
```

## Tips, I have to configure my Alfa network usb adapter as access point before use it with Bettercap

* [https://github.com/bettercap/bettercap/issues/1061](https://github.com/bettercap/bettercap/issues/1061)
* [https://openwrt.org/docs/guide-user/network/wifi/basic](https://openwrt.org/docs/guide-user/network/wifi/basic)

```
onfig wifi-device 'radio3'
    option type 'mac80211'
    option channel '36'
    option hwmode '11a'
    option path 'platform/ehci-platform/usb1/1-1/1-1.3/1-1.3.3/1-1.3.3:1.0'
    option htmode 'VHT80'
    option country 'BR'

config wifi-iface
    option device 'radio3'
    option ifname 'wlan3'
    option network 'lan'
    option mode 'ap'
    option maxassoc '0'
    option ssid 'XXXX_XXXX'
    option encryption 'psk2+ccmp'
    option key 'XXXXXXXXXX'
    option hidden '0'
    option disabled '0'
```

* [https://github.com/morrownr/USB-WiFi/blob/main/home/AP_Mode/Bridged_Wireless_Access_Point.md](https://github.com/morrownr/USB-WiFi/blob/main/home/AP_Mode/Bridged_Wireless_Access_Point.md)

```
nano /tmp/run/hostapd-phy0.conf
```

`/tmp/run/hostapd-phy0.conf` content.

```
driver=nl80211
logger_syslog=-1
logger_syslog_level=0
logger_stdout=127
logger_stdout_level=2
country_code=BR
ieee80211d=1
ieee80211h=1
hw_mode=a
channel=36

ieee80211n=1
ht_coex=0
ht_capab=[HT40+][LDPC][SHORT-GI-20][SHORT-GI-40][TX-STBC][RX-STBC1]
vht_oper_chwidth=1
vht_oper_centr_freq_seg0_idx=42
ieee80211ac=1
vht_capab=[RXLDPC][SHORT-GI-80][TX-STBC-2BY1][RX-ANTENNA-PATTERN][TX-ANTENNA-PATTERN][RX-STBC1][MAX-A-MPDU-LEN-EXP3]

interface=wlan3
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
ap_isolate=1
disassoc_low_ack=1
preamble=1
wmm_enabled=1
ignore_broadcast_ssid=0
uapsd_advertisement_enabled=1
wpa_passphrase=XXXXXXXXXX
auth_algs=3
wpa=2
wpa_pairwise=CCMP
ssid=XXXX_XXXX
bridge=br-lan
wpa_key_mgmt=WPA-PSK
okc=0
disable_pmksa_caching=1
bssid=XX:XX:XX:XX:XX:XX
```
## Tips, using both 2GHz and 5GHz with Pineapple

* [https://theirsecurity.com/tips-and-best-practice/wifi-pineapple-5ghz/](https://theirsecurity.com/tips-and-best-practice/wifi-pineapple-5ghz/)
* [http://web.archive.org/web/20231001023521/https://theirsecurity.com/tips-and-best-practice/wifi-pineapple-5ghz/](http://web.archive.org/web/20231001023521/https://theirsecurity.com/tips-and-best-practice/wifi-pineapple-5ghz/)

```
§§ Wifi Pineapple – 5Ghz §§

I have been having a lot of fun with my Wifi Pineapple!

But, Today is a great day as Wifi Pineapple got 5Ghz!

I’ve also written a guide further down how to set it up!

§§ The Adapter §§

Having read through the Hak5 docs on compatible adapters, there are 2 choices either an AWUS036ACM from Alpha or an EP-AC1605.

The latter is from Edup and for some reason, mainly lack of sleep, I picked this one.

The adapter cost me £16 from Aliexpress, got here in 8 days and surprisingly for Aliexpress Wifi Adapters, it felt new and well built!

Beware though! if your looking for this on Aliexpress as some aren’t advertised correctly. You need one based on the MT7612U chipset and some are advertised as RTL8812AU.

[IMAGE]

I know! The alpha is smaller, why didn’t i just pick that one!

§§ Setting it up §§

So, Hak5 say this works out of the box as a 5ghz adapter which is completely true!

It just needs configuring to use 5Ghz vs 2.4Ghz.

It’s really easy to do and ive written the below guide on how to it in terminal. There are also some oneliners to copy into your terminal to change between 2.4Ghz and 5Ghz.

This is providing you set it up the same way i did

To open the terminal, click this icon

[IMAGE]

§ Step 1 §

Make sure your Wifi Adapter shows!

Type in ifconfig and you should have an extra adapter.

[IMAGE]

As you can see, mine shows and can see its called wlan3

§ Step 2 §

cd /etc/config

[IMAGE]

In the config folder, the two files we need to edit are pineap and wireless.

But before we do this, backup your current config files using;

cp pineap pineap2g && cp wireless wireless2g

Then use nano with;

nano pineap

[IMAGE]

In the above image we are changing the following

option pineap_interface 'wlan1mon'
# change this to
option pineap_interface 'wlan3mon'

Then to exit, its CTRL+X, hit the Y button to save the changes and press Enter, onto the next one.

nano wireless

[IMAGE]

On this one, you may need to scroll down to find it, but we are changing

option ifname 'wlan1'
# change this to 
option ifname 'wlan3'

Save and exit like we did before.

Then, we are going to backup these changes with

cp pineap pineap5g && cp wireless wireless5g

§ Step 3 §

Last file we need to edit, so change directory and make the backup with;

cd /etc/init.d && cp pineapd pineapd2g

We need to make 2 changes in this file so open it with

nano pineapd

[IMAGE]

This is the first change

pineap_interface = wlan1mon
# this becomes
pineap_interface=wlan3mon

[IMAGE]

This is the last change we need to make

ifconfig wlan1mon &>dev/null || airmon-ng start wlan1 &>/dev/null
# This becomes 
ifconfig wlan3mon &>dev/null || airmon-ng start wlan3 &>/dev/null

Save and exit like we did before

Then create another backup with;

cp pineapd pineapd5g

§ Step 4 §

[IMAGE]

So, we have 5g settings currently active (you need to restart for these to take effect).

We also have 2 backups of each file, one with 2.4Ghz settings and 5Ghz settings.

From this, you can run either of the commands to change the settings back and forth. I.e you want to use the internal 2.4Ghz radios vs plugging your 5Ghz adapter in.

To switch to 2.4Ghz

cd /etc/config && rm pineap && rm wireless && cp pineap2g pineap && cp wireless2g wireless && cd /etc/init.d && rm pineapd && cp pineapd2g pineapd

To switch to 5Ghz

cd /etc/config && rm pineap && rm wireless && cp pineap5g pineap && cp wireless5g wireless && cd /etc/init.d && rm pineapd && cp pineapd5g pineapd

When you copy these in to the terminal, it wont display the full thing correctly, but it will run all the commands and complete correctly.

Don’t forget to restart after each change!

§§ Conclusion §§

I really like using the WiFi pineapple with its new 5Ghz adapter! It really does make a big difference and you find many more networks and even more networks in PineAP. I would also like to thank the Hak5 forums for where i found the code snippets that needed changing, this saved me a ton of time with grep.

I hope it makes more sense with pictures, but if you have any questions, please contact me

Thank you for reading

~ Source
https://theirsecurity.com/tips-and-best-practice/wifi-pineapple-5ghz/
```

## That's all folks.
