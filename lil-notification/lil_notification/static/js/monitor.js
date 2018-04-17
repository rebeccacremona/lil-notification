const wrapper = document.getElementById('alert-wrapper');
const container = document.getElementById('alert-container');
const testMessaging = document.getElementById('test-messaging');

const scheme = window.location.protocol == "https:" ? "wss" : "ws";
const socket = new ReconnectingWebSocket(
    `${scheme}://${window.location.host}/ws/${app}/${tier}`
);


socket.onmessage = function(e) {
    let data = JSON.parse(e.data)
    if (data['active']){
        wrapper.classList.add('active');
        container.innerHTML = `<p>${messageFromData(data)}</p>`;
    } else {
        wrapper.classList.remove('active');
        container.innerHTML = '';
    }
};

socket.onclose = function(e) {
    console.info('Socket closed.');
};

testMessaging.onclick = function(e) {
    socket.send(JSON.stringify({
        'active': true,
        'status': `Test message sent at ${(new Date()).toLocaleTimeString()}`,
    }));
};

function messageFromData(data){
    let msg = "Heads up! ";
    if (data['status'].includes('Test message')){
        msg += data['status'];
    } else {
        if (data['status'] == 'imminent'){
            msg += "We expect to be down for maintenance ";
            if (data['scheduled_start']){
                msg += `beginning at ${localize(data['scheduled_start'])}. `
            } else {
                msg += "momentarily. "
            }
        } else if (data['status'] == 'in_progress'){
            msg += "We are down for maintenance. ";
        } else {
            msg += 'We might not be available for the next short while. ';
        }
        if (data['scheduled_end']){
            msg += `We hope to be back around ${localize(data['scheduled_end'])}. `
        }
    }
    return msg;
}

function localize(dateString){
    // you just try to get rid of the seconds in IE....
    return (new Date(dateString)).toLocaleTimeString();
}
