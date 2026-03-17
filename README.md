# 🏨 Hotel Management System (Flask)

A web-based Hotel Management System built using Flask that supports three types of users: **Customer**, **Manager**, and **Admin**. The system streamlines hotel operations including room booking, payment processing, customer management, and feedback handling.

---

## 📌 Features

### 👤 Customer

* Browse available rooms
* Check room details and availability
* Partially book a room
* Complete payment
* Check-in functionality
* Submit feedback and complaints

### 🧑‍💼 Manager

* View all rooms and their status
* Track customer booking status
* Verify customer payments
* Monitor room occupancy
* View and manage complaints
* Take action on customer issues

### 🛠️ Admin

* Access analytics dashboard
* Monitor room and booking status
* Review and respond to feedback
* Verify payment records
* System-wide supervision

---

## 🏗️ Tech Stack

* **Backend:** Flask (Python)
* **Frontend:** HTML, CSS, JavaScript (Jinja2 templating)
* **Database:** SQLite / MySQL (configurable)
* **Other Tools:** Bootstrap (for UI), Flask-Login (for authentication)

---

## 📂 Project Structure

```
hotel-management/
│── app.py
│── requirements.txt
│
├── templates/
│   ├── customer/
│   ├── manager/
│   ├── admin/
│   └── base.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── models.py
│
├── routes/
│   ├── customer_routes.py
│   ├── manager_routes.py
│   └── admin_routes.py
│
└── database/
    └── db.sqlite3
```

---

## ⚙️ Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/hotel-management.git
cd hotel-management
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
flask run
```

5. Open in browser:

```
http://127.0.0.1:5000/
```

---

## 🔐 User Roles Overview

| Role     | Permissions                                      |
| -------- | ------------------------------------------------ |
| Customer | Book rooms, make payments, check-in, feedback    |
| Manager  | Manage rooms, verify payments, handle complaints |
| Admin    | View analytics, manage feedback, oversee system  |

---

## 📊 Key Modules

* **Authentication System** – Login/signup for all roles
* **Room Management** – Add, update, and monitor rooms
* **Booking System** – Partial and full booking workflow
* **Payment Verification** – Manual/automated verification
* **Feedback System** – Customer reviews and complaint handling
* **Admin Dashboard** – Analytics and reports

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.