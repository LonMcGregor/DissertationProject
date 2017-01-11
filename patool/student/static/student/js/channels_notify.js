var note_count = 0;

function update_note_count(){
    note_count++;
    var note_count_box = document.getElementById('note_count');
    note_count_box.innerText = "Notifications (" + note_count + ")";
}

function notify(o){
    update_note_count();
    html_notify(o);
    html_5_notify(o);
}

function html_notify(o){
    var note_message_box = document.getElementById('note_messages_container');
    var note = document.createElement('div');
    note.className = 'note';
    note.innerHTML = o.toString();
    note_message_box.appendChild(note);
}

function html_5_notify(o){
    if(Notification.permission === "granted"){
        new Notification(o.toString());
    }
}

Notification.requestPermission().then(function() {
    notify("HTML5 Notifications:" + Notification.permission);
});

function toggle_notes_status(){
    var c = document.getElementById('note_messages_container').className;
    if(c==='collapsed'){
        document.getElementById('note_messages_container').className = 'opened';
    } else {
        document.getElementById('note_messages_container').className = 'collapsed';
    }
}


socketMan = {
    open: function() {
        notify('Notifications Socket Opened');
    },

    msg: function(e) {
        notify(e.data.toString());
    },

    close: function() {
        notify('Notifications Socket Closed');
    }
};


var sock = new WebSocket('ws://localhost:8000/messages');
sock.onopen = socketMan.open;
sock.onmessage = socketMan.msg;
sock.onclose = socketMan.close;
