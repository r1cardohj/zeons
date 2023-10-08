from zeons import Zeons,simple_render,jinja_render

app = Zeons()

@app.get('/')
def index(req):
    return jinja_render('index.html',name='bb')

@app.get('/method')
def get_method(req):
    return req.method

if __name__ == '__main__':
    app.run()