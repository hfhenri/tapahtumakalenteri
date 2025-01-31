from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"


def get_category_id(category):
    if category == "Konsertti":
        return 0
    elif category == "Teatteri":
        return 1
    elif category == "Urheilu":
        return 2
    elif category == "Muu":
        return 3
    return 3

def get_category_from_id(id):
    if id == 0:
        return "Konsertti"
    elif id == 1:
        return "Teatteri"
    elif id == 2:
        return "Urheilu"
    elif id == "3":
        return "Muu"
    return "Muu"

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
