
document.addEventListener('DOMContentLoaded', function() {
$("#textup").on("click", function(){
    var oldvalue = $("main").css("font-size");
    var newvalue = Number(oldvalue.substring(0, oldvalue.length-2)) + 1;
    $("main").css("font-size", newvalue+"px");
});
$("#textdown").on("click", function(){
    var oldvalue = $("main").css("font-size");
    var newvalue = Number(oldvalue.substring(0, oldvalue.length-2)) - 1;
    $("main").css("font-size", newvalue+"px");
});
$("#highlight").on("click", function(){
    var highlights = $(".highlight");
    var nohighlights = $(".noHighlight");
    highlights.addClass("noHighlight");
    highlights.removeClass("highlight");
    nohighlights.addClass("highlight");
    nohighlights.removeClass("noHighlight");
});
$("#download").on("click", function(){
    var gets = window.location.href.indexOf("?");
    var dlurl = window.location.href.substring(0, gets);
    window.location.assign(dlurl);
});
});