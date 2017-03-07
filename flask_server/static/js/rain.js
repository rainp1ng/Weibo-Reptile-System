/**
 * Created by rainp1ng on 4/17/16.
 */

var user="id";
var passwd="passwd";
var vercode="vercode";
var log_flag = "logflag";
var cur_ip="ip";

var $$=document;

var current_ip=$$.getElementById("ip");
if(current_ip!=null){
    if(current_ip.value=="")
        current_ip.value=window.location.href;
}

var login_btn=$$.getElementById("login-btn");

if(login_btn!=null){
login_btn.onclick = function () {
    var user_val=$$.getElementById(user);
    var password_val=$$.getElementById(passwd);
    var cur_ip_val=$$.getElementById(cur_ip);
    var vercode = $$.getElementById('vercode');
    var log_flag = $$.getElementById('log_flag');

    var data=new FormData;
    data.append(user,user_val.value);
    data.append(passwd,password_val.value);
    data.append('vercode',vercode.value);
    data.append('logflag', log_flag.value);
    data.append("ip",cur_ip_val.value);
    var re_val=$$.getElementById("remember");
    data.append("remember",re_val.checked);
    url="/login";
    var result=request("post",url,data);
    var json_result = jQuery.parseJSON(result);
    if(json_result['stat']!="200"){
        //alert("密码错误");
        tip=$$.getElementById("tip");
        tip.style.visibility="visible";
        tip.innerHTML = json_result['reason']
        get_vercode(json_result['vercode_no']);
    }else{
        //alert("登录成功");
        //alert(result);
        $$.location.href=json_result['furl'];
    }
};
}

function request(action,url,data){
    var request=new XMLHttpRequest();
    if(action=="post"){
        request.open('POST',url,false);
        request.send(data);
        //alert(request.responseText);
        return request.responseText;
    }else{
        request.open('GET',url,false);
        request.send();
        //alert(request.responseText);
        return request.responseText;
    }
};


var input_user=$$.getElementById(user);
function user_onblur () {
    user_val=$$.getElementById(user);
    password_val=$$.getElementById(passwd);
    var data = new FormData;
    data.append(user,user_val.value);
    data.append(passwd,password_val.value);
    url="/check_log";
    var result=request("post",url,data);
    var json_result = jQuery.parseJSON(result);
    if(json_result['stat']=='200'){
        set_log_true()
    }else if(json_result['stat']=='502'){
        get_vercode(json_result['vercode_no'])
    }else{

    }
}


function set_log_true(){
    var log_flag = $$.getElementById('log_flag');
    log_flag.value = '1';
}


var vercode_img=$$.getElementById('vercode_img');
function get_vercode(no){
    vercode_img.src = '/static/png/vercode'+no+'.png';
}


var input_passwd=$$.getElementById(passwd);
function passwd_onblur(){
}