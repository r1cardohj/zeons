from string import Template
import os

default_dir = 'templates'

_jinja_env = None

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