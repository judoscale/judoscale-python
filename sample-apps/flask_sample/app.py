from flask import Flask, request
from middleware import RequestQueueTimeMiddleware


app = Flask('DemoApp')

# calling our middleware
app.wsgi_app = RequestQueueTimeMiddleware(app.wsgi_app)


@app.route('/', methods=['GET'])
def index():
#    user = request.environ['user']
#    return "Hi %s" % user['name']
	return f"Welcome to Judoscale {request.environ}"


if __name__ == "__main__":
    app.run('127.0.0.1', '5000', debug=True)
