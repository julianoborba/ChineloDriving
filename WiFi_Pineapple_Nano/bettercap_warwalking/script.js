var accessPoint = {};

function exportEvent(data, newClient) {

    var gps = session.GPS;
    if (gps.Latitude === 0 || gps.Longitude === 0) {
        return;
    }

    if (!accessPoint[data.mac]) {
        accessPoint[data.mac] = {
            seen: 0,
            lastSeen: '',
            clients: []
        };
    }

    if (!newClient) {
        accessPoint[data.mac].seen++;
    }
    accessPoint[data.mac].lastSeen = data.last_seen;
    accessPoint[data.mac].clients = accessPoint[data.mac].clients.concat(data.clients);

    var capture = {
        Hostname: data.hostname,
        Mac: data.mac.toUpperCase(),
        Updated: accessPoint[data.mac].lastSeen,
        Latitude: gps.Latitude,
        Longitude: gps.Longitude,
        Altitude: gps.Altitude,
        Seen: accessPoint[data.mac].seen,
        Clients: accessPoint[data.mac].clients,
        Encryption: data.encryption + '+' + data.authentication + '-' + data.cipher,
        Packets: data.received,
        Manufacturer: data.vendor,
        WPS: data.wps
    };

    var pHostname = data.hostname.replace(/[/\\?%7*:|"<>._ ]/g, '');
    var pMac = data.mac.replace(/:/g, '');
    var path = '/sd/LEET/handshakes/bettercap_gps_json/' + pHostname + '_' + pMac + '.gps.json';

    writeFile(path, JSON.stringify(capture));

}

onEvent('wifi.ap.new', function(event) {
    exportEvent(event.data, false);
});

onEvent('wifi.client.new', function(event) {
    exportEvent(event.data['AP'], true);
});
