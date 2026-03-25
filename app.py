from flask import Flask, render_template, request, redirect, url_for, session
from model import db, User, Booking, Room, Payment, Feedback, Complaint
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta

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
@login_required(role="customer")
def customer_dashboard():
    user = User.query.get(session["user_id"])
    rooms = Room.query.all()
    bookings = Booking.query.filter_by(user_id=user.id).all()
    complaints = Complaint.query.filter_by(user_id=user.id).all()
    feedbacks = Feedback.query.filter_by(user_id=user.id).all()

    return render_template(
        "customer/dashboard.html",
        rooms=rooms,
        bookings=bookings,
        complaints=complaints,
        feedbacks=feedbacks
    )


@app.route("/customer/rooms")
@login_required(role="customer")
def customer_rooms():
    return redirect(url_for("customer_dashboard"))


@app.route("/customer/room/<int:id>")
@login_required(role="customer")
def customer_room_detail(id):
    room = Room.query.get_or_404(id)
    return render_template("customer/room_detail.html", room=room)


@app.route("/customer/book/<int:id>", methods=["POST"])
@login_required(role="customer")
def customer_book(id):

    room = Room.query.get_or_404(id)

    days = int(request.form.get("days", 1))
    check_in_date = date.today()
    check_out_date = check_in_date + timedelta(days=days)
    total_amount = room.price * days

    booking = Booking(
        user_id=session["user_id"],
        room_id=id,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        days=days,
        status="pending",
        total_amount=total_amount,
        amount_paid=0
    )

    room.status = "booked"

    db.session.add(booking)
    db.session.commit()

    return redirect(url_for("customer_dashboard"))


@app.route("/customer/payment/<int:booking_id>", methods=["POST"])
@login_required(role="customer")
def customer_payment(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session["user_id"]:
        return "Unauthorized"

    amount = float(request.form.get("amount", booking.total_amount - (booking.amount_paid or 0)))
    mode = request.form.get("mode", "UPI")

    due = booking.total_amount - (booking.amount_paid or 0)
    if amount <= 0 or amount > due:
        return "Invalid payment amount"

    pay = Payment(
        booking_id=booking_id,
        amount=amount,
        payment_method=mode,
        status="verified",
        paid_at=datetime.utcnow()
    )

    booking.amount_paid = (booking.amount_paid or 0) + amount
    if booking.amount_paid >= booking.total_amount:
        booking.status = "confirmed"

    db.session.add(pay)
    db.session.commit()

    return redirect(url_for("customer_dashboard"))


@app.route("/customer/checkin/<int:booking_id>", methods=["POST"])
@login_required(role="customer")
def customer_checkin(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session["user_id"]:
        return "Unauthorized"

    if (booking.amount_paid or 0) < booking.total_amount:
        return "Payment must be completed before check-in"

    if booking.status != "confirmed":
        return "Booking must be confirmed before check-in"

    booking.status = "checked_in"
    booking.room.status = "occupied"
    db.session.commit()

    return redirect(url_for("customer_dashboard"))


@app.route("/customer/feedback", methods=["POST"])
@login_required(role="customer")
def customer_feedback():

    comment = request.form.get("comment")
    rating = int(request.form.get("rating", 0))

    feedback = Feedback(
        user_id=session["user_id"],
        comment=comment,
        rating=rating
    )

    db.session.add(feedback)
    db.session.commit()

    return redirect(url_for("customer_dashboard"))


@app.route("/customer/complaint", methods=["POST"])
@login_required(role="customer")
def customer_complaint():

    subject = request.form.get("subject")
    description = request.form.get("description")

    complaint = Complaint(
        user_id=session["user_id"],
        subject=subject,
        description=description,
        status="open"
    )

    db.session.add(complaint)
    db.session.commit()

    return redirect(url_for("customer_dashboard"))

# =====================================================
# ================= MANAGER ROUTES ====================
# =====================================================

@app.route("/manager")
@login_required(role="manager")
def manager_dashboard():
    rooms = Room.query.all()
    bookings = Booking.query.all()
    complaints = Complaint.query.all()

    return render_template(
        "manager/dashboard.html",
        rooms=rooms,
        bookings=bookings,
        complaints=complaints
    )


@app.route("/manager/rooms")
@login_required(role="manager")
def manager_rooms():
    return redirect(url_for("manager_dashboard"))


@app.route("/manager/bookings")
@login_required(role="manager")
def manager_bookings():
    return redirect(url_for("manager_dashboard"))


@app.route("/manager/complaints")
@login_required(role="manager")
def manager_complaints():
    return redirect(url_for("manager_dashboard"))


@app.route("/manager/complaint/respond/<int:id>", methods=["POST"])
@login_required(role="manager")
def manager_respond_complaint(id):

    complaint = Complaint.query.get_or_404(id)
    complaint.response = request.form.get("response", "")
    complaint.status = "resolved"

    db.session.commit()

    return redirect(url_for("manager_complaints"))


@app.route("/manager/verify-payment/<int:id>", methods=["POST"])
@login_required(role="manager")
def manager_verify_payment(id):

    payment = Payment.query.get_or_404(id)
    payment.status = "verified"
    payment.verified_by = session["user_id"]
    payment.verified_at = datetime.utcnow()

    if payment.booking:
        payment.booking.status = "confirmed"
        payment.booking.amount_paid = payment.booking.amount_paid + payment.amount if payment.booking.amount_paid else payment.amount

    db.session.commit()

    return redirect(url_for("manager_bookings"))


@app.route("/manager/checkout/<int:booking_id>", methods=["POST"])
@login_required(role="manager")
def manager_checkout(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if booking.status not in ["checked_in", "confirmed"]:
        return "Cannot check out unless checked in or confirmed"

    booking.status = "completed"
    if booking.room:
        booking.room.status = "available"

    db.session.commit()

    return redirect(url_for("manager_dashboard"))


# =====================================================
# ================= ADMIN ROUTES ======================
# =====================================================

@app.route("/admin")
@login_required(role="admin")
def admin_dashboard():

    return render_template(
        "admin/dashboard.html",
        total_rooms=Room.query.count(),
        total_users=User.query.count(),
        total_bookings=Booking.query.count(),
        total_payments=Payment.query.count(),

        payments=Payment.query.all(),
        feedback=Feedback.query.all(),
        users=User.query.all(),
        rooms=Room.query.all(),
        bookings=Booking.query.all()
    )


@app.route("/admin/analytics")
@login_required(role="admin")
def admin_analytics():
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/feedback")
@login_required(role="admin")
def admin_feedback():
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/payments")
@login_required(role="admin")
def admin_payments():
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/add-manager", methods=["POST"])
@login_required(role="admin")
def add_manager():

    name = request.form["name"]
    email = request.form["email"]
    password = generate_password_hash(request.form["password"])

    manager = User(
        name=name,
        email=email,
        password=password,
        role="manager"
    )

    db.session.add(manager)
    db.session.commit()

    return redirect(url_for("admin_dashboard"))

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = generate_password_hash(request.form.get("password"))
        role = request.form.get("role")

        # Check if user exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            return "User already exists!"

        user = User(
            name=name,
            email=email,
            phone=phone,
            password=password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# =====================================================
# ================= RUN ===============================
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)