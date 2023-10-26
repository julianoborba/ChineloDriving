// refers to https://github.com/bettercap/scripts, Simone Margaritelli a.k.a. evilsocket

var l = '\\\\n';


var fakeESSID = random.String(16, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ');
var fakeBSSID = random.Mac();


db = JSON.stringify(readFile(dbPath));
if (db.aps && db.endpoints) {
    log('database loaded from ' + dbPath);
} else {
    log('empty database loaded from ' + dbPath);
    var db = {
        endpoints: {},
        aps: {}
    };
}

function updateEndpoint(endpoint) {
    var known = db.endpoints[endpoint.mac];
    known.last_seen = endpoint.last_seen;
    for (var name in endpoint.meta.values) {
        if (!(name in known.meta.values)) {
            known.meta.values[name] = endpoint.meta.values[name];
        }
    }
    db.endpoints[endpoint.mac] = known;
}

function decorateMac(label, mac, vendor) {
    if (vendor.length) {
        return label + ': ' + mac + ' ( ' + vendor + ' )';
    }
    return label + ': ' + mac;
}

function decorateEndpoint(endpoint, padding) {
    var msg = (endpoint.hostname.length ? (padding + 'Hostname: ' + endpoint.hostname + l) : '') +
        (endpoint.ipv4.length ? (padding + 'IPv4: ' + endpoint.ipv4 + l) : '') +
        (endpoint.ipv6.length ? (padding + 'IPv6: ' + endpoint.ipv6 + l) : '') +
        padding + decorateMac('MAC', endpoint.mac, endpoint.vendor) + l;
    if (endpoint.meta.values.length > 0) {
        msg += l + padding + 'Info:' + l;
        for (var name in endpoint.meta.values) {
            msg += padding + name + ' : ' + endpoint.meta.values[name] + l;
        }
    }
    return msg;
}

function onNewEndpoint(event) {
    var endpoint = event.data;
    var msg = null;
    if (endpoint.mac in db.endpoints) {
        updateEndpoint(endpoint);
    } else {
        var gps = session.GPS;
        var msg = l
            + '🖥️ **NEW UNKNOWN ENDPOINT CONNECTION DETECTED** 🖥️' + l + l
            + decorateEndpoint(endpoint, '') + l
            + '**GPS** ' + gps.Latitude + ',' + gps.Longitude;
        db.endpoints[endpoint.mac] = endpoint;
    }
    writeFile(dbPath, JSON.stringify(db));
    if (notifyUknownEndpoints && msg != null) {
        sendMessage(msg);
    }
}

function updateAP(ap) {
    var known = db.aps[ap.mac];
    known.last_seen = ap.last_seen;
    for (var name in ap.meta.values) {
        if (!(name in known.meta.values)) {
            known.meta.values[name] = ap.meta.values[name];
        }
    }
    db.aps[ap.mac] = known;
}

function onNewAP(event) {
    var ap = event.data;
    if (ap.hostname == fakeESSID) {
        if (!notifyRogueAPs) {
            return;
        }
        var gps = session.GPS;
        var message = l
            + '📡 **KARMA ATTACK DETECTED** 📡' + l + l
            + '**BSSID** '      + ap.mac.toUpperCase() + l
            + '**ESSID** '      + ap.hostname + l
            + '**PACKETS** '    + ap.received + l
            + '**GPS** '        + gps.Latitude + ',' + gps.Longitude + l
            + '**SEEN** '       + ap.last_seen;
        sendMessage(message);
        return;
    }
    if (ap.mac in db.aps) {
        updateAP(ap);
    } else {
        db.aps[ap.mac] = ap;
    }
    writeFile(dbPath, JSON.stringify(db));
}

function decorateAP(ap, padding) {
    var msg = padding + 'ESSID: ' + ap.hostname + l + padding + decorateMac('BSSID', ap.mac, ap.vendor) + l;
    if (ap.meta.values.length > 0) {
        msg += l + padding + 'Info:' + l;
        for (var name in ap.meta.values) {
            msg += padding + name + ' : ' + ap.meta.values[name] + l;
        }
    }
    return msg;
}

function decorateAddress(label, mac) {
    if (mac in db.endpoints) {
        return label + ':' + l + decorateEndpoint(db.endpoints[mac], '  ');
    } else if (mac in db.aps) {
        return label + ':' + l + decorateAP(db.aps[mac], '  ');
    }
    return label + ': ' + mac + l;
}

function onDeauthentication(event) {
    if (!notifyDeauth) {
        return;
    }
    var data = event.data;
    var gps = session.GPS;
    message = l
        + '📵 **DEAUTHENTICATION FRAME PACKET DETECTED** 📵' + l + l
        + '**RSSI** '       + data.rssi + l
        + '**REASON** '     + data.reason + l
        + '**BSSID** '      + data.ap.mac.toUpperCase() + l
        + '**ESSID** '      + data.ap.hostname + l
        + '**GPS** '        + gps.Latitude + ',' + gps.Longitude + l
        + '**SEEN** '       + data.ap.last_seen + l
        + decorateAddress('**ADDRESS**', data.address1) + l
        + decorateAddress('**ADDRESS**', data.address2) + l
        + decorateAddress('**ADDRESS**', data.address3);
    sendMessage(message);
}

function onGatewayChange(event) {
    if (!notifyGatewayChanges) {
        return;
    }
    var change = event.data;
    var gps = session.GPS;
    var message = l
        + '🕵️ **MAN-IN-THE-MIDDLE ATTACK DETECTED** 🕵️' + l + l
        + '**TYPE** '       + change.type + ' gateway change, possible MiTM attack' + l
        + '**PREVIP** '     + change.prev.ip + ' / ' + change.prev.mac + l
        + '**NEWIP** '      + change.new.ip + ' / ' + change.new.mac + l
        + '**GPS** '        + gps.Latitude + ',' + gps.Longitude;
    sendMessage(message);
}

function onTick(event) {
    run('wifi.probe ' + fakeBSSID + ' ' + fakeESSID);
}
