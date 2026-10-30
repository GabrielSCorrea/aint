from flask import Flask

from settings import session
from urls import register_urls

app = Flask(__name__)
register_urls(app)


@app.teardown_appcontext
def remove_session(exception=None):
    session.remove()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
