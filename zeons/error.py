from abc import abstractmethod


class BaseHttpException(Exception):
    """sub class should rewrite __repr__() method"""

    def __init__(self, status_code, why=None):
        self.status_code = status_code
        self.why = why

    @abstractmethod
    def __repr__(self):
        pass


class HttpException(BaseHttpException):
    def __init__(self, *args) -> None:
        super().__init__(*args)

    def __repr__(self):
        return f"HttpException:{self.status_code}.{self.why} "


class RouteNotFoundException(HttpException):
    pass


# Type Error
class TypeException(Exception):
    pass


class ResponseTypeException(TypeException):
    pass
