from zeons import Zeons

app = Zeons()

@app.get('/')
def index(req):
    return 'hi zeons'

if __name__ == '__main__':
    app.run()