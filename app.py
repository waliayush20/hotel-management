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
    return render_template("customer/dashboard.html", bookings=user.bookings)


@app.route("/customer/rooms")
@login_required(role="customer")
def customer_rooms():
    rooms = Room.query.all()
    return render_template("customer/rooms.html", rooms=rooms)


@app.route("/customer/room/<int:id>")
@login_required(role="customer")
def customer_room_detail(id):
    room = Room.query.get_or_404(id)
    return render_template("customer/room_detail.html", room=room)


@app.route("/customer/book/<int:id>", methods=["GET", "POST"])
@login_required(role="customer")
def customer_book(id):

    room = Room.query.get_or_404(id)

    if request.method == "POST":

        days = int(request.form.get("days", 1))
        check_in_date = date.today()
        check_out_date = check_in_date + timedelta(days=days)
        total_amount = room.price * days

        booking = Booking(
            user_id=session["user_id"],
            room_id=id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status="pending",
            total_amount=total_amount,
            amount_paid=0
        )

        room.status = "booked"

        db.session.add(booking)
        db.session.commit()

        return redirect(url_for("customer_payment", booking_id=booking.id))

    return render_template("customer/booking.html", room=room)


@app.route("/customer/payment/<int:booking_id>", methods=["GET", "POST"])
@login_required(role="customer")
def customer_payment(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if request.method == "POST":

        amount = float(request.form["amount"])
        mode = request.form["mode"]

        pay = Payment(
            booking_id=booking_id,
            amount=amount,
            payment_method=mode,
            status="verified"  # mark as immediately verified for customer complete flow
        )

        # Update booking payment summary
        booking.amount_paid = booking.amount_paid + amount if booking.amount_paid else amount
        if booking.amount_paid >= booking.total_amount:
            booking.status = "confirmed"

        db.session.add(pay)
        db.session.commit()

        return redirect(url_for("customer_dashboard"))

    return render_template("customer/payment.html", booking=booking)


@app.route("/customer/checkin/<int:booking_id>", methods=["POST"])
@login_required(role="customer")
def customer_checkin(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session["user_id"]:
        return "Unauthorized"

    if booking.payment and booking.payment.status == "verified":
        booking.status = "checked_in"
        booking.room.status = "occupied"
        db.session.commit()

    return redirect(url_for("customer_dashboard"))


@app.route("/customer/feedback", methods=["GET", "POST"])
@login_required(role="customer")
def customer_feedback():

    if request.method == "POST":
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

    return render_template("customer/feedback.html")


@app.route("/customer/complaint", methods=["GET", "POST"])
@login_required(role="customer")
def customer_complaint():

    if request.method == "POST":
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

    return render_template("customer/complaint.html")


@app.route("/customer/complaints")
@login_required(role="customer")
def customer_complaints():
    complaints = Complaint.query.filter_by(user_id=session["user_id"]).all()
    return render_template("customer/complaints.html", complaints=complaints)


# =====================================================
# ================= MANAGER ROUTES ====================
# =====================================================

@app.route("/manager")
@login_required(role="manager")
def manager_dashboard():
    return render_template("manager/dashboard.html")


@app.route("/manager/rooms")
@login_required(role="manager")
def manager_rooms():

    rooms = Room.query.all()

    return render_template(
        "manager/rooms.html",
        rooms=rooms
    )


@app.route("/manager/bookings")
@login_required(role="manager")
def manager_bookings():

    bookings = Booking.query.all()

    return render_template(
        "manager/bookings.html",
        bookings=bookings
    )


@app.route("/manager/complaints")
@login_required(role="manager")
def manager_complaints():

    complaints = Complaint.query.all()

    return render_template(
        "manager/complaints.html",
        complaints=complaints
    )


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

        users=User.query.all(),
        rooms=Room.query.all(),
        bookings=Booking.query.all()
    )


@app.route("/admin/analytics")
@login_required(role="admin")
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


@app.route("/admin/add-manager", methods=["GET", "POST"])
@login_required(role="admin")
def add_manager():

    if request.method == "POST":

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

    return render_template("admin/add_manager.html")


@app.route("/admin/feedback")
@login_required(role="admin")
def admin_feedback():

    feedback = Feedback.query.all()

    return render_template(
        "admin/feedback.html",
        feedback=feedback
    )

@app.route("/admin/payments")
@login_required(role="admin")
def admin_payments():

    payments = Payment.query.all()

    return render_template(
        "admin/payments.html",
        payments=payments
    )

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