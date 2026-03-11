from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from model import db

app = Flask(__name__)

# ================= CONFIG =================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotel.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "123456"

# ================= DB INIT =================
db = SQLAlchemy(app)


# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("home.html")


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)