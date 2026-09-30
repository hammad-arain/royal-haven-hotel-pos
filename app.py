from flask import Flask, request, redirect, url_for, render_template_string, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "luxury-hotel-pos-secret"

DATABASE = "hotel_pos.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Rooms
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'Available',
            image TEXT
        )
    """)

    # Bookings
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            phone TEXT,
            room_id INTEGER NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            guests INTEGER DEFAULT 1,
            total REAL DEFAULT 0,
            status TEXT DEFAULT 'Booked',
            created_at TEXT
        )
    """)

    # Restaurant tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER UNIQUE NOT NULL,
            seats INTEGER DEFAULT 4,
            status TEXT DEFAULT 'Available'
        )
    """)

    # Menu
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        )
    """)

    # Orders
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER,
            customer_name TEXT,
            total REAL DEFAULT 0,
            status TEXT DEFAULT 'Open',
            created_at TEXT
        )
    """)

    # Order items
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            menu_id INTEGER,
            quantity INTEGER,
            price REAL,
            subtotal REAL
        )
    """)

    # Create rooms only if empty
    room_count = cur.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]

    if room_count == 0:
        rooms = [
            ("101", "Standard", 7500, "Available",
             "https://images.unsplash.com/photo-1611892440504-42a792e24d32"),
            ("102", "Standard", 7500, "Available",
             "https://images.unsplash.com/photo-1618773928121-c32242e63f39"),
            ("103", "Standard", 7500, "Available",
             "https://images.unsplash.com/photo-1590490360182-c33d57733427"),
            ("104", "Deluxe", 10500, "Available",
             "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b"),
            ("105", "Deluxe", 10500, "Available",
             "https://images.unsplash.com/photo-1566665797739-1674de7a421a"),
            ("106", "Deluxe", 10500, "Available",
             "https://images.unsplash.com/photo-1591088398332-8a7791972843"),
            ("107", "Executive", 14000, "Available",
             "https://images.unsplash.com/photo-1601918774946-25832a4be0d6"),
            ("108", "Executive", 14000, "Available",
             "https://images.unsplash.com/photo-1578683010236-d716f9a3f461"),
            ("109", "Executive", 14000, "Available",
             "https://images.unsplash.com/photo-1595576508898-0ad5c879a061"),
            ("110", "Family", 16500, "Available",
             "https://images.unsplash.com/photo-1590490359683-658d3d23f972"),
            ("111", "Family", 16500, "Available",
             "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6"),
            ("112", "Family", 16500, "Available",
             "https://images.unsplash.com/photo-1560185127-6a8c0d7f8e8f"),
            ("113", "Luxury Suite", 22000, "Available",
             "https://images.unsplash.com/photo-1584132967334-10e028bd69f7"),
            ("114", "Luxury Suite", 22000, "Available",
             "https://images.unsplash.com/photo-1598928506311-c55ded91a20c"),
            ("115", "Presidential Suite", 35000, "Available",
             "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c"),
        ]

        cur.executemany("""
            INSERT INTO rooms
            (room_number, room_type, price, status, image)
            VALUES (?, ?, ?, ?, ?)
        """, rooms)

    # Create 12 restaurant tables
    table_count = cur.execute(
        "SELECT COUNT(*) FROM restaurant_tables"
    ).fetchone()[0]

    if table_count == 0:
        tables = [(i, 4 if i <= 8 else 6) for i in range(1, 13)]

        cur.executemany("""
            INSERT INTO restaurant_tables
            (table_number, seats)
            VALUES (?, ?)
        """, tables)

    # Menu
    menu_count = cur.execute(
        "SELECT COUNT(*) FROM menu"
    ).fetchone()[0]

    if menu_count == 0:

        menu_items = [

            # BURGERS
            ("Classic Zinger Burger", "Burgers", 650,
             "Crispy chicken fillet, lettuce and special sauce"),
            ("Cheesy Zinger Burger", "Burgers", 750,
             "Crispy chicken, cheese and signature sauce"),
            ("Chicken Burger", "Burgers", 600,
             "Grilled chicken fillet with fresh vegetables"),
            ("Beef Burger", "Burgers", 700,
             "Juicy beef patty with cheese and vegetables"),
            ("Double Beef Burger", "Burgers", 950,
             "Two beef patties with double cheese"),

            # DESI
            ("Chicken Karahi", "Desi", 1600,
             "Traditional chicken karahi"),
            ("Mutton Karahi", "Desi", 2200,
             "Traditional mutton karahi"),
            ("Beef Karahi", "Desi", 1900,
             "Spicy beef karahi"),
            ("White Chicken Karahi", "Desi", 1800,
             "Creamy white chicken karahi"),
            ("Chicken Handi", "Desi", 1700,
             "Creamy chicken handi"),
            ("Chicken Biryani", "Desi", 550,
             "Traditional aromatic chicken biryani"),
            ("Mutton Biryani", "Desi", 750,
             "Mutton biryani with aromatic rice"),
            ("Chicken Pulao", "Desi", 500,
             "Traditional chicken pulao"),

            # PIZZA
            ("Chicken Tikka Pizza", "Pizza", 1450,
             "Chicken tikka, mozzarella and vegetables"),
            ("Chicken Fajita Pizza", "Pizza", 1550,
             "Fajita chicken, peppers and cheese"),
            ("Malai Boti Pizza", "Pizza", 1650,
             "Malai boti, mozzarella and special sauce"),
            ("Pepperoni Pizza", "Pizza", 1700,
             "Pepperoni and mozzarella cheese"),
            ("Cheese Lover Pizza", "Pizza", 1350,
             "Four cheese blend"),

            # CHINESE
            ("Chicken Chow Mein", "Chinese", 850,
             "Stir-fried noodles with chicken"),
            ("Chicken Manchurian", "Chinese", 950,
             "Chicken with Manchurian sauce"),
            ("Chicken Fried Rice", "Chinese", 800,
             "Fried rice with chicken and vegetables"),
            ("Chicken Shashlik", "Chinese", 1100,
             "Chicken skewers with vegetables"),
            ("Hot & Sour Soup", "Chinese", 550,
             "Classic Chinese hot and sour soup"),

            # BBQ
            ("Chicken Tikka", "BBQ", 750,
             "Charcoal grilled chicken tikka"),
            ("Chicken Malai Boti", "BBQ", 850,
             "Creamy marinated chicken"),
            ("Seekh Kabab", "BBQ", 800,
             "Traditional beef seekh kabab"),
            ("Chicken Wings", "BBQ", 700,
             "Spicy BBQ chicken wings"),
            ("BBQ Platter", "BBQ", 2200,
             "Mixed BBQ platter"),

            # SIDES
            ("Fresh Salad", "Sides", 300,
             "Fresh seasonal vegetables"),
            ("Russian Salad", "Sides", 450,
             "Creamy Russian salad"),
            ("Raita", "Sides", 180,
             "Fresh yogurt raita"),
            ("French Fries", "Sides", 300,
             "Crispy golden fries"),
            ("Chapati", "Sides", 70,
             "Fresh tandoori chapati"),
            ("Naan", "Sides", 100,
             "Fresh tandoori naan"),
            ("Garlic Naan", "Sides", 180,
             "Garlic butter naan"),

            # DRINKS
            ("Pepsi", "Drinks", 180,
             "Chilled soft drink"),
            ("7UP", "Drinks", 180,
             "Chilled soft drink"),
            ("Mirinda", "Drinks", 180,
             "Chilled soft drink"),
            ("Fresh Lime", "Drinks", 280,
             "Fresh lime drink"),
            ("Mineral Water 500ml", "Drinks", 100,
             "Bottled mineral water"),
            ("Mineral Water 1.5L", "Drinks", 180,
             "Bottled mineral water"),

            # DESSERTS
            ("Gulab Jamun", "Desserts", 250,
             "Traditional sweet dessert"),
            ("Kheer", "Desserts", 300,
             "Creamy rice pudding"),
            ("Brownie with Ice Cream", "Desserts", 550,
             "Warm chocolate brownie"),
            ("Chocolate Cake", "Desserts", 450,
             "Rich chocolate cake"),
            ("Ice Cream", "Desserts", 350,
             "Two scoops of ice cream"),

            # FAST FOOD
            ("Chicken Shawarma", "Food", 450,
             "Grilled chicken, garlic sauce and fresh vegetables"),
            ("Chicken Club Sandwich", "Food", 750,
             "Triple-layer sandwich with chicken, egg and vegetables"),
            ("Grilled Chicken Sandwich", "Food", 650,
             "Grilled chicken with lettuce, cheese and special sauce"),
            ("Chicken Wrap", "Food", 500,
             "Crispy chicken wrap with fresh vegetables and sauce"),
            ("Chicken Nuggets", "Food", 550,
             "Crispy golden chicken nuggets"),
            ("Fish & Chips", "Food", 950,
             "Crispy fried fish served with French fries"),
            ("Chicken Alfredo Pasta", "Food", 950,
             "Creamy Alfredo pasta with grilled chicken"),
            ("Arrabbiata Pasta", "Food", 800,
             "Penne pasta in spicy tomato sauce"),
            ("Chicken Lasagna", "Food", 1000,
             "Layered pasta with chicken, cheese and rich tomato sauce"),
            ("Loaded Fries", "Food", 650,
             "French fries topped with chicken, cheese and special sauce"),

            # PASTRIES
            ("Chocolate Croissant", "Pastries", 350,
             "Buttery croissant filled with rich chocolate"),
            ("Plain Butter Croissant", "Pastries", 300,
             "Freshly baked buttery French croissant"),
            ("Almond Croissant", "Pastries", 400,
             "Crispy croissant with almond filling"),
            ("Blueberry Muffin", "Pastries", 320,
             "Soft muffin filled with blueberries"),
            ("Chocolate Muffin", "Pastries", 320,
             "Soft chocolate muffin with chocolate chips"),
            ("Cinnamon Roll", "Pastries", 380,
             "Freshly baked cinnamon roll with sweet glaze"),
            ("Apple Danish", "Pastries", 400,
             "Flaky Danish pastry with apple filling"),
            ("Chocolate Danish", "Pastries", 420,
             "Flaky pastry filled with chocolate"),
            ("Cream Puff", "Pastries", 350,
             "Light pastry filled with vanilla cream"),
            ("Fruit Tart", "Pastries", 450,
             "Buttery tart topped with fresh seasonal fruit"),
        ]

        cur.executemany("""
            INSERT INTO menu
            (name, category, price, description)
            VALUES (?, ?, ?, ?)
        """, menu_items)

    conn.commit()
    conn.close()


# ============================================================
# HTML / CSS
# ============================================================

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>{{ title }} | Royal Haven Hotel</title>

    <link rel="preconnect"
          href="https://fonts.googleapis.com">

    <link rel="preconnect"
          href="https://fonts.gstatic.com"
          crossorigin>

    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap"
          rel="stylesheet">

    <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background: #0b0b0d;
            color: #eee;
        }

        a {
            text-decoration: none;
            color: inherit;
        }

        .navbar {
            height: 76px;
            background: rgba(10,10,12,.96);
            border-bottom: 1px solid rgba(212,175,55,.25);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 5%;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo {
            font-family: 'Cinzel', serif;
            color: #d8b45a;
            font-size: 22px;
            letter-spacing: 2px;
        }

        .navlinks {
            display: flex;
            gap: 22px;
            align-items: center;
        }

        .navlinks a {
            color: #ddd;
            font-size: 13px;
            transition: .3s;
        }

        .navlinks a:hover {
            color: #e0b957;
        }

        .hero {
            min-height: 680px;
            display: flex;
            align-items: center;
            position: relative;
            background:
            linear-gradient(90deg,
            rgba(0,0,0,.86),
            rgba(0,0,0,.35)),
            url("https://images.unsplash.com/photo-1566073771259-6a8506099945")
            center/cover;
        }

        .hero-content {
            width: 90%;
            max-width: 1200px;
            margin: auto;
        }

        .hero h1 {
            font-family: 'Cinzel', serif;
            font-size: clamp(42px, 7vw, 82px);
            color: white;
            max-width: 800px;
            line-height: 1.05;
        }

        .gold {
            color: #d8b45a;
        }

        .hero p {
            max-width: 600px;
            margin: 25px 0;
            color: #ddd;
            font-size: 17px;
        }

        .btn {
            display: inline-block;
            background: #c9a24d;
            color: #111;
            padding: 13px 23px;
            border-radius: 4px;
            border: none;
            font-weight: 700;
            cursor: pointer;
            transition: .3s;
        }

        .btn:hover {
            background: #f1d27b;
            transform: translateY(-2px);
        }

        .btn-dark {
            background: #171719;
            color: #e7c56a;
            border: 1px solid #6d5829;
        }

        .section {
            width: 90%;
            max-width: 1200px;
            margin: 70px auto;
        }

        .section-title {
            text-align: center;
            margin-bottom: 35px;
        }

        .section-title small {
            color: #d5b15b;
            text-transform: uppercase;
            letter-spacing: 3px;
        }

        .section-title h2 {
            font-family: 'Cinzel', serif;
            font-size: 36px;
            margin-top: 8px;
        }

        .cards {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(250px, 1fr));
            gap: 22px;
        }

        .card {
            background: #151518;
            border: 1px solid #28282b;
            border-radius: 8px;
            overflow: hidden;
            transition: .3s;
        }

        .card:hover {
            transform: translateY(-6px);
            border-color: #a98535;
        }

        .card img {
            width: 100%;
            height: 210px;
            object-fit: cover;
        }

        .card-content {
            padding: 20px;
        }

        .card h3 {
            font-family: 'Cinzel', serif;
            margin-bottom: 10px;
        }

        .price {
            color: #e3bc5b;
            font-weight: 700;
        }

        .dashboard {
            width: 90%;
            max-width: 1250px;
            margin: 40px auto;
        }

        .page-title {
            font-family: 'Cinzel', serif;
            font-size: 35px;
            margin-bottom: 30px;
        }

        .stats {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px;
            margin-bottom: 35px;
        }

        .stat {
            background: linear-gradient(135deg, #18181c, #101012);
            border: 1px solid #302d26;
            padding: 25px;
            border-radius: 10px;
        }

        .stat h3 {
            font-size: 30px;
            color: #e2bd61;
        }

        .stat p {
            color: #999;
            margin-top: 5px;
        }

        .table-wrap {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: #151518;
        }

        th, td {
            padding: 15px;
            border-bottom: 1px solid #29292c;
            text-align: left;
        }

        th {
            color: #d9b85d;
            font-size: 13px;
        }

        td {
            color: #ddd;
            font-size: 14px;
        }

        .status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 11px;
            background: #242428;
        }

        .available {
            color: #69db91;
        }

        .occupied {
            color: #ff7474;
        }

        .reserved {
            color: #e2bd61;
        }

        .form-box {
            background: #151518;
            padding: 30px;
            border: 1px solid #2b2b2e;
            border-radius: 10px;
            max-width: 700px;
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }

        .input-group {
            margin-bottom: 18px;
        }

        label {
            display: block;
            margin-bottom: 7px;
            color: #cfcfcf;
            font-size: 13px;
        }

        input, select {
            width: 100%;
            padding: 13px;
            background: #0d0d0f;
            color: white;
            border: 1px solid #333;
            border-radius: 5px;
            outline: none;
        }

        input:focus, select:focus {
            border-color: #b99340;
        }

        .menu-grid {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
        }

        .menu-item {
            background: #151518;
            border: 1px solid #29292c;
            padding: 20px;
            border-radius: 8px;
        }

        .menu-item h3 {
            font-size: 17px;
        }

        .menu-item p {
            color: #888;
            font-size: 12px;
            margin: 8px 0 15px;
        }

        .menu-top {
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }

        .category {
            color: #bda05a;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .order-panel {
            background: #151518;
            border: 1px solid #29292c;
            padding: 25px;
            border-radius: 10px;
            margin-top: 30px;
        }

        .table-grid {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(130px, 1fr));
            gap: 15px;
        }

        .restaurant-table {
            padding: 25px 15px;
            text-align: center;
            border-radius: 8px;
            border: 1px solid #333;
            background: #161619;
        }

        .restaurant-table.available {
            border-color: #3e754f;
        }

        .restaurant-table.occupied {
            border-color: #803f3f;
        }

        .footer {
            background: #070708;
            border-top: 1px solid #27272a;
            padding: 45px 5%;
            text-align: center;
            color: #777;
            margin-top: 80px;
        }

        .filter-bar {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 25px;
        }

        .filter-bar a {
            border: 1px solid #39393d;
            padding: 9px 15px;
            border-radius: 30px;
            font-size: 12px;
            color: #bbb;
        }

        .filter-bar a:hover {
            color: #e3bc5b;
            border-color: #9a7935;
        }

        .bill {
            max-width: 850px;
            margin: 50px auto;
            background: white;
            color: #222;
            padding: 40px;
            border-radius: 5px;
        }

        .bill h1 {
            font-family: 'Cinzel', serif;
            color: #222;
        }

        .bill table {
            color: #222;
            background: white;
        }

        .bill th, .bill td {
            color: #222;
            border-bottom: 1px solid #ddd;
        }

        .bill-total {
            text-align: right;
            font-size: 23px;
            margin-top: 20px;
        }

        .alert {
            width: 90%;
            max-width: 1200px;
            margin: 20px auto;
            padding: 14px;
            background: #27220f;
            color: #e4c15e;
            border: 1px solid #705827;
            border-radius: 5px;
        }

        @media(max-width: 700px) {

            .navbar {
                height: auto;
                padding: 18px;
                flex-direction: column;
                gap: 15px;
            }

            .navlinks {
                flex-wrap: wrap;
                justify-content: center;
            }

            .hero {
                min-height: 600px;
            }

            .form-grid {
                grid-template-columns: 1fr;
            }

            .section {
                width: 92%;
            }
        }

        @media print {
            .navbar,
            .footer,
            .no-print {
                display: none !important;
            }

            body {
                background: white;
            }

            .bill {
                margin: 0;
                width: 100%;
            }
        }

    </style>
</head>

<body>

<nav class="navbar">

    <a href="/" class="logo">
        ROYAL HAVEN
    </a>

    <div class="navlinks">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/rooms">Rooms</a>
        <a href="/bookings">Bookings</a>
        <a href="/restaurant">Restaurant POS</a>
        <a href="/menu">Menu</a>
        <a href="/orders">Orders</a>
    </div>

</nav>

{% with messages = get_flashed_messages() %}
    {% if messages %}
        {% for message in messages %}
            <div class="alert">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}

{{ content|safe }}

<footer class="footer">
    <h3 class="gold">ROYAL HAVEN HOTEL</h3>
    <p>Luxury accommodation • Fine dining • Professional service</p>
    <br>
    <p>Hotel Management & Restaurant POS System</p>
</footer>

</body>
</html>
"""


def render_page(title, content_template, **context):
    content = render_template_string(content_template, **context)
    return render_template_string(
        BASE_HTML,
        title=title,
        content=content
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    conn = get_db()

    rooms = conn.execute(
        "SELECT * FROM rooms LIMIT 6"
    ).fetchall()

    conn.close()

    content = """
    <section class="hero">

        <div class="hero-content">

            <p class="gold">
                FIVE STAR HOSPITALITY
            </p>

            <h1>
                Your Stay,
                <span class="gold">Elevated.</span>
            </h1>

            <p>
                Experience elegant rooms, exceptional dining,
                relaxing leisure facilities and personalized
                hospitality at Royal Haven Hotel.
            </p>

            <a href="/rooms" class="btn">
                Explore Rooms
            </a>

            <a href="/restaurant"
               class="btn btn-dark">
                Restaurant POS
            </a>

        </div>

    </section>

    <section class="section">

        <div class="section-title">
            <small>Stay in comfort</small>
            <h2>Featured Rooms</h2>
        </div>

        <div class="cards">

            {% for room in rooms %}

            <div class="card">

                <img src="{{ room['image'] }}?auto=format&fit=crop&w=900&q=80">

                <div class="card-content">

                    <h3>
                        {{ room['room_type'] }}
                    </h3>

                    <p>
                        Room {{ room['room_number'] }}
                    </p>

                    <br>

                    <span class="price">
                        PKR {{ "{:,.0f}".format(room['price']) }}
                        / night
                    </span>

                </div>

            </div>

            {% endfor %}

        </div>

    </section>

    <section class="section">

        <div class="section-title">
            <small>World class facilities</small>
            <h2>Hotel Experience</h2>
        </div>

        <div class="cards">

            <div class="card">
                <img src="https://images.unsplash.com/photo-1544161515-4ab6ce6db874">
                <div class="card-content">
                    <h3>Swimming Pool</h3>
                    <p>Relax beside our beautiful pool.</p>
                </div>
            </div>

            <div class="card">
                <img src="https://images.unsplash.com/photo-1534438327276-14e5300c3a48">
                <div class="card-content">
                    <h3>Fitness Center</h3>
                    <p>Modern equipment for your daily workout.</p>
                </div>
            </div>

            <div class="card">
                <img src="https://images.unsplash.com/photo-1551882547-ff40c63fe5fa">
                <div class="card-content">
                    <h3>Luxury Lobby</h3>
                    <p>A sophisticated welcome for every guest.</p>
                </div>
            </div>

            <div class="card">
                <img src="https://images.unsplash.com/photo-1414235077428-338989a2e8c0">
                <div class="card-content">
                    <h3>Fine Dining</h3>
                    <p>Pakistani, Chinese and international cuisine.</p>
                </div>
            </div>

        </div>

    </section>
    """

    return render_page(
        "Home",
        content,
        rooms=rooms
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    conn = get_db()

    total_rooms = conn.execute(
        "SELECT COUNT(*) FROM rooms"
    ).fetchone()[0]

    available_rooms = conn.execute(
        "SELECT COUNT(*) FROM rooms WHERE status='Available'"
    ).fetchone()[0]

    booked_rooms = conn.execute(
        "SELECT COUNT(*) FROM rooms WHERE status!='Available'"
    ).fetchone()[0]

    total_tables = conn.execute(
        "SELECT COUNT(*) FROM restaurant_tables"
    ).fetchone()[0]

    occupied_tables = conn.execute(
        "SELECT COUNT(*) FROM restaurant_tables WHERE status='Occupied'"
    ).fetchone()[0]

    total_orders = conn.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    revenue = conn.execute(
        "SELECT COALESCE(SUM(total),0) FROM orders WHERE status='Paid'"
    ).fetchone()[0]

    conn.close()

    content = """

    <div class="dashboard">

        <h1 class="page-title">
            Management Dashboard
        </h1>

        <div class="stats">

            <div class="stat">
                <h3>{{ total_rooms }}</h3>
                <p>Total Rooms</p>
            </div>

            <div class="stat">
                <h3>{{ available_rooms }}</h3>
                <p>Available Rooms</p>
            </div>

            <div class="stat">
                <h3>{{ booked_rooms }}</h3>
                <p>Occupied / Reserved</p>
            </div>

            <div class="stat">
                <h3>{{ total_tables }}</h3>
                <p>Restaurant Tables</p>
            </div>

            <div class="stat">
                <h3>{{ occupied_tables }}</h3>
                <p>Occupied Tables</p>
            </div>

            <div class="stat">
                <h3>{{ total_orders }}</h3>
                <p>Total Orders</p>
            </div>

            <div class="stat">
                <h3>
                    PKR {{ "{:,.0f}".format(revenue) }}
                </h3>
                <p>Paid Restaurant Revenue</p>
            </div>

        </div>

        <div class="cards">

            <div class="card">
                <div class="card-content">
                    <h3>Hotel Management</h3>
                    <p>
                        Manage rooms, reservations,
                        check-ins and check-outs.
                    </p>
                    <br>
                    <a href="/rooms" class="btn">
                        Rooms
                    </a>
                </div>
            </div>

            <div class="card">
                <div class="card-content">
                    <h3>Restaurant POS</h3>
                    <p>
                        Take customer orders and
                        generate restaurant bills.
                    </p>
                    <br>
                    <a href="/restaurant" class="btn">
                        Open POS
                    </a>
                </div>
            </div>

            <div class="card">
                <div class="card-content">
                    <h3>Bookings</h3>
                    <p>
                        View hotel guest reservations.
                    </p>
                    <br>
                    <a href="/bookings" class="btn">
                        View Bookings
                    </a>
                </div>
            </div>

        </div>

    </div>
    """

    return render_page(
        "Dashboard",
        content,
        total_rooms=total_rooms,
        available_rooms=available_rooms,
        booked_rooms=booked_rooms,
        total_tables=total_tables,
        occupied_tables=occupied_tables,
        total_orders=total_orders,
        revenue=revenue
    )


# ============================================================
# ROOMS
# ============================================================

@app.route("/rooms")
def rooms():

    conn = get_db()

    rooms = conn.execute(
        "SELECT * FROM rooms ORDER BY id"
    ).fetchall()

    conn.close()

    content = """

    <div class="dashboard">

        <h1 class="page-title">
            Hotel Rooms
        </h1>

        <div class="cards">

            {% for room in rooms %}

            <div class="card">

                <img src="{{ room['image'] }}?auto=format&fit=crop&w=900&q=80">

                <div class="card-content">

                    <h3>
                        Room {{ room['room_number'] }}
                    </h3>

                    <p>
                        {{ room['room_type'] }}
                    </p>

                    <br>

                    <span class="price">
                        PKR {{ "{:,.0f}".format(room['price']) }}
                        / night
                    </span>

                    <br><br>

                    <span class="status
                        {% if room['status'] == 'Available' %}
                            available
                        {% else %}
                            occupied
                        {% endif %}
                    ">
                        {{ room['status'] }}
                    </span>

                    <br><br>

                    {% if room['status'] == 'Available' %}

                    <a href="/book/{{ room['id'] }}"
                       class="btn">
                        Book Room
                    </a>

                    {% endif %}

                </div>

            </div>

            {% endfor %}

        </div>

    </div>

    """

    return render_page(
        "Rooms",
        content,
        rooms=rooms
    )


# ============================================================
# BOOK ROOM
# ============================================================

@app.route("/book/<int:room_id>", methods=["GET", "POST"])
def book_room(room_id):

    conn = get_db()

    room = conn.execute(
        "SELECT * FROM rooms WHERE id=?",
        (room_id,)
    ).fetchone()

    if not room:
        conn.close()
        return "Room not found", 404

    if request.method == "POST":

        guest_name = request.form["guest_name"]
        phone = request.form["phone"]
        check_in = request.form["check_in"]
        check_out = request.form["check_out"]
        guests = int(request.form["guests"])

        try:
            start = datetime.strptime(
                check_in, "%Y-%m-%d"
            )

            end = datetime.strptime(
                check_out, "%Y-%m-%d"
            )

            nights = (end - start).days

            if nights <= 0:
                flash("Check-out must be after check-in.")
                conn.close()
                return redirect(
                    url_for("book_room", room_id=room_id)
                )

        except ValueError:
            flash("Invalid date.")
            conn.close()
            return redirect(
                url_for("book_room", room_id=room_id)
            )

        total = nights * room["price"]

        conn.execute("""
            INSERT INTO bookings
            (guest_name, phone, room_id, check_in,
             check_out, guests, total, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            guest_name,
            phone,
            room_id,
            check_in,
            check_out,
            guests,
            total,
            "Booked",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

        conn.execute("""
            UPDATE rooms
            SET status='Reserved'
            WHERE id=?
        """, (room_id,))

        conn.commit()
        conn.close()

        flash(
            f"Room {room['room_number']} booked successfully!"
        )

        return redirect(url_for("bookings"))

    conn.close()

    content = """

    <div class="dashboard">

        <h1 class="page-title">
            Book Room {{ room['room_number'] }}
        </h1>

        <div class="form-box">

            <h2>{{ room['room_type'] }}</h2>

            <p class="price">
                PKR {{ "{:,.0f}".format(room['price']) }}
                / night
            </p>

            <br>

            <form method="POST">

                <div class="form-grid">

                    <div class="input-group">
                        <label>Guest Name</label>
                        <input
                            type="text"
                            name="guest_name"
                            required>
                    </div>

                    <div class="input-group">
                        <label>Phone</label>
                        <input
                            type="text"
                            name="phone"
                            required>
                    </div>

                    <div class="input-group">
                        <label>Check In</label>
                        <input
                            type="date"
                            name="check_in"
                            required>
                    </div>

                    <div class="input-group">
                        <label>Check Out</label>
                        <input
                            type="date"
                            name="check_out"
                            required>
                    </div>

                    <div class="input-group">
                        <label>Number of Guests</label>
                        <input
                            type="number"
                            name="guests"
                            min="1"
                            value="1"
                            required>
                    </div>

                </div>

                <button class="btn">
                    Confirm Booking
                </button>

            </form>

        </div>

    </div>

    """

    return render_page(
        "Book Room",
        content,
        room=room
    )


# ============================================================
# BOOKINGS
# ============================================================

@app.route("/bookings")
def bookings():

    conn = get_db()

    bookings = conn.execute("""
        SELECT
            bookings.*,
            rooms.room_number,
            rooms.room_type
        FROM bookings
        JOIN rooms
        ON bookings.room_id = rooms.id
        ORDER BY bookings.id DESC
    """).fetchall()

    conn.close()

    content = """

    <div class="dashboard">

        <h1 class="page-title">
            Hotel Bookings
        </h1>

        <div class="table-wrap">

        <table>

            <tr>
                <th>ID</th>
                <th>Guest</th>
                <th>Room</th>
                <th>Check In</th>
                <th>Check Out</th>
                <th>Guests</th>
                <th>Total</th>
                <th>Status</th>
                <th>Action</th>
            </tr>

            {% for b in bookings %}

            <tr>

                <td>#{{ b['id'] }}</td>

                <td>
                    {{ b['guest_name'] }}<br>
                    <small>{{ b['phone'] }}</small>
                </td>

                <td>
                    {{ b['room_number'] }}
                    <br>
                    {{ b['room_type'] }}
                </td>

                <td>{{ b['check_in'] }}</td>
                <td>{{ b['check_out'] }}</td>

                <td>{{ b['guests'] }}</td>

                <td>
                    PKR {{ "{:,.0f}".format(b['total']) }}
                </td>

                <td>
                    <span class="status reserved">
                        {{ b['status'] }}
                    </span>
                </td>

                <td>

                    {% if b['status'] != 'Checked Out' %}

                    <a
                        href="/checkout/{{ b['id'] }}"
                        class="btn">
                        Check Out
                    </a>

                    {% endif %}

                </td>

            </tr>

            {% endfor %}

        </table>

        </div>

    </div>

    """

    return render_page(
        "Bookings",
        content,
        bookings=bookings
    )


# ============================================================
# CHECKOUT
# ============================================================

@app.route("/checkout/<int:booking_id>")
def checkout(booking_id):

    conn = get_db()

    booking = conn.execute("""
        SELECT * FROM bookings
        WHERE id=?
    """, (booking_id,)).fetchone()

    if not booking:
        conn.close()
        return "Booking not found", 404

    conn.execute("""
        UPDATE bookings
        SET status='Checked Out'
        WHERE id=?
    """, (booking_id,))

    conn.execute("""
        UPDATE rooms
        SET status='Available'
        WHERE id=?
    """, (booking["room_id"],))

    conn.commit()
    conn.close()

    flash("Guest checked out and room is available again.")

    return redirect(url_for("bookings"))


# ============================================================
# RESTAURANT POS
# ============================================================

@app.route("/restaurant")
def restaurant():

    category = request.args.get("category", "All")

    conn = get_db()

    tables = conn.execute("""
        SELECT * FROM restaurant_tables
        ORDER BY table_number
    """).fetchall()

    if category == "All":
        menu = conn.execute("""
            SELECT * FROM menu
            ORDER BY category, name
        """).fetchall()
    else:
        menu = conn.execute("""
            SELECT * FROM menu
            WHERE category=?
            ORDER BY name
        """, (category,)).fetchall()

    categories = conn.execute("""
        SELECT DISTINCT category
        FROM menu
        ORDER BY category
    """).fetchall()

    conn.close()

    content = """

    <div class="dashboard">

        <h1 class="page-title">
            Restaurant POS
        </h1>

        <h2 style="margin-bottom:20px;">
            Select Table
        </h2>

        <div class="table-grid">

            {% for table in tables %}

            <div class="restaurant-table
                {% if table['status'] == 'Available' %}
                    available
                {% else %}
                    occupied
                {% endif %}
            ">

                <h2>
                    Table {{ table['table_number'] }}
                </h2>

                <p>
                    {{ table['seats'] }} Seats
                </p>

                <br>

                <span class="status">
                    {{ table['status'] }}
                </span>

                {% if table['status'] == 'Available' %}

                <br><br>

                <a
                    href="/new-order/{{ table['id'] }}"
                    class="btn">
                    New Order
                </a>

                {% endif %}

            </div>

            {% endfor %}

        </div>

        <br><br>

        <h2>Menu</h2>

        <div class="filter-bar">

            <a href="/restaurant">
                All
            </a>

            {% for c in categories %}

            <a href="/restaurant?category={{ c['category'] }}">
                {{ c['category'] }}
            </a>

            {% endfor %}

        </div>

        <div class="menu-grid">

            {% for item in menu %}

            <div class="menu-item">

                <div class="menu-top">

                    <h3>
                        {{ item['name'] }}
                    </h3>

                    <span class="price">
                        {{ "{:,.0f}".format(item['price']) }}
                    </span>

                </div>

                <span class="category">
                    {{ item['category'] }}
                </span>

                <p>
                    {{ item['description'] }}
                </p>

            </div>

            {% endfor %}

        </div>

    </div>

    """

    return render_page(
        "Restaurant POS",
        content,
        tables=tables,
        menu=menu,
        categories=categories
    )


# ============================================================
# NEW ORDER
# ============================================================

@app.route("/new-order/<int:table_id>", methods=["GET", "POST"])
def new_order(table_id):

    conn = get_db()

    table = conn.execute("""
        SELECT * FROM restaurant_tables
        WHERE id=?
    """, (table_id,)).fetchone()

    menu = conn.execute("""
        SELECT * FROM menu
        ORDER BY category, name
    """).fetchall()

    if not table:
        conn.close()
        return "Table not found", 404

    if request.method == "POST":

        customer_name = request.form.get(
            "customer_name", "Walk-in Customer"
        )

        selected_items = []

        for item in menu:

            quantity = int(
                request.form.get(
                    f"quantity_{item['id']}", 0
                )
            )

            if quantity > 0:
                selected_items.append(
                    (item, quantity)
                )

        if not selected_items:
            flash("Please select at least one menu item.")
            conn.close()
            return redirect(
                url_for("new_order", table_id=table_id)
            )

        total = sum(
            item["price"] * quantity
            for item, quantity in selected_items
        )

        cursor = conn.execute("""
            INSERT INTO orders
            (table_id, customer_name, total,
             status, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            table_id,
            customer_name,
            total,
            "Open",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

        order_id = cursor.lastrowid

        for item, quantity in selected_items:

            subtotal = item["price"] * quantity

            conn.execute("""
                INSERT INTO order_items
                (order_id, menu_id, quantity,
                 price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (
                order_id,
                item["id"],
                quantity,
                item["price"],
                subtotal
            ))

        conn.execute("""
            UPDATE restaurant_tables
            SET status='Occupied'
            WHERE id=?
        """, (table_id,))

        conn.commit()
        conn.close()

        return redirect(
            url_for("order_bill", order_id=order_id)
        )

    conn.close()

    content = """

    <div class="dashboard">

        <h1 class="page-title">
            New Order — Table {{ table['table_number'] }}
        </h1>

        <form method="POST">

            <div class="form-box"
                 style="max-width:100%;">

                <div class="input-group">

                    <label>
                        Customer Name
                    </label>

                    <input
                        type="text"
                        name="customer_name"
                        placeholder="Walk-in Customer">

                </div>

            </div>

            <br>

            <div class="menu-grid">

                {% for item in menu %}

                <div class="menu-item">

                    <div class="menu-top">

                        <h3>
                            {{ item['name'] }}
                        </h3>

                        <span class="price">
                            PKR {{ "{:,.0f}".format(item['price']) }}
                        </span>

                    </div>

                    <span class="category">
                        {{ item['category'] }}
                    </span>

                    <p>
                        {{ item['description'] }}
                    </p>

                    <label>
                        Quantity
                    </label>

                    <input
                        type="number"
                        min="0"
                        value="0"
                        name="quantity_{{ item['id'] }}">

                </div>

                {% endfor %}

            </div>

            <br>

            <button class="btn">
                Create Order & Generate Bill
            </button>

        </form>

    </div>

    """

    return render_page(
        "New Order",
        content,
        table=table,
        menu=menu
    )


# ============================================================
# ORDERS
# ============================================================

@app.route("/orders")
def orders():

    conn = get_db()

    orders = conn.execute("""
        SELECT
            orders.*,
            restaurant_tables.table_number
        FROM orders
        LEFT JOIN restaurant_tables
        ON orders.table_id = restaurant_tables.id
        ORDER BY orders.id DESC
    """).fetchall()

    conn.close()

    content = """

    <div class="dashboard">

        <h1 class="page-title">
            Restaurant Orders
        </h1>

        <div class="table-wrap">

        <table>

            <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Table</th>
                <th>Date</th>
                <th>Total</th>
                <th>Status</th>
                <th>Bill</th>
            </tr>

            {% for order in orders %}

            <tr>

                <td>
                    #{{ order['id'] }}
                </td>

                <td>
                    {{ order['customer_name'] }}
                </td>

                <td>
                    Table {{ order['table_number'] }}
                </td>

                <td>
                    {{ order['created_at'] }}
                </td>

                <td>
                    PKR {{ "{:,.0f}".format(order['total']) }}
                </td>

                <td>
                    <span class="status">
                        {{ order['status'] }}
                    </span>
                </td>

                <td>
                    <a
                        href="/order/{{ order['id'] }}/bill"
                        class="btn">
                        View Bill
                    </a>
                </td>

            </tr>

            {% endfor %}

        </table>

        </div>

    </div>

    """

    return render_page(
        "Orders",
        content,
        orders=orders
    )


# ============================================================
# RESTAURANT BILL
# ============================================================

@app.route("/order/<int:order_id>/bill")
def order_bill(order_id):

    conn = get_db()

    order = conn.execute("""
        SELECT
            orders.*,
            restaurant_tables.table_number
        FROM orders
        LEFT JOIN restaurant_tables
        ON orders.table_id = restaurant_tables.id
        WHERE orders.id=?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        return "Order not found", 404

    items = conn.execute("""
        SELECT
            order_items.*,
            menu.name
        FROM order_items
        JOIN menu
        ON order_items.menu_id = menu.id
        WHERE order_id=?
    """, (order_id,)).fetchall()

    conn.close()

    content = """

    <div class="bill">

        <div style="text-align:center;">

            <h1>
                ROYAL HAVEN HOTEL
            </h1>

            <p>
                Restaurant & Fine Dining
            </p>

            <br>

            <h2>
                RESTAURANT BILL
            </h2>

        </div>

        <br>

        <p>
            <strong>Order:</strong>
            #{{ order['id'] }}
        </p>

        <p>
            <strong>Customer:</strong>
            {{ order['customer_name'] }}
        </p>

        <p>
            <strong>Table:</strong>
            {{ order['table_number'] }}
        </p>

        <p>
            <strong>Date:</strong>
            {{ order['created_at'] }}
        </p>

        <br>

        <table>

            <tr>
                <th>Item</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Total</th>
            </tr>

            {% for item in items %}

            <tr>

                <td>
                    {{ item['name'] }}
                </td>

                <td>
                    {{ item['quantity'] }}
                </td>

                <td>
                    PKR {{ "{:,.0f}".format(item['price']) }}
                </td>

                <td>
                    PKR {{ "{:,.0f}".format(item['subtotal']) }}
                </td>

            </tr>

            {% endfor %}

        </table>

        <div class="bill-total">

            <strong>
                Grand Total:
                PKR {{ "{:,.0f}".format(order['total']) }}
            </strong>

        </div>

        <br><br>

        <div class="no-print">

            <button
                onclick="window.print()"
                class="btn">
                Print Bill
            </button>

            {% if order['status'] != 'Paid' %}

            <a
                href="/pay-order/{{ order['id'] }}"
                class="btn">
                Mark as Paid
            </a>

            {% endif %}

        </div>

        <br>

        <p style="text-align:center;">
            Thank you for dining with us.
        </p>

    </div>

    """

    return render_page(
        "Restaurant Bill",
        content,
        order=order,
        items=items
    )


# ============================================================
# PAY ORDER
# ============================================================

@app.route("/pay-order/<int:order_id>")
def pay_order(order_id):

    conn = get_db()

    order = conn.execute("""
        SELECT * FROM orders
        WHERE id=?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        return "Order not found", 404

    conn.execute("""
        UPDATE orders
        SET status='Paid'
        WHERE id=?
    """, (order_id,))

    if order["table_id"]:

        conn.execute("""
            UPDATE restaurant_tables
            SET status='Available'
            WHERE id=?
        """, (order["table_id"],))

    conn.commit()
    conn.close()

    flash("Payment received. Table is available again.")

    return redirect(
        url_for("orders")
    )


# ============================================================
# MENU PAGE
# ============================================================

@app.route("/menu")
def menu_page():

    conn = get_db()

    menu = conn.execute("""
        SELECT * FROM menu
        ORDER BY category, name
    """).fetchall()

    conn.close()

    content = """

    <div class="dashboard">

        <h1 class="page-title">
            Royal Haven Menu
        </h1>

        <div class="menu-grid">

            {% for item in menu %}

            <div class="menu-item">

                <div class="menu-top">

                    <h3>
                        {{ item['name'] }}
                    </h3>

                    <span class="price">
                        PKR {{ "{:,.0f}".format(item['price']) }}
                    </span>

                </div>

                <span class="category">
                    {{ item['category'] }}
                </span>

                <p>
                    {{ item['description'] }}
                </p>

            </div>

            {% endfor %}

        </div>

    </div>

    """

    return render_page(
        "Menu",
        content,
        menu=menu
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    init_db()

    print("=" * 60)
    print("ROYAL HAVEN HOTEL POS")
    print("Server running at http://127.0.0.1:5000")
    print("=" * 60)

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
