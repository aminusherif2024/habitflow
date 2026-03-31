from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta, datetime

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.secret_key = "supersecretkey"
today = date.today()

@app.route('/register', methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (email, password) VALUES (?,?)",
                (email, hashed_password)
            )
            conn.commit()
        except:
            conn.close()
            return "User already exists"

        conn.close()
        return redirect("/login")

    return render_template('register.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print("POST request received")
        print(email, password)

        conn = get_db_connection()

        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect("/")

        return "Invalid Credentials"

    return render_template("login.html")

@app.route('/')
def index():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    if not user:
        conn.close()
        session.clear()
        return redirect("/login")

    habits = conn.execute("SELECT * FROM habits WHERE user_id = ? ORDER BY id DESC", (session["user_id"],)).fetchall()


    total = conn.execute("SELECT COUNT(*) AS count_total FROM habits WHERE user_id = ?", (session["user_id"],)).fetchone()["count_total"]

    completed = conn.execute("SELECT COUNT(*) AS count_completed FROM habits where user_id = ? AND done = 1", (session["user_id"],)).fetchone()["count_completed"]

    completed_dates = conn.execute("SELECT date FROM habits WHERE user_id = ? AND done = 1 ORDER BY date DESC", (session["user_id"],)).fetchall()

    completed_dates_list = [row["date"] for row in completed_dates]

    completed_dates_set = set(datetime.strptime(row, "%Y-%m-%d").date() for row in completed_dates_list if row is not None)

    streak = 0

    for i in range(len(completed_dates_set)):
        expected_date = today - timedelta(days = i)

        if expected_date in completed_dates_set:
            streak+=1
        else:
            break

    conn.close()

    if total > 0:
        percent = completed/total*100
    else:
        percent = 0

    return render_template("index.html", habits = habits, user = user, total = total, completed = completed, percent = percent, streak = streak)

@app.route('/add', methods = ["POST"])
def add():

    if "user_id" not in session:
        return redirect("/login")
    name = request.form.get("habit").lower()
    conn = get_db_connection()
    conn.execute("INSERT INTO HABITS (name, user_id, date) VALUES (?,?,?)", (name,session["user_id"],today))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route("/logout", methods = ["POST"])
def logout():
    session.pop("user_id", None)
    return redirect("/login")

@app.route('/done', methods = ["POST"])
def done():
    if "user_id" not in session:
        return redirect("/login")
    index = int(request.form.get("index"))

    conn = get_db_connection()
    conn.execute("UPDATE habits SET done=1, date = ? WHERE id = ?", (today,index))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete", methods = ["POST"])
def delete():
    if "user_id" not in session:
        return redirect("/login")

    habit_id = request.form.get("index")

    conn = get_db_connection()
    conn.execute("DELETE FROM habits WHERE id=? AND user_id=?", (habit_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)