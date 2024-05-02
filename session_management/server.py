'''
1. Create server
2. manage cookies
3. simple session management
'''

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import http.cookies
import uuid
import os
import re

# session storage
sessions = {}

class HttpRequestHandler(BaseHTTPRequestHandler):

    def load_html(self, fileName):
        # print('current directory path:', os.getcwd())
        
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # file_path = os.path.join(current_dir, fileName)
        # print('emmaka', file_path)
        with open(fileName, 'r') as file:
            return file.read()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        # Route the request based on the path
        if path == '/':
            self.handle_index()
        elif path == '/set-cookie':
            self.handle_set_cookie(query_params)
        elif path == '/get-cookie':
            self.handle_get_cookie()
        else:
            self.send_error(404, 'File Not Found: %s' % path)
    
    def handle_index(self):
        content = self.load_html("/home/emmaka/workplace_emmaka/misc_small_projects/session_management/templates/index.html")
        cookie = self.get_cookie('session_id')
        session_id = cookie if cookie else str(uuid.uuid4())

        if session_id not in sessions:
            sessions[session_id] = {'visits': 1}
            session_message = f"Hello, new visitor! A session has been creted for for you! ID:{session_id}"
        else:
            sessions[session_id]['visits'] += 1
            session_message = f"Hello again! You have visited {sessions[session_id]['visits']} times."
        
        content = content.replace("{{sessionMessage}}", session_message)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')

        if not cookie:
            self.set_cookie('session_id', session_id)
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    
    def handle_set_cookie(self, params):

        key = params.get('key', [None])[0] # Extract the first value
        val = params.get('value', [None])[0]

        if key and val:
            key = self.sanitize_cookie_value(key)
            val = self.sanitize_cookie_value(val)

            if not key: # check if key is empty after sanitization
                self.send_response(400, 'BAD REQUEST')
                self.end_headers()
                self.wfile.write(b"Invalid cookie key provided!")
                return

            self.send_response(303, "See Other!")
            self.send_header('Location', '/')
            self.set_cookie(key, val)
            # signals end of http headers section of the response.
            # any further data sent after this line, to the client is considered part of the response body.
            self.end_headers()
            m = f"Cookie {key} set to {val}".encode('utf-8')
            self.wfile.write(m)
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing key or value parameters.")

    def handle_get_cookie(self):
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        cookie_message = '''
        <html>
            <body>
                Stored Cookies:
            </body>
        </html>
        '''
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = http.cookies.SimpleCookie(cookie_header)
            for key, morsel in cookie.items():
                cookie_message += f'''<p>
                    {key}: {morsel.value}
                </p>'''
        else:
            cookie_message += "<p> No cookies found. </p>"
        cookie_message += '<br> <a href="/">Back</a></html> '
        
        self.wfile.write(cookie_message.encode('utf-8'))

   


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
            return cookie.get(key).value if key in cookie else 'Cookie Not Found!'


    def sanitize_cookie_value(self, value):
        return re.sub(r'[^\w!#$%&\'*+-.^_`|~]', '', value)
    

def run(server_class=HTTPServer, handler_class=HttpRequestHandler, port=8000):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print(f"Starting httpd server on {port}")
        httpd.serve_forever()

if __name__=='__main__':
    run()