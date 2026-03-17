from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# -------------------------
# User Model (All Roles)
# -------------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Role: customer / manager / admin
    role = db.Column(db.String(20), nullable=False)

    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='customer', lazy=True)
    feedbacks = db.relationship('Feedback', backref='customer', lazy=True)
    complaints = db.relationship('Complaint', backref='customer', lazy=True)

    def __repr__(self):
        return f"<User {self.email} - {self.role}>"


# -------------------------
# Room Model
# -------------------------
class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # Single, Double, Suite
    price = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(20), default='available')
    # available / booked / occupied / maintenance

    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='room', lazy=True)

    def __repr__(self):
        return f"<Room {self.room_number} - {self.status}>"


# -------------------------
# Booking Model
# -------------------------
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)

    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)

    status = db.Column(db.String(20), default='pending')
    # pending / partially_booked / confirmed / checked_in / completed / cancelled

    total_amount = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payment = db.relationship('Payment', backref='booking', uselist=False)

    def __repr__(self):
        return f"<Booking {self.id} - {self.status}>"


# -------------------------
# Payment Model
# -------------------------
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # UPI, Card, Cash

    status = db.Column(db.String(20), default='pending')
    # pending / verified / failed

    transaction_id = db.Column(db.String(100))
    paid_at = db.Column(db.DateTime)

    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Manager/Admin

    def __repr__(self):
        return f"<Payment {self.id} - {self.status}>"


# -------------------------
# Feedback Model
# -------------------------
class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))

    rating = db.Column(db.Integer)  # 1 to 5
    comment = db.Column(db.Text)

    admin_reply = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.id} - Rating {self.rating}>"


# -------------------------
# Complaint Model
# -------------------------
class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))

    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), default='open')
    # open / in_progress / resolved

    response = db.Column(db.Text)  # Manager response

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Complaint {self.id} - {self.status}>"