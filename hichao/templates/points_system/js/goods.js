$(function(){
    var GOODS = {
        init : function(){
            var self = this;
            self.judgeImg();
            self.lazyload();
        },
        judgeImg : function(){
            $(".main-content img").each(function(){
                if($(this).offset().top < $(window).innerHeight()){
                    $(this).attr("src",$(this).attr("lazy-src"));
                }
            })
        },
        lazyload : function(){
            if($(".main-content img").size()>0){
                
                var win = $(window),
                    winheight = win.innerHeight();
                win.scroll(function(){
                    var scrollTop = win.scrollTop();
                    $(".main-content img").each(function(){
                        if($(this).attr("src")){
                            return true;
                        }
                        if($(this).attr("lazy-src")){
                            if($(this).offset().top - scrollTop < winheight){
                                $(this).attr("src",$(this).attr("lazy-src"));
                            }
                        }
                    })
                })
            }
        }
    };
    GOODS.init();
})
