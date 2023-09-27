import typing as t

class Zeons:
    """Zeons is a flask like framework
        it will be A simple wsig app
        
        ex::
        
        
            app = Zeons()
            @app.get()
            def index():
                return 'zeons is running'
            app.run()    
    """
    def __init__(self,app_name=__name__):
        self.app_name = app_name
        self.url_map = {}
        self.error_handlers = {}
        self.server = None
        
    
    def route(self,url_path,methods=None):
        """append url_rule to url_map

        Args:
            url_path (path): a path for searching
            methods (str, optional): only 'GET','POST' can use, it should be a list or tuple
            
            btw default methods is 'GET'
        """
        def decorated(view_func):
            self.url_map[url_path] = ([method.upper() for method in (methods or ['GET'])],view_func)
            return view_func
        return decorated
    
    def get(self,url_path):
        """decorate like route()
            for http method 'GET'
        """
        return self.route(url_path,methods=['GET'])
    
    def post(self,url_path):
        """decorate like route
            for http method 'POST'
        """
        return self.route(url_path,methods=['POST'])
    
    def error_handle(self,status_code):
        """if Zeons raise a special error_code (400,404,..) func will

        Args:
            status_code (_type_): _description_
        """
        pass