# Zeons

a flask like wsgi app framework.

now it have:

* a fast router
* a easy request obj
* a simple template

it will have other feature in future like:

* orm base sqlite(todo)
* a stronger template enginee.(todo)
* ...

**Quick Start**

``` python
from zeons import Zeons,simple_render

app = Zeons()

@app.get('/')
def index(req):
    return simple_render('index.html',name='whoami',age=18)

if __name__ == '__main__':
    app.run()
```
