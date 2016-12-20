function logToPage(o){
    log = document.getElementById('log');
    log.appendChild(document.createElement('p'));
    s = document.createTextNode(o.toString());
    log.appendChild(s);
    if(Notification.permission === "granted"){
        new Notification(o.toString());
    }
}
logToPage("No server updates");

Notification.requestPermission().then(function(result) {
  logToPage(Notification.permission);
});

var sock = new WebSocket('ws://localhost:8000/messages');
sock.onopen = function() {
    logToPage('socket object opened');
};
sock.onmessage = function(e) {
    logToPage('message received: ' + e.data.toString());
};
sock.onclose = function() {
    logToPage('socket object closed');
};

b = document.createElement('button');
b.appendChild(document.createTextNode('close'));
b.onclick = function(){sock.close()};
document.body.appendChild(b);

c = document.createElement('button');
c.appendChild(document.createTextNode('send message to server'));
c.onclick = function(){sock.send('echo')};
document.body.appendChild(c);
