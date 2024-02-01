const GH_TOKEN = "" // 非公开内容(用于访问网页编辑器数据仓库的github auth token)
const GH_REPO = "" // 非公开内容(用于存放网页编辑器数据的github仓库 格式为 user/repo)
const header = {"Authorization":"Bearer "+GH_TOKEN,"User-Agent": "Awesome-Octocat-App"}
const _options = {headers:header}

async function getJsonFromIssueNumber(IssueNumber){
  let REQUEST = new Request("https://api.github.com/repos/"+GH_REPO+"/issues/"+IssueNumber.toString(),_options);
  let RESPONSE = await fetch(REQUEST);
  let Json = await RESPONSE.json();
  if(Json.body==undefined){
    return undefined
  }
  if(Json["state"]!="open"){
    return "ERR 此数据不可用"
  }
  return Json.body; 
}

function toJson(JsonStr){
  return JSON.parse(JsonStr)
}

async function createIssue(body,_form="XTBot"){
  let requestOptions = {
    headers: header,
    method: 'POST',
    body: JSON.stringify({"title":_form+" Chat History","body":body})
  };
  let REQUEST = new Request("https://api.github.com/repos/"+GH_REPO+"/issues",requestOptions);
  let RESPONSE = await fetch(REQUEST);
  let Json = await RESPONSE.json();
  return Json.number.toString();
}

function ac(response){
  response.headers.append('Access-Control-Allow-Origin','*');
  response.headers.set('Access-Control-Allow-Origin','*');
  return response;
}
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url).pathname;
    if(url.startsWith('/upload')){
      if (request.method != "POST") {
        return ac(new Response("ERR 请求方式错误"));
      }
      let t = await request.text();
      let form = "XTBot";
      if(url.toLowerCase().endsWith("xdbot")){
        form = "XDbot";
      }
      try{
        toJson(t);
        if(! t.startsWith("[")){
          return ac(new Response("ERR Json格式不正确"));
        }
      }catch(e){
        return ac(new Response("ERR Json格式不正确"));
      }
      return ac(new Response(await createIssue(t,form)));
    }
    else if(url.startsWith('/get/')){
      if (request.method != "GET") {
        return ac(new Response("ERR 请求方式错误"));
      }
      let r = await getJsonFromIssueNumber(url.replace("/get/",""))
      if(r){
        return ac(new Response(r));
      }else{
        return ac(new Response("ERR 数据不存在"));
      }
    }
    else{
      return ac(new Response("not found"));
    }
  },
};