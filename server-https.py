# webブラウザで、https://IPアドレス:8000/send?q=こんにちは　にアクセス

# Windowsのコマンドプロンプトで set OPENAI_API_KEY=自分のAPIキーを実行しておく

###########################################################
## 以下、ChatGPTを使うための前処理         ################
###########################################################

from openai import OpenAI
import os


# OpenAI APIキーを設定。環境変数から取得します。
# 事前に `set OPENAI_API_KEY=sk-xxxx...` のように設定してください。
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI APIキーが設定されていません。環境変数 'OPENAI_API_KEY' を設定してください。")
client = OpenAI(api_key=api_key)

###########################################################
## 以下、Webサーバーとして動かすための処理 ################
###########################################################

from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import socket
import urllib
import re

class MyHandler(SimpleHTTPRequestHandler):

    def htmlheader(self): #httpヘッダーを出力
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.endswith('favicon.ico'):
            return

        p = urllib.parse.urlparse(self.path)
        #print(p) #consoleに表示
        
        if (p.path == "/send"):
            self.htmlheader()
            q=urllib.parse.parse_qs(p.query).get("q","")[0]
            print(q) #consoleに表示
            
            #answer="<b>"+q+"</b>"+"ですか？" 
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": q}]
            )
            answer = response.choices[0].message.content #webブラウザに返信するHTML文を作成する
            # HTMLタグを削除
            answer = re.sub(r'<[^>]+>', '', answer)
            print(answer) #consoleに表示
            
            self.wfile.write(answer.encode('utf-8'))#webブラウザに返信する

        else:#webページを表示
            print(p.path) #consoleに表示
            super().do_GET() #SimpleHTTPRequestHandlerクラスのdo_GETを呼ぶ



#openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes

host = socket.gethostbyname(socket.gethostname()) #'localhost'
port = 8000
httpd = HTTPServer((host, port), MyHandler)

#httpd.socket = ssl.wrap_socket (httpd.socket, certfile='server.pem', server_side=True)
context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='server.pem')
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print('Ready! Now you can access to https://%s:%s' % (host, port))
httpd.serve_forever()


