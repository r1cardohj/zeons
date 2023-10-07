""" Author:r1cardohj 
    Lisence:MIT
    Date:20230928
"""

from typing import Any
from .error import HttpException,ResponseTypeException,RouteNotFoundException
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
from enum import Enum 
import json

class Zeons:
    """Zeons is a flask like framework,
        it will be a simple wsig app.
        
        ex::
        
        
            app = Zeons()
            @app.get()
            def index():
                return '<h1>hello zeons</h1>'
    """
    def __init__(self,name='app'):
        self.app_name = name
        self.url_map = {}
        self.before_request_handlers = []
        self.after_request_handlers = []
        
        self.config = {}
        self.error_handlers = {}
        self.server = None
        
    
    def route(self,url_path,methods=None):
        """append url_rule to url_map

        Args:
            url_path (path): a path for searching
            methods (str, optional): only 'GET','POST' can use now,
            it should be a list or tuple
            
            btw default methods is 'GET'
        """
        def decorated(view_func):
            self.url_map[url_path] = ([method.upper() for method in (methods or ['GET'])],view_func)
            return view_func
        return decorated
    
    def get(self,url_path):
        """decorator like route()
            for http method 'GET'
        """
        return self.route(url_path,methods=['GET'])
    
    def post(self,url_path):
        """decorator like route
            for http method 'POST'
        """
        return self.route(url_path,methods=['POST'])
    
    def error_handle(self,status_code):
        """if Zeons raise a special error code like (400,404,..) func will call

        Args:
            status_code (_type_): http status error code
            
        Exm::
            
            @app.error_handle(404)
            def error_handler():
                return '<h1>404 Not Found</h1>'
        """
        def decorated(func):
            self.error_handlers[status_code] = func
        return decorated
    
    
    @staticmethod
    def abort(status_code,why=None):
        """ just raise a HttpException"""
        raise HttpException(status_code,why)
    
    
    def run(self,host='127.0.0.1',port=5001,debug=False):
        """ just run a simple server by wsgiref moudel"""
        server = make_server(host,port,self)
        print(f"Server started on http://{host}:{port}")
        server.serve_forever()
    
    
    def wsgi_app(self,environ, start_response):
        """a wsgi application callable"""
        request = self._make_request(environ)
        response = self.deal_request_and_get_response(request)
        response.finish_response_make()
        reason = response.err_why or ('OK' if response.status_code == 200 else 'N/A')
        headers_list = [(k,v) for k,v in response.headers.items()]
        start_response(str(response.status_code)+ ' ' + reason,headers_list)
        return response.gen_body()
        
    
    
    def __call__(self,environ,start_response):
        return self.wsgi_app(environ,start_response)
    
    
    def _make_request(self,environ):
        """ parse envrion and make Request obj"""
        return Request.make_request_by_environ(self,environ)
    
    
    def find_route_and_get_func(self,request):
        """find the view func if exist
            else return None
        """
        method = request.method.upper()
        methods = []
        if method in ('GET','POST'):
            try:
                if request.path == '/favicon.ico':
                    return None
                methods,func =  self.url_map[request.path] 
            except KeyError:
                pass
            if method in methods:
                    return func
            return None
            
    
    def deal_request_and_get_response(self,request):
        """handle a request and get response"""
        if request:
            f = self.find_route_and_get_func(request)
            if not f:
                resp =  'Not Found',404
            else:
                try:
                    callable(f)
                    response = f(request)
                    if isinstance(response,tuple) \
                        and len(response) == 2:
                        resp = Response(response[0],int(response[1])) # body and status code
                    elif isinstance(response,Response):
                        resp = response
                    else:
                        resp = Response(response)
                except HttpException as e:
                    if e.status_code in self.error_handlers:
                        resp = self.error_handlers[e.status_code]
                    else:
                        resp = e.why,e.status_code
                except Exception as e:
                    print(f'{e!r}')
                    resp = e.why,500    
        else:
            resp = 'Bad request',400
        
        if isinstance(resp, tuple):
            resp = Response(*resp)
        elif not isinstance(resp, Response):
            resp = Response(resp)
        
        return resp
                         



####### Request and Response ##########
class Z(dict):
    """like flask's g object
        it is a dict follow every single http request  
    """
    pass

class Request:
    """parse http request  and make it easy
    """
    def __init__(self,
                 app,
                 client_addr,
                 method,
                 path,
                 url,
                 http_version,
                 headers,
                 stream = None,
                 body = None
                 ) -> None:
        self.app = app
        self.client_addr = client_addr # (host,port)
        self.method = method
        self.path = path
        self.url:str = url
        self.headers = headers
        
        self._stream = stream
        self._body = body
        self._form = None
        self._json = None
        
        
        self.cookies = {}
        self.content_length = 0
        self.content_type = None
        self.http_version = http_version
        
        if '?' in self.url: 
            self.path,self.query_str = self.url.split('?')
            self.args = parse_qs(self.query_str) if self.query_str else {}
        
        if 'CONTENT-LENGTH' in self.headers:
            self.content_length = int(self.headers['CONTENT-LENGTH'])
        if 'CONTENT-TYPE' in self.headers:
            self.content_type = self.headers['CONTENT-TYPE']
        if 'COOKIE' in self.headers:
            for cookie in self.headers['COOKIE'].split(';'):
                key, value = cookie.strip().split('=', 1)
                self.cookies[key] = value
        self.z = Z()
    
    
    @staticmethod
    def make_request_by_environ(app,environ:dict):
        """ parse wsgi envrion obj and return a Request object"""
        
        method = environ.get('REQUEST_METHOD')
        path =  environ.get('PATH_INFO', '')
        full_uri = environ.get('SCRIPT_NAME', '') + environ.get('PATH_INFO', '')
        
        query_str = environ.get('QUERY_STRING','')
        if query_str:
            full_uri += '?' + query_str
        
        client_addr = environ.get('REMOTE_ADDR','')
        remote_port = int(environ.get('REMOTE_PORT','0'))
        http_version = environ.get('SERVER_PROTOCOL','')
        
        # http header
        headers = {}
        # http stream
        stream = environ.get('wsgi.input')
        
        # HTTP_* in environ is information in http header
        # like   HTTP_ACCEPT to ACCEPT
        #        HTTP_ACCEPT_ENCODING to ACCEPT-ENCODING         
        for key,value in environ.items():
            if key.startswith('HTTP_'):
                header_key_list = key.replace('_','-').split('-')
                header_key_str = '-'.join(header_key_list[1:])
                headers[header_key_str] = value
        
        req = Request(
            app=app,
            method=method,
            path=path,
            url=full_uri,
            client_addr =(client_addr,remote_port),
            headers=headers,
            http_version=http_version,
            stream=stream,
        )
        return req
    
    
    @property
    def body(self):
        """ request's body,"""
        if not self._body:
            self._body = b''
            if self.content_length:
                while len(self._body) < self.content_length:
                    data = self._stream.read(self.content_length - len(self._body))
                    self._body += data
        return self._body
    
    
    @property
    def json(self):
        """ simple way to get body's json"""
        if not self._json:
            if not self.content_type:
                return None
            mime_type = self.content_type.split(';')[0]
            if mime_type != 'application/json':
                return None
            self._json = json.loads(self.body.decode())
        return self._json
    
    
    @property
    def form(self):
        """simple way to get body's form"""
        if not self._form:
            if not self.content_type:
                return None
            mime_type = self.content_type.split(';')[0]
            if mime_type != 'application/x-www-form-urlencoded':
                return None
            self._form = parse_qs(self.body.decode())
        return self._form
    
    

        
        
    
        

class Response:
    """ Http Response"""
    
    max_one_time_buffer_size = 1024
    
    class ContentTypes(Enum):
        CSS = 'text/css'
        GIF = 'image/gif'
        HTML = 'text/html'
        JPG = 'image/jpge'
        JS = 'application/javascript'
        JSON = 'application/json'
        PNG = 'image/png'
        TXT = 'text/plain'
    
    default_content_type = ContentTypes.TXT.value
    
    def __init__(self,
                 body=None,
                 status_code=200,
                 headers=None,
                 err_why=None) -> None:
        self.status_code =status_code
        self.headers = headers
        self.err_why = err_why
        if not self.headers:
            self.headers = {}
        if isinstance(body,(dict,list)):
            self.body = json.dumps(body).encode()
            self.headers['Content-Type'] = 'application/json; charset=UTF-8'
        elif isinstance(body,str):
            self.body = body.encode()
            self.headers['Content-Type'] = self.ContentTypes.HTML.value +'; charset=UTF-8'
        elif isinstance(body,bytes):
            self.body = body
        else:
            raise ResponseTypeException('response type must be dict,list,str or bytes')
    
    
    def set_cookies(self): #TODO 
        pass
    
    
    def finish_response_make(self):
        self._fix_content_length()
        self._fix_content_type()
        
    
    
    def _fix_content_length(self):
        """fix Content-Length """
        if 'Content-Length' not in self.headers:
            self.headers['Content-Length'] =  str(len(self.body))
        
    
    def _fix_content_type(self):
        """fix Content-Type"""
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] =  self.default_content_type
            if 'charset=' not in self.headers['Content-Type']:
                self.headers['Content-Type'] += '; charset=UTF-8'
    
    def gen_body(self):
        if hasattr(self.body,'read'):
            while True:
                buf = self.body.read(self.max_one_time_buffer_size)
                if len(buf):
                    yield buf
                if len(buf) < self.max_one_time_buffer_size:
                    break
                if hasattr(self.body, 'close'):  
                    self.body.close()
        elif hasattr(self.body,'__next__'):
            yield from self.body
        else:
            yield self.body
    
    