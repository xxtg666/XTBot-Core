const GH_TOKEN = "" // 非公开内容(用于访问状态信息仓库的github auth token)
const GH_REPO = "" // 非公开内容(用于存放状态信息的github仓库 格式为 user/repo)
// 自行搭建请修改下方 PAGE_URL
const TOP = `\
<!DOCTYPE html>
<html lang="zh">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>XTBotChatGPTv2 状态页面</title>
    <link rel="icon" href="https://avatars.githubusercontent.com/u/123957996" sizes="16x16">
    <link rel="stylesheet" href="https://cdn.staticfile.org/bulma/0.9.4/css/bulma.min.css">
    <style>
        html{background: linear-gradient(to left, lightblue , skyblue);}
        .center{text-align: center;}
    </style>
    <script>
    let PAGE_URL = "https://xtbot-status.xxtg666.top/";
    function getReloadTimes() {
      var after = window.location.search;
      after = after.substr(1) || window.location.hash.split('?')[1];
      if (!after) return 0;
      if (after.indexOf("r") === -1) return 0;
      var reg = new RegExp('(^|&)' + "r" + '=([^&]*)(&|$)');
      var r = decodeURI(after).match(reg);
      if (!r) return 0;
      return Number(r[2]);
    }
    </script>
  </head>
  <body>
  <section class="section">
    <div class="container">
    <article class="message is-info">
  <div class="message-header">
    <p>XTBotChatGPTv2 状态页面</p>
  </div>
  <div class="message-body">
    可查询 XTBotChatGPTv2 请求状态 剩余 <strong><span id="rtime">15</span></strong> 秒自动刷新
  </div>
</article>
`
const BOTTOM = `\
<div class="notification is-primary is-light center">
          <a href="https://xtbot-status.xxtg666.top/"><strong>XTBotChatGPTv2-Status</strong></a> by <a href="https://github.com/xxtg666"><strong>xxtg666</strong></a>
        </div>
</div>
</section>
</body>
</html>
`
const PART1_FREE = `\
<div class="modal" id="no-auto-reload-notice">
  <div class="modal-background"></div>
  <div class="modal-content">
    <div class="box">
      <p>XTBot 当前长时间处于 <strong>空闲</strong> 状态, 本页面将 <strong>不会</strong> 自动刷新, 请 <button class="button is-primary is-light is-small" onclick="window.location.href=PAGE_URL+'?r=2';">点击此处</button> 手动刷新</p>
    </div>
  </div>
</div>
<script>
let grt = getReloadTimes();
if(grt < 0){grt = 0;}
if(grt <= 3){
  window.setTimeout(function(){
    window.location.href=PAGE_URL+"?r="+(grt+1).toString();
  },15500);
  let rtime = 15;
  window.setInterval(function(){
    rtime -= 1;
    document.getElementById("rtime").innerHTML = rtime;
  }, 1000);
}else{
  if(grt == 4){
    document.getElementById("no-auto-reload-notice").classList.add("is-active");
  }
}
</script>
<article class="message is-success">
<div class="message-header">
  <p>当前状态 - 空闲</p>
</div>
<div class="message-body">
  在群内使用 <strong>.cg</strong> 命令即可发送信息
</div>
</article>
`
const PART2_TOP = `\
<article class="message is-link">
<div class="message-header">
  <p>历史请求记录 - 仅显示最近 10 条</p>
</div>
<div class="message-body">
`
const PART2_BOTTOM = `\
</div>
</article>
`
async function handleRequest(request) {
  let html = TOP;
  const REQUEST_getIssueList = new Request("https://api.github.com/repos/"+GH_REPO+"/issues",{headers:{"Authorization":"Bearer "+GH_TOKEN,"User-Agent": "Awesome-Octocat-App"}});
  const RESPONSE_getIssueList = await fetch(REQUEST_getIssueList);
  const JSON_getIssueList = await RESPONSE_getIssueList.json();
  if(JSON_getIssueList[0]!=undefined){html += processTask(JSON_getIssueList[0]["body"])}else{html += PART1_FREE}
  html += PART2_TOP + (await processHistory()) + PART2_BOTTOM;
  html += BOTTOM;
  let newResponse = new Response(replaceAll(html,"\n",""), {
    headers: {
      "content-type": "text/html;charset=UTF-8",
    },
  })
  newResponse.headers.append('Cache-Control','no-store')
  newResponse.headers.set('Cache-Control','no-store')
  return newResponse
}

addEventListener("fetch", event => {
  return event.respondWith(handleRequest(event.request))
})

function processTask(body) {
  let datas = body.split("\n")
  let time = datas[0]
  let user = datas[1]
  let model = datas[2]
  let msg = cutstr(datas[3],20)
  return `\
<article class="message is-warning">
<div class="message-header">
  <p>当前状态 - 请求中</p>
</div>
<div class="message-body">
  <p>正在使用 <strong>%model%</strong> 处理用户 <strong>%user%</strong> 的信息: <strong>%msg%</strong></p>
  <p>已用时 <strong id="time"></strong> s</p>
</div>
</article>
<script>
window.setInterval(function(){document.getElementById("time").innerHTML = Date.now()/1000 - %time%}, 200);
window.setTimeout(function(){window.location.href=PAGE_URL;},15500);
let rtime = 15;
window.setInterval(function(){
  rtime -= 1;
  document.getElementById("rtime").innerHTML = rtime;
}, 1000);
</script>
`.replace("%time%",time).replace("%user%",user).replace("%model%",model).replace("%msg%",msg)
}

function cutstr(str, len) {
  var str_length = 0;
  var str_len = 0;
  var str_cut = new String();
  str_len = str.length;
  for (var i = 0; i < str_len; i++) {
      var a = str.charAt(i);
      str_length++;
      if (escape(a).length > 4) {
          str_length++;
      }
      str_cut = str_cut.concat(a);
      if (str_length >= len) {
          str_cut = str_cut.concat("...");
          return str_cut;
      }
  }
  if (str_length < len) {
      return str;
  }
}

async function processHistory(){
  const REQUEST_getIssueList = new Request("https://api.github.com/repos/"+GH_REPO+"/issues?state=closed",{headers:{"Authorization":"Bearer "+GH_TOKEN,"User-Agent": "Awesome-Octocat-App"}});
  const RESPONSE_getIssueList = await fetch(REQUEST_getIssueList);
  let JSON_getIssueList = await RESPONSE_getIssueList.json();
  JSON_getIssueList = JSON_getIssueList.slice(0,10)
  let lens = JSON_getIssueList.length;
  let r = "";
  for(let i=0;i<lens;i++){
    r += processHistoryTask(JSON_getIssueList[i]["body"])
  }
  return r
}

function processHistoryTask(body) {
  let datas = body.split("\n")
  let time = formatDate((Number(datas[0])+28800)*1000)
  let user = datas[1]
  let model = datas[2]
  return `\
<p>用户 <strong>%user%</strong> 在 <strong>%time%</strong> 使用了 <strong>%model%</strong></p>`.replace("%time%",time).replace("%user%",user).replace("%model%",model)
}

function formatDate(value) {
  var date = new Date(value);
  var y = date.getFullYear(),
    m = date.getMonth() + 1,
    d = date.getDate(),
    h = date.getHours(),
    i = date.getMinutes(),
    s = date.getSeconds();
  if (m < 10) { m = '0' + m.toString(); }
  if (d < 10) { d = '0' + d.toString(); }
  if (h < 10) { h = '0' + h.toString(); }
  if (i < 10) { i = '0' + i.toString(); }
  if (s < 10) { s = '0' + s.toString(); }
  var t = y + '-' + m + '-' + d + ' ' + h + ':' + i + ':' + s;
  return t;
}

function replaceAll(string, search, replace) {
  return string.split(search).join(replace);
}