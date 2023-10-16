var path = '/sd/LEET/handshakes/';
var accessPointData = {};

function exportDiscovery(event) {

    var gps = session.GPS;
    var data = event.data;;

    var hasValidGPS = gps.Latitude !== 0 || gps.Longitude !== 0;
    if (hasValidGPS) {

        if (!accessPointData[data.mac]) {
            accessPointData[data.mac] = {
                timesSeen: 0,
                lastSeenTimestamp: '',
                clients: []
            };
        }

        accessPointData[data.mac].timesSeen++;
        accessPointData[data.mac].lastSeenTimestamp = data.last_seen;
        accessPointData[data.mac].clients.concat(data.clients);

        var exportData = {
            Updated: accessPointData[data.mac].lastSeenTimestamp,
            Latitude: gps.Latitude,
            Longitude: gps.Longitude,
            Altitude: gps.Altitude,
            Seen: accessPointData[data.mac].timesSeen,
            Clients: accessPointData[data.mac].clients,
            Encryption: data.encryption + '+' + data.authentication + '-' + data.cipher,
            Packets: data.received,
            Manufacturer: data.vendor
        };

        var jsonData = JSON.stringify(exportData);
        var filename = path + data.hostname.replace(/[/\\?%7*:|"<>_]/g, '-') + '_' + data.mac.replace(/:/g, '') + '.gps.json';
        writeFile(filename, jsonData);

    }
}

onEvent('wifi.ap.new', function(event) {
    exportDiscovery(event);
});
