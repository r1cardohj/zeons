from abc import abstractmethod

class BaseHttpException(Exception):
    """sub class should rewrite __repr__() method"""
    def __init__(self,status_code,why=None):
        self.status_code = status_code
        self.why = why
    
    @abstractmethod
    def __repr__(self):
        pass
    
    
class HttpException(BaseException):
    
    def __repr__(self):
        return f'HttpException:{self.status_code}.{self.why} '