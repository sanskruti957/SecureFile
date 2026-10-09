import os
import io
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
    session
)
from werkzeug.utils import secure_filename
from cryptography.fernet import InvalidToken

from encryption import encrypt_file, decrypt_file
from auth import create_user, verify_user, init_db


app = Flask(__name__)

# Secret key for sessions
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "dev-only-change-this-before-deployment"
)

# Maximum file size: 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Initialize database
init_db()


# File size error
@app.errorhandler(413)
def file_too_large(error):
    return "File too large! Maximum size is 10 MB.", 413


# Login protection
def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped_view


# HOME PAGE
# Login opens first when the user is not logged in
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("index.html")


# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            message = "Please fill in all fields."

        elif len(username) < 3 or len(username) > 30:
            message = "Username must be 3 to 30 characters long."

        elif len(password) < 8:
            message = "Password must contain at least 8 characters."

        elif password != confirm_password:
            message = "Passwords do not match."

        elif create_user(username, password):
            return redirect(url_for("login", registered="1"))

        else:
            message = "Username already exists. Please choose another."

    return render_template("register.html", message=message)


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = verify_user(username, password)

        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("home"))

        message = "Incorrect username or password."

    registered = request.args.get("registered") == "1"

    return render_template(
        "login.html",
        message=message,
        registered=registered
    )


# LOGOUT
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ENCRYPT FILE
@app.route("/encrypt", methods=["GET", "POST"])
@login_required
def encrypt():
    message = ""

    if request.method == "POST":
        file = request.files.get("file")
        password = request.form.get("password", "")

        if not file or not file.filename:
            message = "Please select a file."

        elif not password:
            message = "Please enter a password."

        else:
            filename = secure_filename(file.filename)

            if not filename:
                message = "Invalid filename."

            else:
                file_data = file.read()

                if not file_data:
                    message = "The selected file is empty."

                else:
                    encrypted_data = encrypt_file(
                        file_data,
                        password
                    )

                    return send_file(
                        io.BytesIO(encrypted_data),
                        as_attachment=True,
                        download_name=filename + ".encrypted"
                    )

    return render_template("encrypt.html", message=message)


# DECRYPT FILE
@app.route("/decrypt", methods=["GET", "POST"])
@login_required
def decrypt():
    message = ""

    if request.method == "POST":
        file = request.files.get("file")
        password = request.form.get("password", "")

        if not file or not file.filename:
            message = "Please select a file."

        elif not password:
            message = "Please enter a password."

        else:
            filename = secure_filename(file.filename)

            if not filename:
                message = "Invalid filename."

            else:
                try:
                    encrypted_data = file.read()

                    if not encrypted_data:
                        message = "The selected file is empty."

                    else:
                        decrypted_data = decrypt_file(
                            encrypted_data,
                            password
                        )

                        if filename.endswith(".encrypted"):
                            download_name = filename[:-10]
                        else:
                            download_name = filename + ".decrypted"

                        return send_file(
                            io.BytesIO(decrypted_data),
                            as_attachment=True,
                            download_name=download_name
                        )

                except InvalidToken:
                    message = (
                        "Incorrect password or invalid encrypted file."
                    )

    return render_template("decrypt.html", message=message)


# RUN APPLICATION
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
