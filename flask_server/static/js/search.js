/**
 * Created by rainp1ng on 4/19/16.
 */

var $$ = document;
var search_tip = $$.getElementById('search_tip');
var display_grid = $$.getElementById('display_grid');
var scrap_listen_div = $$.getElementById('scrap_listen_div');
var scrap_input = $$.getElementById('sd');


if(scrap_input!=null){
    listen_scrap_info(scrap_input.value, 0);
}

function listen_scrap_info(scrap_id, id){
    req_url = '/read_scrap/' + scrap_id + '/' + id;
    var res = request('get', req_url)
//    alert('res:' + res);
    var result_list = jQuery.parseJSON(res);
    var final_result = '';
    for(result in result_list){
        scrap_listen_div.innerHTML += '<p>' + result_list[result]['return_content'] + '</p>';
        final_result = result_list[result];
    }
    if(result_list.length == 0){
        setTimeout(function(){
            listen_scrap_info(scrap_id, id)
        }, 1500);
    }else if(parseInt(final_result['stat_content'])==0){
        setTimeout(function(){
            listen_scrap_info(scrap_id, final_result['id'])
        }, 1500);
    }else if(parseInt(final_result['stat_content'])==1){
        scrap_listen_div.innerHTML += '<p><a href="/search">查看爬虫结果</a></p>';
    }

};


function sleep(numberMillis) {
    var now = new Date();
    var exitTime = now.getTime() + numberMillis;
    while (true) {
        now = new Date();
        if (now.getTime() > exitTime)
            return;
    }
};


var search_weibo_btn = $$.getElementById('search_weibo_btn');
if(search_weibo_btn != null){
    search_weibo_btn.onclick = function (){
        var search_username = $$.getElementById('search_username');
        var search_keyword = $$.getElementById('search_keyword');
        var username = search_username.value;
        var keyword = search_keyword.value;
//        alert(username);
//        alert(keyword);
        if(username == '' && keyword =='')
            return;

        display_grid.style.display = 'none';
        search_tip.style.display = '';
        search_tip.innerHTML = '查询中...';
        var weibo_list = search_weibo_list(username, keyword);
        show_weibo_result(weibo_list);
    };
}


function search_weibo_list(username, keyword){
    var search_weibo_url = '/search_scraped_weibo/' + username + '?keyword=' + keyword;
    var result = request('get', search_weibo_url);
//    alert(result);
    var json_result = jQuery.parseJSON(result);
    if(json_result['stat'] == '200'){
        return json_result['result'];
    }else{
        return '';
    }
};


function show_weibo_result(weibo_list){
    if(weibo_list.length==0){
        search_tip.innerHTML = '搜索无结果或网络异常!';
    }else{
        var display_grid = $$.getElementById('display_grid');
        var result_html = '<hr/>'
        for(i in weibo_list){
            var weibo = weibo_list[i]
//            alert(user['title']);
//            alert(user['user_id']);
            result_html += '<h4><a href="' + weibo['link'] + '">@' + weibo['username'] + '</a></h4>';  // 发布者昵称
            result_html += '<p>' + weibo['pub_time'] + ' ' + weibo['pub_dev'] + '</p>'; // 发布时间与发布设备
            result_html += '<p>' + weibo['content'] + '</p>';        // 微博内容
            if(weibo['is_repost'] == '1'){
                result_html += '<h4><a href="' + weibo['repost_from_link'] + '">' + weibo['repost_from_username'] + '</a></h4>'  // 被转发者昵称
                result_html += '<p>' + weibo['repost_from_pub_time'] + ' ' + weibo['repost_from'] + '</p>';       // 原微博发布时间与设备
                result_html += '<p>' + weibo['repost_from_content'] + '</p>';   // 原微博内容
            }
            // 处理图片

            result_html += '<hr/>'
        }
        display_grid.innerHTML = result_html
        search_tip.innerHTML = ''
        search_tip.style.display = 'none';
        display_grid.style.display = '';
    }
};


var search_btn = $$.getElementById('search_btn');
if(search_btn != null){
    search_btn.onclick = function (){
        display_grid.style.display = 'none';
        search_tip.style.display = '';
        search_tip.innerHTML = '搜索中...';
        var search_username = $$.getElementById('search_username');
        var search_word = search_username.value;
//        alert(search_word);
        var user_list = search_user(search_word);
        show_result(user_list);
    };
}


function show_result(user_list){
    if(user_list.length==0){
        search_tip.innerHTML = '搜索无结果或网络异常!';
    }else{
        var search_result_grid = $$.getElementById('search_result_list');
        var result_html = ''
        for(user in user_list){
//            alert(user['title']);
//            alert(user['user_id']);
            result_html +=  '<tr><td></td>'
            result_html += '<td>' + user_list[user]['title'] + '</td>'
            result_html += '<td>' + user_list[user]['user_id'] + '</td><td></td>'
            result_html += '<td><button class="btn btn-default" onclick="to_scrap(' + user + ')">爬取</button></td><td></td></tr>'
        }
        search_result_grid.innerHTML = result_html
        search_tip.innerHTML = ''
        search_tip.style.display = 'none';
        display_grid.style.display = '';
    }
};


function to_scrap(id){
    document.location.href="/scrap/"+id;
};


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


function search_user(search_word){
    var search_url = '/search_user/' + search_word;
    var result = request('get', search_url);
//    alert(result);
    result = jQuery.parseJSON(result);
    if(result['stat']=='200'){
//        alert(result['result']);
        return result['result']
    }else{
        return []
    }
};
