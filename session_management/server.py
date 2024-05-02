'''
1. Create server
2. manage cookies
3. simple session management
'''

from http.server import BaseHTTPRequestHandler, HTTPServer
import http.cookies
import uuid

# Simple session storage
sessions = {}

class HttpRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.handle_index()
        elif self.path == '/set-cookie':
            self.handle_set_cookie()
        elif self.path == '/get-cookie':
            self.handle_get_cookie()
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)
    
    def handle_index(self):
        cookie = self.get_cookie('session_id')
        session_id = cookie if cookie else str(uuid.uuid4())

        if session_id not in sessions:
            sessions[session_id] = {'visits': 1}
            message = f"Hello, new visitor! A session has been creted for for you! ID:{session_id}"
        else:
            sessions[session_id]['visits'] += 1
            message = f"Hello again! You have visited {sessions[session_id]['visits']} times."

        self.send_response(200)
        self.send_header('Content-type', 'text/html')

        if not cookie:
            self.set_cookie('session_id', session_id)
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

    
    def handle_set_cookie(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        key, val = 'test_cookie_emmaka', 'test_value_emmaka'
        self.set_cookie(key, val)
        # signals end of http headers section of the response.
        # any further data sent after this line, to the client is considered part of the response body.
        self.end_headers()
        m = f"Cookie {key} set to {val}".encode('utf-8')
        self.wfile.write(m)

    def handle_get_cookie(self):
        cookie_value1 = self.get_cookie('test_cookie_emmaka') or 'No Cookie found!'
        #cookie_value2 = self.get_cookie('sess')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Cookie value: {cookie_value1}".encode('utf-8'))


    def set_cookie(self, key, value):
        cookie = http.cookies.SimpleCookie()
        cookie[key] = value
        # set the path attribute of the cookie to the root directory
        # this means the cookie will be included in every request to server regardless of the path
        # It's a way to make the cookie available across the entire domain
        cookie[key]['path'] = '/'
        # sends cookie to the client within http headers.
        # Set-Cookie header is used to deliver cookies from the server to the browser
        # cookie.output - formats the cookie as a string suitable for sending in a header
        # header = '' - ensures no additional header name is  prefixed before the cookie str
        # sep=; - ensures if there are multiple cookies or attributes, they are separated by a semicolon
        # which standard for http headers
        self.send_header('Set-Cookie', cookie.output(header='', sep=';'))

    

    def get_cookie(self, key):
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = http.cookies.SimpleCookie(cookie_header)
            return cookie.get(key).value if key in cookie else None
        
    

def run(server_class=HTTPServer, handler_class=HttpRequestHandler, port=8000):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print(f"Starting httpd server on {port}")
        httpd.serve_forever()

if __name__=='__main__':
    run()