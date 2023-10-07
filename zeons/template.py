from string import Template
import os

default_dir = 'templates'

def simple_render(file_name,**kwargs):
    with open(os.path.join(default_dir,file_name),'r',encoding='utf-8') as file:
        string = file.read()
        s = Template(string)
        return s.safe_substitute(**kwargs)