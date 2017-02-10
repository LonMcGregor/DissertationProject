/*
 Javascript to be used in conjunction with the feedback view
 */

document.addEventListener('DOMContentLoaded', function() {

var tabs = document.getElementById("file_tabs").getElementsByTagName("span");

for(var i = 0; i < tabs.length; i++){
    tabs[i].addEventListener("click", function(){
        var dataid = this.attributes['data-id'].value;
        var actives = [].slice.call(document.getElementsByClassName("active"));
        actives.forEach(function(item, index, arr){
            if(item.classList.contains("active")){
                item.classList.add("inactive");
                item.classList.remove("active");
            }
        });
        var tabs = [].slice.call(document.getElementById("file_tabs").getElementsByTagName("span"));
        tabs.forEach(function(item, index, arr){
            if(item.attributes['data-id'] && item.attributes['data-id'].value===dataid){
                item.classList.add("active");
                item.classList.remove("inactive");
            }
        });
        var frames = [].slice.call(document.getElementsByTagName("iframe"));
        frames.forEach(function(item, index, arr){
            if(item.attributes['data-id'] && item.attributes['data-id'].value===dataid){
                item.classList.add("active");
                item.classList.remove("inactive");
            }
        });
    })
}
});