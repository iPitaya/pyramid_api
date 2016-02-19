$(function(){
    $('input[type=text]:first').focus();
    $('input[type=submit]').click(function(){
        var name=$("#name").val();
        var telephone=$("#telephone").val();
        var code=$("#code").val();
        var address=$("#address").val();
        var phoneTest = /^0*(13|14|15|18)\d{9}$/;
        if(name <2 || name > 16 || name==""){
            alert("请输入正确的姓名！");
            $("#name").focus();
            return false;
        }
        if(!phoneTest.test(telephone) || telephone==""){
            alert("请输入正确的电话号码！");
            $("#telephone").focus();
            return false;
        }
        if(code.length != 6 || code==""){
            alert("请输入正确的邮编！");
            $("#code").focus();
            return false;
        }
        if(address.length <3 || address==""){
            alert("请输入正确的地址！");
            $("#address").focus();
            return false;
        }

    })  
})

