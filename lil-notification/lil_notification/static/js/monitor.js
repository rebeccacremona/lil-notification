const wrapper = document.getElementById('alert-wrapper');
const container = document.getElementById('alert-container');
const testMessaging = document.getElementById('test-messaging');

const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
const socket = new ReconnectingWebSocket(
    `${ws_scheme}://${window.location.host}/ws/${app}/${tier}`
);

socket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    let message = data['message'];
    if (data['active']){
        wrapper.classList.add('active');
        container.innerHTML = `<p>${message}</p>`;
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
        'message': `Alert! Test message sent at ${(new Date()).toLocaleTimeString('en-US')}`,
        'active': true
    }));
};
