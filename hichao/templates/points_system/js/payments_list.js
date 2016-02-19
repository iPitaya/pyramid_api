$(function(){

        var PAY = {
            config :{
                scrollStatus : true,
                offset : 0,
                payListUrl : '/ong/points_system/payments_list/data',
                limit :30
            }
        };
        //初始化  
        //获取id。。。
        PAY.init = function(){
            PAY.config.access_token = PAY.getparam("access_token") || "";
            PAY.getPayList();
            PAY.bindEvent();    
        };
        PAY.bindEvent = function(){
            var win = $(window),
                doc = $(document);
            var winhandle = function(e){
                e.stopPropagation();
                if(PAY.config.scrollStatus && doc.scrollTop()>=doc.height()-win.height()-200){
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
                    PAY.config.scrollStatus = true;
                    var result = response;
                    PAY.insertToHtml(result);
                },
                error :function(){

                }
            })
        };
        PAY.insertToHtml = function(data){
            if(data.payments_list && data.payments_list.length >0){
                PAY.config.offset += data.payments_list.length;
                console.log(PAY.config.offset)
                var payArray = [];
                $.each(data.payments_list,function(i,item){
                 // alert(item.points);
                  if(item.points>0){ payArray.push('<li> <p class="date">'+item.date+'</p> <div class="pic"> <img src="'+item.image_url+'" width="100%" /></div> <span class="tit">'+item.description+'</span> <span class="red">+'+item.points+'</span> </li>');
                    }
                    else{
                        payArray.push('<li> <p class="date">'+item.date+'</p> <div class="pic"> <img src="'+item.image_url+'" width="100%" /></div> <span class="tit">'+item.description+'</span> <span class="green">'+item.points+'</span> </li>');
                    }    
                })
                $("ul").append(payArray.join(""));
                if(data.payments_list.length >= PAY.config.limit){
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

