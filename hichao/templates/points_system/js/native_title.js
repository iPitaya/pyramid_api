(function(){
    var title = document.getElementsByTagName("title")[0].innerHTML;
    window.doGetTitle = function(e){//
        
        wodfan.doTitleChange(title);
    }
    //IOS题目
    function connectWebViewJavascriptBridge(callback) {
            if (window.WebViewJavascriptBridge) {
                callback(WebViewJavascriptBridge)
         } else {
                document.addEventListener('WebViewJavascriptBridgeReady', function() {
                callback(WebViewJavascriptBridge)  }, false)                                                                                   }
         }

                                                                                                                                        connectWebViewJavascriptBridge(function(bridge) {
                                                                                                                                                                          // alert("123");
                                                                                                                                                                           var uniqueId = 1                                                        
                                              window.WebViewJavascriptBridge.callHandler('doAction',{'actionKey':'title','titleName':title});
                                           bridge.init(function(message, responseCallback) {                                                                               var data = { 'Javascript Responds':'Wee!' }
                                           responseCallback(data)
                                            })                                                                                          })
    window.doMineChange = function(){//ajax请求任务完成数
        var url = '/ong/points_system/home_activity',
            token = $.trim($(".daily").attr("token")) || "";
        var selected = sessionStorage.selected || "";
        if(!token){return false;}
        if(selected == ""){return false;}
        $.ajax({
            type : "get",
            url : url,
            data : {access_token : token,activity_id : selected},
            success : function(response){
                var result = response;
                if(result.activity_id != ""){
                    $(".other li").each(function(){
                        if($(this).attr("_id") == result.activity_id){
                            if(result.points == result.points_limit){
                                $(this).find(".result").removeClass("red");
                            }
                            $(this).find(".process").html('+'+result.points+'/'+result.points_limit);
                            return false;
                        }
                    })
                }
            },
            error : function(i,o){
                alert(o)
            }
        })

        
    }
})()
