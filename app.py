from flask import Flask, render_template, request, send_file
from encryption import encrypt_file, decrypt_file
import io

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/encrypt", methods=["GET", "POST"])
def encrypt():
    if request.method == "POST":
        file = request.files["file"]
        password = request.form["password"]

        if file and password:
            file_data = file.read()
            encrypted_data = encrypt_file(file_data, password)

            return send_file(
                io.BytesIO(encrypted_data),
                as_attachment=True,
                download_name=file.filename + ".encrypted"
            )

    return render_template("encrypt.html")


@app.route("/decrypt", methods=["GET", "POST"])
def decrypt():
    message = ""

    if request.method == "POST":
        file = request.files["file"]
        password = request.form["password"]

        try:
            if file and password:
                encrypted_data = file.read()
                decrypted_data = decrypt_file(encrypted_data, password)

                filename = file.filename.replace(".encrypted", "")

                return send_file(
                    io.BytesIO(decrypted_data),
                    as_attachment=True,
                    download_name=filename
                )

        except Exception:
            message = "Incorrect password or invalid encrypted file."

    return render_template("decrypt.html", message=message)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)