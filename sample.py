from zeons import Zeons

app = Zeons()


@app.get('/')
@app.template('index.html')
def index(req):
    return {'name':'hello'}

@app.get('/method')
def get_method(req):
    return req.method

if __name__ == '__main__':
    app.run()