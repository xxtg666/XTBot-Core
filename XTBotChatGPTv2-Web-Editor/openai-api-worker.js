export default {
    async fetch(request, env) {
      let pathname = request.url;
      pathname = pathname.replace("https://openai-api.xxtg666.top/","https://api.openai.com/") // 自行修改为你的域名
      try {
        const newRequest = new Request(pathname,request)
        newRequest.headers.set('origin', pathname)
        newRequest.headers.set('referer', pathname)
        const response = await fetch(newRequest)
        const newResponse = new Response(response.body, response)
        newResponse.headers.append('Access-Control-Allow-Origin','*')
        newResponse.headers.set('Access-Control-Allow-Origin','*')
        newResponse.headers.append('Cache-Control','no-cache')
        newResponse.headers.set('Cache-Control','no-cache')
        newResponse.headers.append('Pragma','no-cache')
        newResponse.headers.set('Pragma','no-cache')
        newResponse.headers.append('Expires','-1')
        newResponse.headers.set('Expires','-1')
        return newResponse;
      } catch(err) {
        return new Response(err.stack, { status: 500 })
      }
    }
  }