from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash

# Import the app instance and the db/models
from app import app
from model import db, User, Room, Booking, Payment

def seed_database():
    with app.app_context():
        print("--- Resetting Database ---")
        # Drops all tables and recreates them based on models
        db.drop_all()
        db.create_all()

        # 1. Create Users
        print("Seeding Users...")
        admin = User(
            name="System Admin", 
            email="admin@hotel.com", 
            password=generate_password_hash("admin123"), 
            role="admin", 
            phone="91-8920-370-920"
        )
        manager = User(
            name="John Manager", 
            email="manager@hotel.com", 
            password=generate_password_hash("manager123"), 
            role="manager", 
            phone="91-0000-000-000"
        )
        customer = User(
            name="Jane Customer", 
            email="jane@gmail.com", 
            password=generate_password_hash("customer123"), 
            role="customer", 
            phone="91-1111-111-111"
        )
        db.session.add_all([admin, manager, customer])
        db.session.commit()

        # 2. Create Rooms
        print("Seeding Rooms...")
        room_data = [
            {"num": "101", "type": "Single", "price": 1500.0, "desc": "Cozy city view."},
            {"num": "102", "type": "Single", "price": 1500.0, "desc": "Standard single."},
            {"num": "201", "type": "Double", "price": 2500.0, "desc": "Spacious balcony."},
            {"num": "301", "type": "Suite", "price": 5000.0, "desc": "Luxury ocean view."}
        ]
        
        for r in room_data:
            new_room = Room(
                room_number=r["num"],
                room_type=r["type"],
                price=r["price"],
                description=r["desc"],
                status="available"
            )
            db.session.add(new_room)
        db.session.commit()

        # 3. Create a Sample Booking
        print("Seeding Sample Booking...")
        target_room = Room.query.filter_by(room_number="201").first()
        
        new_booking = Booking(
            user_id=customer.id,
            room_id=target_room.id,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=2),
            days=2,
            status="confirmed",
            total_amount=target_room.price * 2,
            amount_paid=target_room.price * 2
        )
        db.session.add(new_booking)
        db.session.flush() # Flushed to get new_booking.id

        # 4. Create a Payment
        new_payment = Payment(
            booking_id=new_booking.id,
            amount=new_booking.total_amount,
            payment_method="UPI",
            status="verified",
            transaction_id="TXN123456789",
            paid_at=datetime.utcnow()
        )
        db.session.add(new_payment)
        
        # Mark room as booked
        target_room.status = "booked"
        
        db.session.commit()
        print("--- Database Seeded Successfully! ---")

if __name__ == "__main__":
    seed_database()