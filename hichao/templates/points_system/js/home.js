$(function(){
    var HOME = {};
    HOME.init = function(){
        HOME.bindEvent();
    };
    HOME.bindEvent = function(){
        $(".other").on("click","a",function(e){
            var curT = $(this),
                href = curT.attr("href"),
                li = curT.parent();
            sessionStorage.selected = li.attr("_id");
        })
    }
    HOME.init();
})
