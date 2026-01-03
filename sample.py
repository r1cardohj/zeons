from zeons import Zeons, abort

app = Zeons()


@app.get("/")
@app.template("index.html")
def index(req):
    return {"name": "r1cardohj"}


@app.get("/method")
def get_method(req):
    return req.method


@app.post("/post")
def test_post(req):
    return [{"name": "zzj", "age": 12}, {"name": "zzy", "age": 13}]


@app.get("/test/error")
def test_abort(req):
    abort(404, "not found")
    return {"mes": "nothing"}


@app.route("/hello", methods=["post"])
def test_form(req):
    # print(req.form)
    print(req.json["age"])
    return req.json


if __name__ == "__main__":
    app.run()
