/* Script file that offers functionality to generate
 * breadcrumb style links at top of page, and also
 * scrape them from the url. */

function get_breadcrumbs(url){
    /* extract possible crumbs from the url path */
    var pattern = /https?:\/\/[^\s\/]+\/(.+)/g;
    var result = pattern.exec(url)[1]
    return result.split("/")
}

function create_breadcrumb(crumb, url){
    /* given a crumb and a url, generate an html element for this */
    var s = document.createElement('span');
    var a = document.createElement('a');
    a.innerHTML = crumb;
    a.href = url;
    s.innerHTML = ' &gt; ' + a.outerHTML;
    return s;
}

function write_breadcrumbs(crumbs){
    /* given an array of crumbs, fill out the breadcrumb container */
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

/* when the document loads, start acting on the location url */
document.addEventListener( "DOMContentLoaded", function(){
    write_breadcrumbs(get_breadcrumbs(window.location.href));
}, false);
