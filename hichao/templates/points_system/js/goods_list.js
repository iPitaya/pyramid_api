$(function(){
        var PAY = {
            config :{
                listwidth : 0.44,
                scrollStatus : true,
                offset : 0,
                payListUrl : '/ong/points_system/goods_list/data',
                limit :10
            }
        };
        //初始化  
        //获取id。。。
        PAY.init = function(){
            PAY.config.access_token = PAY.getparam("access_token") || "";
            PAY.config.currentWidth = $(window).width()*PAY.config.listwidth;
            PAY.getPayList();
            PAY.bindEvent();    
        };
        PAY.bindEvent = function(){
            var win = $(window),
                doc = $(document);
            var winhandle = function(e){
                e.stopPropagation();
                if(PAY.config.scrollStatus && doc.scrollTop()>=doc.height()-win.height()-100){
                    PAY.config.scrollStatus = false;
                    PAY.getPayList(PAY.config.offset);
                }
            }
            win.on("scroll",winhandle);
        };
        //ajax请求获取消费列表数据
        PAY.getPayList = function(offset){

            var offset = offset || 0;
            if(!PAY.config.access_token){return false;}
            $.ajax({
                type : "get",
                url : PAY.config.payListUrl,
                data : {access_token:PAY.config.access_token,offset:offset,limit:PAY.config.limit},
                success : function(response){
                    var result = response;
                    PAY.insertToHtml(result);
                   
                },
                error :function(){

                }
            })
        };
        PAY.insertToHtml = function(data){
            if(data.goods_list && data.goods_list.length >0){
                PAY.config.offset += data.goods_list.length;
                console.log(PAY.config.offset)
                var host = window.location.host;
                var payArray = [];
                $.each(data.goods_list,function(i,item){
                  
                        payArray.push('<li><a href="goods?access_token='+data.access_token+'&goods_id='+item.id+'"><dl><dt style="overflow:hidden;width:'+(PAY.config.currentWidth*0.9)+'px;height:'+PAY.config.currentWidth+'px"><img src="'+item.image_url+'" width="100%" title="'+item.title+'"/></dt><dd>'+item.title+'</dd></dl><p class="h"><img class="candy candy1" src="http://api.beta.hichao.com/ong/static/img/candy_07.png" width="16%"/><span class="no">'+item.points_price+'</span></p><div class="line"></div><p class="msg">共'+item.inventory+'件 <span>剩余'+item.remain+'件</span></p></a></li>');
                   
                    
                })
                $(".main-content ul").append(payArray.join(""));
                if(data.goods_list.length >= PAY.config.limit){
                    PAY.config.scrollStatus = true;
                }
            }
        };
        PAY.getparam = function(name,url){
            var search = url || document.location.search;
            var pattern = new RegExp("[?&]"+name+"\=([^&]+)", "g");
            var matcher = pattern.exec(search);
            var items = null;
            if(null != matcher){
                try{
                    items = decodeURIComponent(decodeURIComponent(matcher[1]));
                }catch(e){
                    try{
                        items = decodeURIComponent(matcher[1]);
                    }catch(e){
                        items = matcher[1];
                    }
                }
            }
            return items;
        };
        PAY.init();
    })
