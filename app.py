from flask import Flask, render_template, request, redirect, url_for, session
from model import db, User, Booking, Room, Payment, Feedback, Complaint
from werkzeug.security import check_password_hash

app = Flask(__name__)

# ================= CONFIG =================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./hotel.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "123456"

# ================= DB INIT =================
db.init_app(app)

with app.app_context():
    db.create_all()
    User.makeAdmin()

# ================= AUTH DECORATOR =================
def login_required(role=None):
    def wrapper(func):
        def inner(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))

            if role and session.get("user_role") != role:
                return "❌ Unauthorized Access"

            return func(*args, **kwargs)
        inner.__name__ = func.__name__
        return inner
    return wrapper


# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["user_role"] = user.role
            session["user_name"] = user.name

            # Redirect based on role
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "manager":
                return redirect(url_for("manager_dashboard"))
            else:
                return redirect(url_for("customer_dashboard"))

        return "❌ Invalid Credentials"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =====================================================
# ================= CUSTOMER ROUTES ===================
# =====================================================

@app.route("/customer")
def customer_dashboard():
    return render_template("customer/dashboard.html")


@app.route("/customer/rooms")
def customer_rooms():
    rooms = Room.query.all()
    return render_template("customer/rooms.html", rooms=rooms)


@app.route("/customer/book/<int:id>", methods=["GET", "POST"])
def customer_book(id):

    if request.method == "POST":

        days = request.form["days"]

        booking = Booking(
            room_id=id,
            days=days,
            status="pending"
        )

        db.session.add(booking)
        db.session.commit()

        return redirect(url_for("customer_payment"))

    return render_template("customer/booking.html", room_id=id)


@app.route("/customer/payment", methods=["GET", "POST"])
def customer_payment():

    if request.method == "POST":

        amount = request.form["amount"]
        mode = request.form["mode"]

        pay = Payment(
            amount=amount,
            mode=mode,
            status="waiting"
        )

        db.session.add(pay)
        db.session.commit()

        return redirect(url_for("customer_dashboard"))

    return render_template("customer/payment.html")


@app.route("/customer/feedback", methods=["GET", "POST"])
def customer_feedback():

    if request.method == "POST":

        msg = request.form["message"]

        f = Feedback(message=msg)

        db.session.add(f)
        db.session.commit()

        return redirect(url_for("customer_dashboard"))

    return render_template("customer/feedback.html")


# =====================================================
# ================= MANAGER ROUTES ====================
# =====================================================

@app.route("/manager")
def manager_dashboard():
    return render_template("manager/dashboard.html")


@app.route("/manager/rooms")
def manager_rooms():

    rooms = Room.query.all()

    return render_template(
        "manager/rooms.html",
        rooms=rooms
    )


@app.route("/manager/bookings")
def manager_bookings():

    bookings = Booking.query.all()

    return render_template(
        "manager/bookings.html",
        bookings=bookings
    )


@app.route("/manager/complaints")
def manager_complaints():

    complaints = Feedback.query.all()

    return render_template(
        "manager/complaints.html",
        complaints=complaints
    )


# =====================================================
# ================= ADMIN ROUTES ======================
# =====================================================

@app.route("/admin")
def admin_dashboard():
    return render_template("admin/dashboard.html")


@app.route("/admin/analytics")
def admin_analytics():

    total_rooms = Room.query.count()
    total_bookings = Booking.query.count()
    total_users = User.query.count()

    return render_template(
        "admin/analytics.html",
        total_rooms=total_rooms,
        total_bookings=total_bookings,
        total_users=total_users
    )


@app.route("/admin/payments")
def admin_payments():

    payments = Payment.query.all()

    return render_template(
        "admin/payments.html",
        payments=payments
    )


@app.route("/admin/feedback")
def admin_feedback():

    feedback = Feedback.query.all()

    return render_template(
        "admin/feedback.html",
        feedback=feedback
    )


# =====================================================
# ================= RUN ===============================
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)