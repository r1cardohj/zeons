from zeons import Zeons
import urllib

app = Zeons()


@app.get('/')
@app.template('index.html')
def index(req):
    return {'name':'r1cardohj'}

@app.get('/method')
def get_method(req):
    return req.method

@app.post('/post')
def test_post(req):
    return {'mes':12}


if __name__ == '__main__':
    app.run()