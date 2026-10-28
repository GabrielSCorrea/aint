from flask import Flask

from settings import session
from urls import registerUrls

app = Flask(__name__)
registerUrls(app)


@app.teardown_appcontext
def removeSession(exception=None):
    session.remove()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
