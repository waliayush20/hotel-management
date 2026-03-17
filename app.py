from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from model import db

app = Flask(__name__)#creating flask app 

# ================= CONFIG =================
#We use app.config to store application settings like database URI,
#  security key, and SQLAlchemy options so that Flask extensions can use them. 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotel.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "123456"

# ================= DB INIT =================
db.init_app(app)

with app.app_context():
    db.create_all()


# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("home.html")


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)