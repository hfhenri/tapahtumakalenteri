from flask import abort, flash, make_response, redirect, render_template, request, session, Flask
from database import Database
import secrets
from werkzeug.security import generate_password_hash
from utils import get_category_from_id, get_category_id

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
            event["image_id"] = db_event[3]

        event["id"] = db_event[4]

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
    event["id"] = event_id
    event["creator"] = database.get_username(db_event[0])[0][0]
    event["category"] = get_category_from_id(db_event[4])
    event["date"] = db_event[6]
    event["registrants"] = database.get_event_registrations(event_id)

    if db_event[5] is not None:
        event["image_id"] = db_event[5]

    is_creator = False
    logged_in = False
    registered = False

    question = {}

    if "user_id" in session:
        if db_event[0] == session["user_id"]:
            is_creator = True

        if len(database.get_username(session["user_id"])[0]) > 0:
            logged_in = True

        if database.is_user_registered(event_id, session["user_id"]):
            registered = True

        db_question = database.get_user_question(event_id, session["user_id"])

        if len(db_question) > 0:

            question["text"] = db_question[0][1]

            db_reply = database.get_reply(db_question[0][0])

            if len(db_reply) > 0:
                question["reply"] = db_reply[0][0]

    return render_template("event.html", event=event, is_creator=is_creator, logged_in=logged_in, registered=registered, question=question)

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

@app.route("/register-event/<string:event_id>", methods=["POST"])
def register_event(event_id):

    check_csrf()

    event = database.get_event(event_id)[0]

    if len(event) == 0:
        return "Not found", 404
    
    if "user_id" in session:
        database.register_for_event(event_id, session["user_id"])
        return redirect(f"/event/{event_id}")

    return "Forbidden", 403

@app.route("/reply/<string:question_id>", methods=["GET", "POST"])
def reply(question_id):

    if "user_id" not in session:
        return "Forbidden", 403

    if request.method == "GET":

        db_question = database.get_question(question_id)
        db_event = database.get_event(db_question[0][3])

        if db_event[0][0] != session["user_id"]:
            return  "Forbidden", 403

        if len(db_question) == 0:
            return "Not Found", 404

        question = {}

        question["text"] = db_question[0][0]
        question["sender_name"] = db_question[0][1]
        question["event_title"] = db_question[0][2]
        question["id"] = question_id

        return render_template("reply.html", question=question)
    
    check_csrf()
    
    db_question = database.get_question(question_id)

    if len(db_question) == 0:
        return 404, "Not Found"
        
    db_event = database.get_event(db_question[0][3])

    if len(db_event) == 0:
        return "Not Found", 404, 
        
    if db_event[0][0] != session["user_id"]:
        return  "Forbidden", 403
        
    if "reply" not in request.form:
        return "Bad request", 400
        
    database.add_reply(question_id, request.form["reply"])

    return redirect("/me")

@app.route("/me")
def me():

    if "user_id" not in session:
        return "Forbidden", 403
    
    if len(database.get_username(session["user_id"])[0]) == 0:
        return "Bad request", 400
    
    db_events = database.get_user_events(session["user_id"])
    events = []
    questions = []

    for db_event in db_events:
        event = {}

        event["title"] = db_event[0]
        event["short_description"] = db_event[1]
        event["price"] = db_event[2]
        event["event_date"] = db_event[5]

        if db_event[3] is not None:
            event["image_id"] = db_event[3]

        event["id"] = db_event[4]
        events.append(event)

        db_event_questions = database.get_event_questions(db_event[4])


        for db_question in db_event_questions:
            question = {}

            question["question"] = db_question[1]
            question["sender_name"] = db_question[2]
            question["event_title"] = db_event[0]
            question["id"] = db_question[0]

            questions.append(question)
    
    return render_template("me.html", events=events, questions=questions)

@app.route("/question/<string:event_id>", methods=["POST"])
def question(event_id):
    check_csrf()

    if "user_id" not in session:
        return "Forbidden", 403
    
    if len(database.get_username(session["user_id"])[0]) == 0:
        return "Bad request", 400

    question_text = request.form["question"]

    database.add_question(event_id, session["user_id"], question_text)

    flash("Kysymys lähetetty.")
    return redirect(f"/event/{event_id}")


def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


