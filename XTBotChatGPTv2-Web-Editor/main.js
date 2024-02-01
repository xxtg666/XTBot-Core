const API_URL = "https://xtbot-editor-api.xxtg666.top"; // 自行搭建请修改
document.getElementById("btn-submit").addEventListener("click", function() {
    if(displayType != "JSON"){
        d=editor2json();
    }else{
        d=document.getElementById("edit-json").value;
    }
    check=checkJson(d,type="submit");
    if(check!="pass"){
        notice(check);
        return;
    }
    setbuttonloading("btn-submit",true,true);
    $.ajax({
        url:API_URL+"/upload",
        type:"POST",
        data:d,
        success:function(result){
            console.log(result);
            if(result.startsWith("ERR")){
                notice(result);
                return;
            }
            document.getElementById("s-data-id").innerHTML=result;
            document.getElementById("s-data-id2").innerHTML=result;
            openModal2();
            setbuttonloading("btn-submit",false,true);
        },
        error:function(){
            notice("提交失败");
            setbuttonloading("btn-submit",false,true);
        }
    });
});
let displayType = "EDITOR";
document.getElementById("btn-convert").addEventListener("click", function() {
    if(displayType != "JSON"){
        displayType = "JSON";
        document.getElementById("pg-editor").classList.add("hidden");
        document.getElementById("pg-right").classList.add("hidden");
        document.getElementById("pg-json").classList.remove("hidden");
        document.getElementById("btn-convert-txt").innerHTML = "转到编辑器视图";
        document.getElementById("edit-json").value=editor2json();
    }else{
        check=checkJson(document.getElementById("edit-json").value,type="convert");
        if(check!="pass"){
            notice(check);
            return;
        }
        displayType = "EDITOR";
        document.getElementById("pg-editor").classList.remove("hidden");
        document.getElementById("pg-right").classList.remove("hidden");
        document.getElementById("pg-json").classList.add("hidden");
        document.getElementById("btn-convert-txt").innerHTML = "转到 JSON 视图";
        json2editor();
    }
});
function editor2json(){
    j=[];
    sysmsg=document.getElementById("edit-system").value;
    if(sysmsg!=""){
        j.push({"role":"system","content":sysmsg});
    }
    for(let i=0;i<messages_list.length;i++){
        x = messages_dict[messages_list[i]];
        if(x){
            j.push(x);
        }
    }
    return JSON.stringify(j);
}
function json2editor(){
    clearMessageList();
    j=JSON.parse(document.getElementById("edit-json").value);
    try{
        if(j[0].role=="system"){
            document.getElementById("edit-system").value=j[0].content;
            j.splice(0,1);
        }else{
            document.getElementById("edit-system").value="";
        }
    }catch{}
    for(let i=0;i<j.length;i++){
        createMessage(j[i].role,j[i].content);
    }
}
function checkJson(j,type="null"){
    console.log("检查Json "+j);
    if(type=="convert"){
        convert=true;
        submit=false;
    }else if(type=="submit"){
        submit=true;
        convert=false;
    }
    console.log("convert "+convert,"submit "+submit);
    if (!j.startsWith("[")){
        return "格式错误! 必须是一个列表";
    }
    if(submit){
        if(j=="[]"){
            return "不能提交空列表"
        }
    }
    try{
    JSON.parse(j);
    }catch{
        return "JSON 格式错误! 无法解析";
    }
    j=JSON.parse(j);
    allempty=true;
    for(let i=0;i<j.length;i++){
        if(j[i]==null){
            return "格式错误! 消息中不能有 null";
        }
        if(j[i].role!="user"&&j[i].role!="assistant"&&j[i].role!="system"&&j[i].role!="function"){
            if(j[i].role==undefined){
                return "格式错误! 消息中必须有 role 字段";
            }
            return "格式错误! 消息中 role 只能为 user, assistant, system 或 function";
        }
        if(j[i].content==undefined){
            return "格式错误! 消息中必须有 content 字段";
        }
        if(j[i].content!=""){
            allempty=false;
        }
        if(j[i].role=="function"){
            if(j[i].name==undefined){
                return "格式错误! 消息中 role 为 function 时必须有 name 字段";
            }
            if(j[i].name.length>64){
                return "格式错误! 消息中 name 字段长度不能超过 64";
            }
            if(convert){
                return "消息中有 role 为 function 时暂不支持转换为编辑器视图";
            }
        }
    }
    if(allempty&&submit){
        return "不能提交空数据"
    }
    return "pass";
}
function randomNum(minNum,maxNum){ 
    switch(arguments.length){ 
        case 1: 
            return parseInt(Math.random()*minNum+1,10); 
        case 2: 
            return parseInt(Math.random()*(maxNum-minNum+1)+minNum,10); 
        default: 
            return 0; 
    }
}
let messages_dict={};
let messages_list=[];
function createMessage(role="",content=""){
    message_id = randomNum(100000000,999999999).toString();
    try{
        if(messages_dict[messages_list[messages_list.length-1]].role=="user"){
            message_role = "assistant";
        }else{
            message_role = "user";
        }
    }catch{
        message_role="user";
    }
    if(role!=""){
        message_role=role;
    }
    html=`\
<div class="chat-pg-message" id="message-%num%">
    <div class="chat-message-role" id="btn-switch-message-%num%">
        <div class="chat-message-subheading subheading">
            <span class="chat-message-role-text" id="txt-role-message-%num%">%role%</span>
        </div>
    </div>
    <div class="text-input-with-focus" id="btn-edit-message-%num%">
    <textarea class="text-input text-input-md text-input" id="edit-message-%num%"
            rows="1" tabindex="0" placeholder="[ 写入一条信息 ]"
            header="%role%"></textarea>
    </div>
    <div class="chat-message-button-container" id="btn-del-message-%num%">
        <svg xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20" fill="none"
            class="chat-message-remove-button" width="20"
            height="20">
        <path d="M10 16.6667C13.6819 16.6667 16.6667 13.6819 16.6667 10C16.6667 6.31811 13.6819 3.33334 10 3.33334C6.31814 3.33334 3.33337 6.31811 3.33337 10C3.33337 13.6819 6.31814 16.6667 10 16.6667Z"
            stroke="#6E6E80" stroke-width="1.5"
            stroke-linecap="round" stroke-linejoin="round">
        </path>
        <path d="M7.33337 10H12.6667" stroke="#6E6E80"
            stroke-width="1.5" stroke-linecap="round"
            stroke-linejoin="round"></path>
        </svg>
    </div>
</div>`.replace(/%num%/g, message_id).replace(/%role%/g, message_role);
    messages_dict[message_id]={"role":message_role,"content":content};
    messages_list.push(message_id);
    document.getElementById("list-message").insertAdjacentHTML('beforeend', html);
    document.getElementById("btn-switch-message-"+message_id).addEventListener("click",
        Function(`\
        if(messages_dict[%num%].role=="user"){
            messages_dict[%num%].role="assistant";
        }else{
            messages_dict[%num%].role="user";
        }
        document.getElementById("txt-role-message-%num%").innerHTML=messages_dict[%num%].role;
        document.getElementById("edit-message-%num%").setAttribute("header",messages_dict[%num%].role);
        `.replace(/%num%/g, message_id))
    );
    document.getElementById("edit-message-"+message_id).value = messages_dict[message_id].content;
    document.getElementById("edit-message-"+message_id).style.height = document.getElementById("edit-message-"+message_id).scrollHeight+"px";
    document.getElementById("edit-message-"+message_id).addEventListener("input",
        Function(`\
        messages_dict[%num%].content=document.getElementById("edit-message-%num%").value;
        document.getElementById("edit-message-%num%").style.height = "48px";
        document.getElementById("edit-message-%num%").style.height = document.getElementById("edit-message-%num%").scrollHeight+"px";
        `.replace(/%num%/g, message_id))
    );
    document.getElementById("btn-del-message-"+message_id).addEventListener("click",
        Function(`\
        document.getElementById("message-%num%").remove();
        delete messages_dict[%num%];
        `.replace(/%num%/g, message_id))
    );
    document.getElementById("btn-edit-message-"+message_id).addEventListener("click",
        Function(`\
        document.getElementById("edit-message-%num%").select();
        `.replace(/%num%/g, message_id))
    );
}
function clearMessageList(){
    document.getElementById("list-message").innerHTML="";
    messages_dict={};
    messages_list=[];
}
document.getElementById("btn-addmessage").addEventListener("click", function() {
    createMessage();
});
function notice(info,t=3000) {
    popup = document.getElementById('popup-box');
    popup.innerHTML = info;
    popup.style.display = 'block';
    popup.style.animation = 'slideIn 0.3s forwards';
    setTimeout(function() {
        popup = document.getElementById('popup-box');
        popup.style.animation = 'slideOut 0.3s forwards';
        setTimeout(function() {
            popup.style.display = 'none';
        }, 300);
    }, t);
}
function notice2(info,t=3000) {
    popup = document.getElementById('popup-box2');
    popup.innerHTML = info;
    popup.style.display = 'block';
    popup.style.animation = 'slideIn 0.3s forwards';
    setTimeout(function() {
        popup = document.getElementById('popup-box2');
        popup.style.animation = 'slideOut 0.3s forwards';
        setTimeout(function() {
            popup.style.display = 'none';
        }, 300);
    }, t);
}
document.getElementById("btn-load-from-server").addEventListener("click",function(){
openModal();
})
function openModal() {
    var modal = document.getElementById('modal-inputnum');
    modal.style.display = 'block';
}
function closeModal() {
    var modal = document.getElementById('modal-inputnum');
    modal.style.display = 'none';
}
function openModal2() {
    var modal = document.getElementById('modal-submitsuccess');
    modal.style.display = 'block';
}
function closeModal2() {
    var modal = document.getElementById('modal-submitsuccess');
    modal.style.display = 'none';
}
document.getElementById("btn-confirm-server-data").addEventListener("click",function(){
    id=document.getElementById("edit-data-id").value;
    if(id==""){
        notice("请输入数据 ID");
        return;
    }
    setbuttonloading("btn-confirm-server-data",true,true);
    $.ajax({
        url:API_URL+"/get/"+id,
        type:"GET",
        success:function(result){
            console.log(result);
            if(!result.startsWith("ERR")){
                document.getElementById("edit-json").value=result;
                closeModal();
                displayType = "EDITOR";
                document.getElementById("pg-editor").classList.remove("hidden");
                document.getElementById("pg-right").classList.remove("hidden");
                document.getElementById("pg-json").classList.add("hidden");
                document.getElementById("btn-convert-txt").innerHTML = "转到 JSON 视图";
                json2editor();
            }else{
                notice(result);
            }
            setbuttonloading("btn-confirm-server-data",false,true);
        },
        error:function(){
            notice("获取数据失败");
            setbuttonloading("btn-confirm-server-data",false,true);
        }
    });
})

function getUrlSearch(name) {
    if (!name) return null;
    var after = window.location.search;
    after = after.substr(1) || window.location.hash.split('?')[1];
    if (!after) return null;
    if (after.indexOf(name) === -1) return null;
    var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)');
    var r = decodeURI(after).match(reg);    if (!r) return null;
    return r[2];
}
if(getUrlSearch("id")!=null){
    $.ajax({
        url:API_URL+"/get/"+getUrlSearch("id"),
        type:"GET",
        success:function(result){
            console.log(result);
            if(!result.startsWith("ERR")){
                document.getElementById("edit-json").value=result;
                closeModal();
                displayType = "EDITOR";
                document.getElementById("pg-editor").classList.remove("hidden");
                document.getElementById("pg-right").classList.remove("hidden");
                document.getElementById("pg-json").classList.add("hidden");
                document.getElementById("btn-convert-txt").innerHTML = "转到 JSON 视图";
                json2editor();
            }else{
                notice(result);
            }
        },
        error:function(){
            notice("获取数据失败");
        }
    });
}
document.getElementById("btn-code").addEventListener("click",function(){
    try{
        navigator.clipboard.writeText(".cg editor "+document.getElementById("s-data-id2").innerHTML);
        notice2("命令已复制到剪贴板");
    }catch{
        notice("复制失败,请手动复制");
    }
})
document.getElementById("btn-close-left").addEventListener("click",function(){
    document.getElementById("pg-left").classList.add("hidden");
})
function setCookie(cname,cvalue)
{
    var expires = "expires=Thu, 18 Dec 2043 12:00:00 GMT";
    document.cookie = cname + "=" + cvalue + "; " + expires;
}
function getCookie(cname)
{
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(name)==0) return c.substring(name.length,c.length);
    }
    return "";
}
document.getElementById("edit-key").value = getCookie("apikey");
document.getElementById("edit-key").addEventListener("input", function(){
    setCookie("apikey",document.getElementById("edit-key").value);
})
function openai(model,chat){
    if(displayType!="EDITOR"){
        notice("请先转到编辑器视图");
        return;
    }
    if(!(document.getElementById("edit-key").value.startsWith("sk-") || document.getElementById("edit-key").value.startsWith("sess-"))){
        notice("请输入正确的 API key");
        return;
    }
    setbuttonloading("btn-send-openai",true);
    console.log(JSON.stringify({"model":model,"messages":chat}))
    $.ajax({
        url:"https://openai-api.xxtg666.top/v1/chat/completions", // 使用Cloudflare worker搭建 源码为 openai-api-worker.js
        type:"POST",
        headers:{"Authorization":"Bearer "+document.getElementById("edit-key").value,"content-type":"application/json"},
        data:JSON.stringify({"model":model,"messages":chat}),
        success:function(result){
            document.getElementById("alert-error").classList.add("hidden");
            msg=result["choices"][0]["message"];
            createMessage(msg["role"],msg["content"]);
            setbuttonloading("btn-send-openai",false);
        },
        error:function(result){
            try{
                palert(JSON.parse(result["responseText"])["error"]["message"]);
            }catch{
                notice("请求OpenAI API失败, 未知错误")
            }
            setbuttonloading("btn-send-openai",false);
        }
    });
}
function palert(txt){
    document.getElementById("alert-error-text").innerHTML=txt;
    document.getElementById("alert-error").classList.remove("hidden");
}
function setbuttonloading(id,status,white=false){
    if(white){
        loading="loading-white";
    }else{
        loading="loading";
    }
    if(status){
        document.getElementById(id).classList.add(loading);
        document.getElementById(id).disabled=true;
    }else{
        document.getElementById(id).classList.remove(loading);
        document.getElementById(id).disabled=false;
    }
}

function getradio(name){
	radio = document.getElementsByName(name);
	for (i=0; i<radio.length; i++) {
		if (radio[i].checked) {
			return radio[i].value;
		}
	}
}
document.getElementById("btn-send-openai").addEventListener("click",function(){
    openai(getradio("model"),JSON.parse(editor2json()));
})
