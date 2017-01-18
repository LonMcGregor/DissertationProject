function get_breadcrumbs(url){
    var pattern = /https?:\/\/[^\s\/]+\/(.+)/g;
    var result = pattern.exec(url)[1]
    return result.split("/")
}

function create_breadcrumb(crumb, url){
    var s = document.createElement('span');
    var a = document.createElement('a');
    a.innerHTML = crumb;
    a.href = url;
    s.innerHTML = ' &gt; ' + a.outerHTML;
    return s;
}

function write_breadcrumbs(crumbs){
    var b = document.getElementById("breadcrumbs");
    var runningUrl = "/";
    for(var i = 0; i < crumbs.length; i++){
        var current = crumbs[i];
        runningUrl += current;
        var c = create_breadcrumb(current, runningUrl);
        b.innerHTML += c.outerHTML;
        runningUrl += "/";
    }
}
document.addEventListener( "DOMContentLoaded", function(){
    write_breadcrumbs(get_breadcrumbs(window.location.href));
}, false);
