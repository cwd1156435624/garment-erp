#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import sys
import ssl

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
        
    def do_GET(self):
        self.proxy_request('GET')
        
    def do_POST(self):
        self.proxy_request('POST')
        
    def do_PUT(self):
        self.proxy_request('PUT')
        
    def do_DELETE(self):
        self.proxy_request('DELETE')
        
    def proxy_request(self, method):
        target_url = f"https://yagtpotihswf.sealosbja.site{self.path}"
        print(f"转发请求到: {target_url}")
        
        # 获取请求头
        headers = {}
        for header in self.headers:
            if header.lower() not in ['host', 'connection']:
                headers[header] = self.headers[header]
        
        try:
            # 创建请求
            req = urllib.request.Request(target_url, method=method, headers=headers)
            
            # 如果是POST/PUT请求，读取请求体
            if method in ['POST', 'PUT']:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length) if content_length > 0 else None
                if body:
                    req.data = body
            
            # 发送请求
            context = ssl._create_unverified_context()
            response = urllib.request.urlopen(req, context=context)
            
            # 发送响应
            self.send_response(response.status)
            
            # 添加CORS头部
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
            self.send_header('Access-Control-Allow-Credentials', 'true')
            
            # 添加原始响应头
            for header in response.headers:
                if header.lower() not in ['transfer-encoding', 'connection', 'content-length', 'access-control-allow-origin']:
                    self.send_header(header, response.headers[header])
            
            # 读取响应体
            response_body = response.read()
            self.send_header('Content-Length', len(response_body))
            self.end_headers()
            
            # 发送响应体
            self.wfile.write(response_body)
            
        except urllib.error.HTTPError as e:
            print(f"HTTP错误: {e.code} - {e.reason}")
            self.send_response(e.code)
            
            # 添加CORS头部
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
            self.send_header('Access-Control-Allow-Credentials', 'true')
            
            # 添加原始响应头
            for header in e.headers:
                if header.lower() not in ['transfer-encoding', 'connection', 'content-length', 'access-control-allow-origin']:
                    self.send_header(header, e.headers[header])
            
            # 读取错误响应体
            error_body = e.read()
            self.send_header('Content-Length', len(error_body))
            self.end_headers()
            
            # 发送错误响应体
            self.wfile.write(error_body)
            
        except Exception as e:
            print(f"错误: {str(e)}")
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"代理服务器错误: {str(e)}".encode('utf-8'))

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    print(f'启动代理服务器在端口 {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
