from flask import abort, flash, make_response, redirect, render_template, request, session, Flask
from database import Database
import secrets
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "18fd24bf6a2ad4dac04a33963db1c42f"

database = Database()

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

@app.route("/logout")
def logout():

    del session["user_id"]
    del session["csrf_token"]

    return redirect("/")

@app.route("/image/<string:image_id>")
def show_image(image_id):
    image = database.get_image(image_id)[0][0]
    if not image:
        return 404
    
    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "GET":

        if "user_id" not in session:
            return redirect("/login")
        
        if len(database.get_username(session["user_id"])) == 0:
            del session["user_id"]
            return redirect("/login")

        return render_template("create.html")
    
    check_csrf()
    
    title = request.form["title"]
    category = request.form["category"]
    price = request.form["price"]
    short_description = request.form["short_description"]
    long_description = request.form["long_description"]
    event_date = request.form["event_date"].replace("T", " ")

    try:
        if float(price) < 0.0:
            flash("Hinnan täytyy olla positiivinen")
            return redirect("/create")

    except ValueError:
        flash("Hinnan täytyy olla numero")
        return redirect("/create")
    
    image_id = None

    file = request.files["image"]
    file_data = file.read()
    if len(file_data) > 0:
        if len(file_data) > 10_000 * 1024:
            flash("Kuva on liian iso. (10 MB Max)")
            return redirect("/create")
        image_id = database.add_image(file_data)        

    database.add_event(session["user_id"], title, short_description, long_description, price, get_category_id(category), image_id, event_date)

    return redirect("/")

@app.route("/")
def index():

    db_events = database.get_all_events()
    
    events = []

    for db_event in db_events:
        event = {}
        event["title"] = db_event[0]
        event["short_description"] = db_event[1]
        event["price"] = db_event[2]
        event["event_date"] = db_event[5]

        if db_event[3] is not None:
            event["image_url"] = "/image/" + db_event[3]

        event["event_url"] = "/event/" + db_event[4]

        events.append(event)
    
    logged_in = False

    if "user_id" in session:
        if len(database.get_username(session["user_id"])) > 0:
            logged_in = True
        
    
    return render_template("index.html", events=events, logged_in=logged_in, is_search=False)

@app.route("/search")
def search():
    if "search" not in request.args:
        return "Bad request", 400
    
    query = request.args["search"]
    db_events = database.search_events(query)
    
    events = []

    for db_event in db_events:
        event = {}

        event["title"] = db_event[0]
        event["short_description"] = db_event[1]
        event["price"] = db_event[2]
        event["event_date"] = db_event[5]

        if db_event[3] is not None:
            event["image_url"] = "/image/" + db_event[3]

        event["event_url"] = "/event/" + db_event[4]
        events.append(event)
    
    logged_in = False

    if "user_id" in session:
        if len(database.get_username(session["user_id"])) > 0:
            logged_in = True
        
    return render_template("index.html", events=events, logged_in=logged_in, query=query, is_search=True, num_results=len(events))

@app.route("/event/<string:event_id>")
def event(event_id):
    db_event = database.get_event(event_id)

    if len(db_event) == 0:
        return "Not found", 404
    
    db_event = db_event[0]

    event = {}

    event["title"] = db_event[1]
    event["price"] = db_event[3]
    event["full_description"] = db_event[2]
    event["category"] = get_category_from_id(db_event[4])
    event["creator"] = database.get_username(db_event[0])[0][0]
    event["date"] = db_event[6]


    if db_event[5] is not None:
        event["image_url"] = "/image/" + db_event[5]

    is_creator = False

    if "user_id" in session:
        if db_event[0] == session["user_id"]:
            event["delete_url"] = "/delete/" + event_id
            event["edit_url"] = "/edit/" + event_id
            is_creator = True

    return render_template("event.html", event=event, is_creator=is_creator)

@app.route("/delete/<string:event_id>", methods=["POST"])
def delete(event_id):

    check_csrf()

    event = database.get_event(event_id)[0]

    if len(event) == 0:
        return "Not found", 404

    if "user_id" in session:
        if event[0] == session["user_id"]:
            database.delete_event(event_id)
            return redirect("/")
    
    return "Forbidden", 403

@app.route("/edit/<string:event_id>", methods=["GET", "POST"])
def edit(event_id):

    if "user_id" not in session:
        return "Forbidden", 403
    
    db_event = database.get_event(event_id)

    if len(db_event) == 0:
        return "Not found", 404
    
    db_event = db_event[0]

    if db_event[0] != session["user_id"]:
        return "Forbidden", 403

    if request.method == "GET":
        
        event = {}

        event["title"] = db_event[1]
        event["id"] = event_id
        event["short_description"] = db_event[7]
        event["full_description"] = db_event[2]
        event["price"] = db_event[3]

        return render_template("edit.html", event=event)
    
    check_csrf()

    new_title = request.form["title"]
    new_short_description = request.form["short_description"]
    new_full_description = request.form["short_description"]
    new_event_date = request.form["event_date"].replace("T", " ")
    new_price = request.form["price"]
    new_category = get_category_id(request.form["category"])

    try:
        if float(new_price) < 0.0:
            flash("Hinnan täytyy olla positiivinen")
            return redirect("/edit/" + event_id)

    except ValueError:
        flash("Hinnan täytyy olla numero")
        return redirect("/edit/" + event_id)

    new_image_id = None
    file = request.files["image"]
    file_data = file.read()
    if len(file_data) > 0:
        if len(file_data) > 10_000 * 1024:
            flash("Kuva on liian iso. (10 MB Max)")
            return redirect("/edit")
        new_image_id = database.add_image(file_data)

    database.update_event(event_id, new_title, new_full_description, new_short_description, new_price, new_category, new_image_id, new_event_date)


    return redirect("/event/" + event_id)

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


