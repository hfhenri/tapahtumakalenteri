from flask import abort, flash, make_response, redirect, render_template, request, session, Flask
from database import Database
import secrets
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "18fd24bf6a2ad4dac04a33963db1c42f"

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form["username"]
    password = request.form["password"]

    if database.check_password(username, password):
        session["user_id"] = database.get_user_id(username)[0][0]
        session["csrf_token"] = secrets.token_hex(16)
    else:
        flash("Käyttäjänimi tai salasana väärin")
        return redirect("/login")

    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")
    
    username = request.form["username"]
    password = request.form["password"]
    confirm_password = request.form["confirm-password"]

    if len(username) > 50:
        flash("Käyttäjänimi ei voi olla yli 50 merkkiä")
        return redirect("/register")
    
    if password != confirm_password:
        flash("Salasanat eivät täsmää")
        return redirect("/register")

    if len(database.get_user_id(username)) > 0:
        flash("Käyttäjänimi on käytössä")
        return redirect("/register")

    hash = generate_password_hash(password)
    database.add_user(username, hash)
    session["user_id"] = database.get_user_id(username)[0][0]
    session["csrf_token"] = secrets.token_hex(16)

    return redirect("/")

@app.route("/image/<string:image_id>")
def show_image(image_id):
    image = database.get_image(image_id)[0][0]
    if not image:
        return 404
    
    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response


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


