from string import Template
from collections import namedtuple
import os
import re
import itertools


default_dir = "templates"

_jinja_env = None


###### useful func ########


def simple_render(file_name, **kwargs):
    with open(os.path.join(default_dir, file_name), "r", encoding="utf-8") as file:
        string = file.read()
        s = Template(string)
        return s.safe_substitute(**kwargs)


def jinja_render(file_name, **kwargs):
    global _jinja_env
    if not _jinja_env:
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        _jinja_env = Environment(
            loader=FileSystemLoader(default_dir), autoescape=select_autoescape()
        )
    template = _jinja_env.get_template(file_name)
    return template.render(**kwargs)


##### Exception #######
class TemplateException(Exception):
    """render template error"""

    def __init__(self, message, position, name=None):
        self.message = message
        self.position = position
        self.name = name

    def __str__(self):
        err_msg = f"{self.message} at string {self.position[0]} to {self.position[1]}"
        if self.name:
            err_msg += f"in {self.name}"
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

    SYMBOL = "$"

    PATTERN = r"(?s)(\${.*?}|\$[_A-Za-z][_A-Za-z0-9]*)"

    def __init__(self, text, *ctx) -> None:
        self.ctx = {}
        for c in ctx:
            self.ctx.update(ctx)
        self.all_vars = set()
        self.loop_vars = set()
        code, vars_code = self.make_render_func()
        buffered = []

        def flush_outpush():
            """buffered to the python code build"""
            if len(buffered) == 1:
                code.add_a_line(f"append_result({buffered[0]})")
            elif len(buffered) > 1:
                code.add_a_line(f"extend_result([{','.join(buffered)}])")
            del buffered[:]

    def make_render_func(self):
        code = CodeBuiler()
        code.add_line("def render_function(context, do_dots):")
        code.indent()
        vars_code = code.add_section()
        code.add_line("result = []")
        code.add_line("append_result = result.append")
        code.add_line("extend_result = result.extend")
        code.add_line("to_str = str")
        return code, vars_code


class CodeBuiler:
    """for build source python code"""

    INDENT_STEP = 4  # indent of python

    def __init__(self, indent=0) -> None:
        self.code = []
        self.indent_level = indent

    def add_a_line(self, line):
        """just add a line"""
        self.code.extend([" " * self.indent_level, line, "\n"])

    def indent(self):
        """begin a indent"""
        self.indent_level += self.INDENT_STEP

    def indent_back(self):
        """end a indent"""
        self.indent_level -= self.INDENT_STEP

    def add_section(self):
        """add a section, a sub Builder"""
        section = CodeBuiler(self.indent_level)
        self.code.append(section)
        return section

    def __str__(self):
        return "".join(str(c) for c in self.code)

    def get_global(self):
        assert self.indent_level == 0

        source_code = str(self)
        global_ns = {}
        exec(source_code, global_ns)
        return global_ns
