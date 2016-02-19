$(function(){

var PAY = {
    config :{
        scrollStatus : true,
        offset : 0,
        payListUrl : '/ong/points_system/order_list/data',
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
            PAY.config.scrollStatus = true;
            var result = response;
            PAY.insertToHtml(result);
           
        },
        error :function(){

        }
    })
};
PAY.insertToHtml = function(data){
    if(data.order_list && data.order_list.length >0){
        PAY.config.offset += data.order_list.length;
        console.log(PAY.config.offset)
        var payArray = [];
        $.each(data.order_list,function(i,item){
           if(item.status==0){
                payArray.push('<li class="cf"><img src="'+item.goods_image_url+'" alt="'+item.goods_title+'"  title="'+item.goods_title+'" height="85" width="85"/><dl><dt>'+item.goods_title+'</dt><dd class="cost">消耗：'+item.points+'糖豆</dd><dd>状态：<span class="pink">'+item.status_desc+'</span></dd></dl></li><div class="line"></div>');
            }else{
                 payArray.push('<li class="cf"><img src="'+item.goods_image_url+'" alt="'+item.goods_title+'"  title="'+item.goods_title+'" height="85" width="85"/><dl><dt>'+item.goods_title+'</dt><dd class="cost">消耗：'+item.points+'糖豆</dd><dd>状态：<span>'+item.status_desc+'</span></dd></dl></li><div class="line"></div>');   
            }
       
           
            
        })
        $(".main-content").append(payArray.join(""));
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
