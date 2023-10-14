## Pineapple Nano recovery mode

* [https://docs.hak5.org/wifi-pineapple-6th-gen-nano-tetra/faq-troubleshooting/firmware-recovery](https://docs.hak5.org/wifi-pineapple-6th-gen-nano-tetra/faq-troubleshooting/firmware-recovery)

```
sudo ifconfig YOUR_PINE_ETH 192.168.1.2 netmask 255.255.255.0 up
```

Enter 192.168.1.1 in browser incognito mode

## Rebuilding Pineapple Nano firmware

* [https://github.com/xchwarze/wifi-pineapple-cloner](https://github.com/xchwarze/wifi-pineapple-cloner)

```
sudo apt install binwalk
```

Install sasquatch to extract non-standard SquashFS images

```
sudo apt-get install zlib1g-dev liblzma-dev liblzo2-dev
git clone https://github.com/devttys0/sasquatch
(cd sasquatch && ./build.sh)
```

From inside the sasquatch directory

```
wget https://raw.githubusercontent.com/devttys0/sasquatch/82da12efe97a37ddcd33dba53933bc96db4d7c69/patches/patch0.txt
mv patch0.txt patches
./build.sh
```

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

Reset Pineapple Nano by flashing the oficial recovery image

Flash the oficial OpenWRT 19.07.9 for Pineapple Nano

In LuCi interface from OpenWRT fresh install, upgrade the firmware with your custom build, check the option to erase any previous data

Wait...

## After up and running

Run at Nano's shell

```
ln -s /lib/libubus.so.20210603 /lib/libubus.so
```

```
rm -rf /tmp/handshakes/
ln -s /sd/LEET/handshakes /tmp/
```

```
rm /etc/aircrack-ng/oui.txt
ln -s /sd/LEET/airodump_warwalking/airodump-ng-oui.txt /etc/aircrack-ng/oui.txt
ln -s /sd/LEET/airodump_warwalking/airodump-ng-oui.txt /etc/aircrack-ng/airodump-ng-oui.txt
```

```
nano /etc/rc.local
```
/etc/rc.local content
```
/bin/sleep 25

# /tmp/airmon-ng-wlan1.log
/bin/echo -e "n\nn" | /usr/sbin/airmon-ng start wlan1 > /dev/null 2>&1 &
/bin/sleep 25

# /tmp/airmon-ng-wlan2.log
# /bin/echo -e "n\nn" | /usr/sbin/airmon-ng start wlan2 > /dev/null 2>&1 &
# /bin/sleep 25

# /tmp/airmon-ng-wlan3.log
# /bin/echo -e "n\nn" | /usr/sbin/airmon-ng start wlan3 > /dev/null 2>&1 &
# /bin/sleep 25

## /tmp/run-ntpd.log
/usr/sbin/ntpd > /dev/null 2>&1 &
/bin/sleep 10

## /tmp/gpsd-172-16-42-107.log
# /sd/usr/sbin/gpsd -F /var/run/gpsd.sock tcp://172.16.42.107:1337 > /dev/null 2>&1 &
/sd/usr/sbin/gpsd -F /var/run/gpsd.sock udp://0.0.0.0:1337 > /dev/null 2>&1 &
/bin/sleep 10

## /tmp/bettercap-wlan2mon-pwnagotchi.log
/sd/usr/bin/bettercap -no-history -iface wlan1mon -caplet /sd/LEET/bettercap_warwalking/pwnagotchi.cap > /dev/null 2>&1 &
/bin/sleep 10

## /tmp/airodump-ng-wlan1mon.log
/usr/sbin/airodump-ng -K 1 --essid-regex '^(?!YOUR_MANAGEMENT_AP)' --band bg --gpsd --write /sd/LEET/handshakes/AI-RO-DU-MP-00-00_full.pcap -f 100 --output-format netxml --write-interval 5 wlan1mon > /dev/null 2>&1 &
/bin/sleep 30

# /tmp/airodump-run.log
/sd/LEET/airodump_warwalking/run.sh > /dev/null 2>&1 &

# Enter commands above this line
exit 0

```

```
nano /etc/init.d/boot
```
/etc/init.d/boot content
```
        ## CUSTOM ##

        rm -rf /tmp/handshakes/
        ln -s /sd/LEET/handshakes /tmp

        ## CUSTOM ##
```

Just a reminder that this exists
```
nano /etc/rc.d/S99pineapd
```

```
nano /etc/config/system
```
/etc/config/system content
```
    'America/Sao Paulo  BRT3BRST,M10.3.0/0,M2.3.0/0'
```

## A reminder to don't use SDCARD with Pineapple Nano

* SWAP is 61,0352 MiB
* Don't use SDCARD, use a USB HUB with pendrive instead

Taking notes
```
opkg update && opkg install --dest sd blkid
blkid | grep /dev/sd
```

Taking notes
```
nano /etc/fstab
```
/etc/fstab content
```
# <file system> <mount point> <type> <options> <dump> <pass>
UUID=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX /dev/sda1 ext4 errors=remount-ro 0 1
UUID=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX /dev/sda2 swap sw 0 0
```

Taking notes
```
fstab config
```

Taking notes
```
block detect | uci import fstab
```

Taking notes, this works fine
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

Just a reminder that this exists
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

Taking notes
```
cat /etc/modules.d/35-usb-ehci 
ehci-hcd
```

Taking notes
```
https://github.com/raspberrypi/linux/issues/4597

"scsi host0: usb-storage 1-1.2:1.0"

https://openwrt.org/docs/guide-user/storage/usb-installing

opkg list-installed | grep usb

opkg remove kmod-usb-uhci
opkg remove kmod-usb-ehci
opkg remove kmod-usb-ohci
opkg remove kmod-usb2
opkg remove kmod-usb3

opkg install kmod-usb2
opkg install kmod-usb3
opkg install kmod-usb-storage-uas
```

## The wps module is nice, but I'm taking notes

Taking notes
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

## Kismet did not work for me, I'm taking notes

* [https://holisticsecurity.wordpress.com/2016/02/27/wardriving-wifi-pineapple-nano-mobile-world-congress-2016-barcelona/](https://holisticsecurity.wordpress.com/2016/02/27/wardriving-wifi-pineapple-nano-mobile-world-congress-2016-barcelona/)

* ChineloDriving uses airodump-ng for mapping only, and bettercap to captures if needed

Taking notes
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

## Easy GPS for the Pineapple

* [https://github.com/tiagoshibata/Android-GPSd-Forwarder](https://github.com/tiagoshibata/Android-GPSd-Forwarder)

Install GPSd Forwarder in Android, enable your GPS

Connect to your Nano with management AP

In GPSd Forwarder, set your Nano IP (172.16.42.1) and GPSd listenning port (1337)

Hit start

Done here

## The pwnagotchi.cap

* [https://miloserdov.org/?p=3500](https://miloserdov.org/?p=3500)

Let's build our own pwnagotchi-godzilla, mine is huge

## The Pineapple button script

```
#!/bin/bash

# User configurable button script

/usr/bin/killall airodump-ng
/usr/bin/killall bettercap
/usr/bin/killall gpsd

/usr/sbin/airmon-ng stop wlan1mon
#/usr/sbin/airmon-ng stop wlan2mon
#/usr/sbin/airmon-ng stop wlan3mon

/bin/chmod -x /etc/rc.d/S99pineapd
#/bin/chmod +x /etc/rc.d/S99pineapd
#/etc/rc.d/S99pineapd start > /tmp/pineapd-stop.log 2>&1 &
#/etc/rc.d/S99pineapd stop > /tmp/pineapd-stop.log 2>&1 &

/bin/echo "BUTTONED" > /tmp/button.log
/bin/sleep 300

/bin/echo "REBOOT" > /dev/console
/bin/sync
/sbin/reboot
```

That's all folks