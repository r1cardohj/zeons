""" Author:r1cardohj 
    Lisence:MIT
    Date:20230928
"""
import typing as t
from typing import Any
from error import HttpException
from wsgiref.simple_server import make_server

class Zeons:
    """Zeons is a flask like framework,
        it will be a simple wsig app.
        
        ex::
        
        
            app = Zeons()
            @app.get()
            def index():
                return 'zeons is running'
            app.run()    
    """
    def __init__(self,name=__name__):
        self.app_name = name
        self.url_map = {}
        self.before_request_handlers = []
        self.after_request_handles = []
        
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
        
    
    
    def __call__(self,environ,start_response):
        return self.wsgi_app(environ,start_response)
    
    
    def _make_request(self,environ):
        """ parse envrion and make Request obj"""
        return Request.make_request_by_environ(self,environ)
    



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
            self.args = self._query_str_to_args(self.query_str) if self.query_str else {}
        
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
    
    
    def _query_str_to_args(query_str:str):
        """ parse url's query_str to a dict"""
        args = {}
        pres = [item for item in query_str.split('&')]
        for pre in pres:
            k,v = pre.split['=']
            args[k] = v
        
        return args
    
    
    @property
    def body(self):
        """ request's body,"""
    
    @property
    def json(self):
        """ simple way to get body's json"""
        
    
    @property
    def form(self):
        """simple way to get body's form"""
        
    
        
