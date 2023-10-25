from string import Template
from collections import namedtuple
import os
import re
import itertools


default_dir = 'templates'

_jinja_env = None


###### useful func ########

def simple_render(file_name,**kwargs):
    with open(os.path.join(default_dir,file_name),'r',encoding='utf-8') as file:
        string = file.read()
        s = Template(string)
        return s.safe_substitute(**kwargs)


def jinja_render(file_name,**kwargs):
    global _jinja_env
    if not _jinja_env:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        _jinja_env = Environment(
            loader=FileSystemLoader(default_dir),
            autoescape=select_autoescape()
        )
    template = _jinja_env.get_template(file_name)
    return template.render(**kwargs)


##### Exception #######
class TemplateException(Exception):
    """render template error
    """
    def __init__(self, message, position, name=None):
        self.message = message
        self.position = position
        self.name = name
    
    
    def __str__(self):
        err_msg = f'{self.message} at string {self.position[0]} to {self.position[1]}'
        if self.name:
            err_msg += f'in {self.name}'
        return err_msg


##### TemplateZ ######
class TemplateZ:
    """TemplateZ is mini template prepare for Zeons

    e.g.::

        ``` <h1>hello $name</h1>

            <ul>
            ${for p in projects}
                <li>$p.title</li>
            ${endfor}
            </ul>

            ${if i_am_rich}
                <p>hhahaha....</p>
            ${endif}
        ```
    """
    SYMBOL='$'

    PATTERN_VAR = r'\$(?a:[_A-Za-z][_A-Za-z0-9]*)'

    PATTERN_EXP = r'\$\{([^}]+)\}'

    Exp_struct = namedtuple('Exp_struct',['begin','content','end'])

    def __init__(self,text: str, name:str|None = None,*kwargs) -> None:
        self.text = text
        self.config = kwargs
        self.name = name
        self.var = {}
        self.exp = []
        self.exp_structs = []

    def _find_var(self):
        """find all of var in template

        exm::
            
            >>> t = TemplateZ('<h1>hello $Name</h1>')
            >>> t._find_var()
            >>> t.var
            {'Name': (10, 15)}
            
        """
        var_iter =  re.finditer(self.PATTERN_VAR,self.text)
        for var in var_iter:
            self.var[var.group()[1:]] = var.span()


    def _find_exp(self):
        """find all of exp in template text
        
        exm::
        
            >>> t = TemplateZ('${for i in range(10)}')
            >>> t._find_exp()
            >>> t.exp
            [('for i in range(10)', (0, 21))]
        """
        exp_iter = re.finditer(self.PATTERN_EXP,self.text)
        for exp in exp_iter:
            exp_str,span = exp.group()[2:-1].strip(),exp.span()
            self.exp.append((exp_str,span))

    