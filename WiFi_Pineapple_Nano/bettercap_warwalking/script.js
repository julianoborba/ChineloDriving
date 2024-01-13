function exportEvent(data) {

    var gps = session.GPS;
    if (gps.Latitude === 0 || gps.Longitude === 0) {
        return;
    }

    var hostname = data.hostname;
    if (!hostname || hostname.indexOf('hidden') != -1) {
        hostname = 'CLOAKED';
    }

    var encryption = '~Empty~';
    if (data.encryption) {
        encryption = data.encryption;
    }
    if (data.authentication) {
        encryption = encryption + '+' + data.authentication;
    }
    if (data.cipher) {
        encryption = encryption + '-' + data.cipher;
    }

    var capture = {
        Hostname: hostname,
        Mac: data.mac.toUpperCase(),
        Updated: data.last_seen,
        Latitude: gps.Latitude,
        Longitude: gps.Longitude,
        Altitude: gps.Altitude,
        Clients: data.clients,
        Encryption: encryption,
        Packets: data.received,
        Manufacturer: data.vendor,
        WPS: data.wps
    };

    var pHostname = data.hostname.replace(/[/\\?%7*:|"<>._ -]/g, '');
    var pMac = data.mac.replace(/:/g, '');
    var today = (new Date()).toISOString().replace(/[^0-9]/g, '').slice(0, -3)

    var path = '/sd/LEET/handshakes/bettercap_gps_json/' + today + '_' + pHostname.toUpperCase() + '_' + pMac.toUpperCase() + '.gps.json';

    writeFile(path, JSON.stringify(capture));

}

onEvent('wifi.ap.new', function(event) {
    exportEvent(event.data);
});

onEvent('wifi.client.new', function(event) {
    exportEvent(event.data['AP']);
});
