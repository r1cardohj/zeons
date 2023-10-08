# Zeons

a flask like wsgi app framework.

now it have:

* a fast router.
* a easy request obj.
* a simple inner template and jinja2 support.

it will have other feature in future like:

* orm base sqlite(todo)
* a stronger template enginee.(todo)
* ...

**Quick Start**

``` python
from zeons import Zeons

app = Zeons()

@app.get('/')
def index(req):
    return '<h1>hello zeons</h1>'

if __name__ == '__main__':
    app.run()
```
