var accessPoint = {};

function exportEvent(event) {

    var gps = session.GPS;

    if (gps.Latitude === 0 || gps.Longitude === 0) {
        return;
    }

    if (!accessPoint[event.data.mac]) {
        accessPoint[event.data.mac] = {
            seen: 0,
            lastSeen: '',
            clients: []
        };
    }

    accessPoint[event.data.mac].seen++;
    accessPoint[event.data.mac].lastSeen = event.data.last_seen;
    accessPoint[event.data.mac].clients = accessPoint[event.data.mac].clients.concat(event.data.clients);

    var capture = {
        Hostname: event.data.hostname,
        Mac: event.data.mac,
        Updated: accessPoint[event.data.mac].lastSeen,
        Latitude: gps.Latitude,
        Longitude: gps.Longitude,
        Altitude: gps.Altitude,
        Seen: accessPoint[event.data.mac].seen,
        Clients: accessPoint[event.data.mac].clients,
        Encryption: event.data.encryption + '+' + event.data.authentication + '-' + event.data.cipher,
        Packets: event.data.received,
        Manufacturer: event.data.vendor
    };

    var pHostname = event.data.hostname.replace(/[/\\?%7*:|"<>._ ]/g, '');
    var pMac = event.data.mac.replace(/:/g, '');
    var path = '/sd/LEET/handshakes/' + pHostname + '_' + pMac + '.gps.json';

    writeFile(path, JSON.stringify(capture));

}

onEvent('wifi.ap.new', function(event) {
    exportEvent(event);
});
