// refers to https://github.com/bettercap/scripts, Simone Margaritelli a.k.a. evilsocket

require("config")
require("messaging")
require("functions")

log("session script loaded, fake AP is " + fakeESSID);

run('set ticker.commands ""');
run('set ticker.period 10');
run('ticker on');
// run('net.recon on');
// run('net.probe on');
run('set wifi.interface ' + wifiInterface);
run('set wifi.handshakes.file /sd/LEET/handshakes/BE-TT-ER-CA-PS-EC_full.pcap')
run('wifi.recon on');

onEvent('endpoint.new', onNewEndpoint);
onEvent('tick', onTick);
onEvent('wifi.deauthentication', onDeauthentication);
onEvent('wifi.ap.new', onNewAP);
onEvent('gateway.change', onGatewayChange)
