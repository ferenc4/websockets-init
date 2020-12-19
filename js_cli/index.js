let socket = io(location.protocol + ' //' + document.domain + ':' + location.port);
let client_id = Math.random().toString(36).substring(2, 12);

socket.on('connect', function () {
    console.log('Making new connection')
    socket.emit('my_custom_event', {
        data: 'User Connected'
    })
});

socket.on('disconnect', function () {
    console.log('Disconnected')
    socket.io.reconnect();
});

socket.on('event_response', function (msg) {
    console.log('Event got the response')
    if (msg['success'] === true) {
        make_client_action(msg['data']);
    }
});
