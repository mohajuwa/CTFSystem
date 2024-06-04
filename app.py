from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import secrets

app = Flask(__name__)
secret_key = secrets.token_hex(32)
app.secret_key = secret_key
print(secret_key)


def get_db_connection():
    conn = sqlite3.connect("/var/www/html/CTFSystem/data/ctf.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/challenges")
def challenges():
    conn = get_db_connection()
    challenges = conn.execute("SELECT * FROM challenges").fetchall()
    conn.close()
    return render_template("challenges.html", challenges=challenges)


@app.route("/scoreboard")
def scoreboard():
    conn = get_db_connection()
    users = conn.execute(
        "SELECT username, points FROM users ORDER BY points DESC"
    ).fetchall()
    conn.close()
    return render_template("scoreboard.html", users=users)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/submit_challenge", methods=["POST"])
def submit_challenge():
    challenge_id = request.form["challenge_id"]
    solution = request.form["solution"]
    conn = get_db_connection()
    challenge = conn.execute(
        "SELECT * FROM challenges WHERE id = ?", (challenge_id,)
    ).fetchone()
    if challenge["solution"] == solution:
        conn.execute(
            "UPDATE users SET points = points + ? WHERE id = ?",
            (challenge["points"], session["user_id"]),
        )
        conn.commit()
    conn.close()
    return redirect(url_for("challenges"))


# Dummy admin credentials (replace these with your actual admin credentials)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin_password"


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin/dashboard")
        else:
            return render_template(
                "admin/admin_login.html", error="Invalid credentials"
            )

    return render_template("admin/admin_login.html", error=None)


@app.route("/admin/dashboard")
def admin_dashboard():
    conn = get_db_connection()
    users = conn.execute(
        "SELECT username, points FROM users ORDER BY points DESC"
    ).fetchall()
    challenges = conn.execute(
        "SELECT title, solution,points FROM challenges ORDER BY points DESC"
    ).fetchall()
    conn.close()
    return render_template(
        "admin/admin_dashboard.html", users=users, challenges=challenges
    )


@app.route("/admin/add_challenge", methods=["GET", "POST"])
def add_challenge():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        solution = request.form["solution"]
        type_ = request.form["type"]
        points = request.form["points"]
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO challenges (title, description, solution, type, points) VALUES (?, ?, ?, ?, ?)",
            (title, description, solution, type_, points),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/add_challenge.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
