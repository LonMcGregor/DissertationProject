/* Script that manages a notifications view
and also connects to a websocket to allow
for notification updates
 */

var note_count = 0;

function update_note_count(){
    /* increment and update the notificaiton count */
    note_count++;
    var note_count_box = document.getElementById('note_count');
    note_count_box.innerText = "Notifications (" + note_count + ")";
}

function notify(o){
    /* fire a notification */
    update_note_count();
    html_notify(o);
    html_5_notify(o);
}

function html_notify(o){
    /* add an item to the basic html notificaitons box */
    var note_message_box = document.getElementById('note_messages_container');
    var note = document.createElement('div');
    note.className = 'note';
    note.innerHTML = o.toString();
    note_message_box.appendChild(note);
}

function html_5_notify(o){
    /* display an HTML5 web notificaiton */
    if(Notification.permission === "granted"){
        new Notification(o.toString());
    }
}

/* on page load double-check notification permissions */
Notification.requestPermission().then(function() {
    /*notify("HTML5 Notifications:" + Notification.permission);*/
});

function toggle_notes_status(){
    /* show or hide the basic html notifications box */
    var c = document.getElementById('note_messages_container').className;
    if(c==='collapsed'){
        document.getElementById('note_messages_container').className = 'opened';
    } else {
        document.getElementById('note_messages_container').className = 'collapsed';
    }
}

/* object offering functionality for connecting to sockets */
socketMan = {
    open: function() {
        /*notify('Notifications Socket Opened');*/
    },

    msg: function(e) {
        notify(e.data.toString());
    },

    close: function() {
        notify('Notifications Socket Closed');
    }
};


/* actually connect to socket on page load */
var sock = new WebSocket('ws://localhost:8000/messages');
sock.onopen = socketMan.open;
sock.onmessage = socketMan.msg;
sock.onclose = socketMan.close;
