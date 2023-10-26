// refers to https://github.com/bettercap/scripts, Simone Margaritelli a.k.a. evilsocket

var q = '\\\"';


function sendMessage(message) {
    if (telegramEnabled) {
        sendTelegramMessage(message);
    }
    if (discordEnabled) {
        sendDiscordMessage(message);
    }
}

function sendTelegramMessage(message) {
    var url = 'https://api.telegram.org/bot'
        + telegramToken
        + '/sendMessage?chat_id='
        + telegramChatId
        + '&text='
        + http.Encode(message);
    var resp = http.Get(url, {});
    if (resp.Error) {
        log("error while running sending telegram message: " + resp.Error.Error());
    }
}

function sendDiscordMessage(message) {
    var url = discordWebHook;
    // var resp = http.PostJSON(url, {}, message);
    // if (resp.Error) {
    //    log("error while running sending discord message: " + resp.Error.Error());
    // }
    var cURL = "!curl -s -d '{"
        + q + "content" + q + ":"
        + q + "\"" + message + "\"" + q
        + "}' -H content-type:application/json -X POST "
        + discordWebHook;
    log('sending discord message...');
    log(cURL);
    run(cURL);
    log('...discord message sent');
}
