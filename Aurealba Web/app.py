from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import sqlite3
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("SECRET_KEY", "aurealba-secret-key-change-in-production")

UPLOAD_FOLDER      = os.path.join("static", "uploads", "avatars")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
app.config["UPLOAD_FOLDER"]      = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── ADMIN CREDENTIALS (change these!) ──
ADMIN_USERNAME = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASS", "tag2025admin")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────

def get_db():
    db = sqlite3.connect("tag.db")
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT    NOT NULL,
                email    TEXT    NOT NULL UNIQUE,
                password TEXT    NOT NULL,
                avatar   TEXT    DEFAULT NULL,
                phone    TEXT    DEFAULT NULL,
                location TEXT    DEFAULT NULL,
                created  DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS contact_messages (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                email   TEXT NOT NULL,
                message TEXT NOT NULL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS orders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                customer   TEXT NOT NULL,
                email      TEXT NOT NULL,
                phone      TEXT DEFAULT '',
                collection TEXT NOT NULL,
                item       TEXT NOT NULL,
                size       TEXT NOT NULL,
                amount     REAL NOT NULL,
                status     TEXT NOT NULL DEFAULT 'pending',
                address    TEXT DEFAULT '',
                notes      TEXT DEFAULT '',
                payment    TEXT DEFAULT 'cod',
                created    DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        for col, defn in [("avatar","TEXT DEFAULT NULL"),("phone","TEXT DEFAULT NULL"),("location","TEXT DEFAULT NULL")]:
            try:
                db.execute(f"ALTER TABLE users ADD COLUMN {col} {defn}")
            except Exception:
                pass

# ─────────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────
# FRONTEND PAGES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    user = None
    if "user_id" in session:
        with get_db() as db:
            user = db.execute("SELECT name FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return render_template("index.html", user=user)

@app.route("/catalog")
def catalog():
    return render_template("catalog.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/casual")
def casual():
    return render_template("casual.html")

@app.route("/party")
def party():
    return render_template("party.html")

@app.route("/office")
def office():
    return render_template("office.html")

@app.route("/traditional")
def traditional():
    return render_template("traditional.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = request.form.get("name","").strip()
        email   = request.form.get("email","").strip()
        message = request.form.get("message","").strip()
        if not all([name, email, message]):
            flash("All fields are required.", "error")
            return render_template("contact.html")
        with get_db() as db:
            db.execute("INSERT INTO contact_messages (name,email,message) VALUES (?,?,?)", (name,email,message))
        flash("Message sent! We'll get back to you soon.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        name     = request.form.get("name","").strip()
        email    = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        confirm  = request.form.get("confirm_password","")
        if not all([name, email, password, confirm]):
            flash("All fields are required.", "error")
            return render_template("signup.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("signup.html")
        with get_db() as db:
            if db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
                flash("An account with that email already exists.", "error")
                return render_template("signup.html")
            db.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                       (name, email, generate_password_hash(password)))
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email    = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"]   = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("index"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for("index"))

# ─────────────────────────────────────────────
# ACCOUNT
# ─────────────────────────────────────────────

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "avatar":
            file = request.files.get("avatar")
            if file and allowed_file(file.filename):
                ext      = file.filename.rsplit(".",1)[1].lower()
                filename = secure_filename(f"user_{session['user_id']}.{ext}")
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                with get_db() as db:
                    db.execute("UPDATE users SET avatar=? WHERE id=?",
                               (f"uploads/avatars/{filename}", session["user_id"]))
                flash("Profile photo updated!", "success")
            else:
                flash("Please upload a valid image.", "error")
        elif action == "profile":
            name     = request.form.get("name","").strip()
            phone    = request.form.get("phone","").strip()
            location = request.form.get("location","").strip()
            if not name:
                flash("Name cannot be empty.", "error")
            else:
                with get_db() as db:
                    db.execute("UPDATE users SET name=?,phone=?,location=? WHERE id=?",
                               (name, phone, location, session["user_id"]))
                session["user_name"] = name
                flash("Profile updated successfully!", "success")
        elif action == "password":
            current = request.form.get("current_password","")
            new_pw  = request.form.get("new_password","")
            confirm = request.form.get("confirm_password","")
            if not check_password_hash(user["password"], current):
                flash("Current password is incorrect.", "error")
            elif new_pw != confirm:
                flash("New passwords do not match.", "error")
            elif len(new_pw) < 6:
                flash("Password must be at least 6 characters.", "error")
            else:
                with get_db() as db:
                    db.execute("UPDATE users SET password=? WHERE id=?",
                               (generate_password_hash(new_pw), session["user_id"]))
                flash("Password changed successfully!", "success")
        return redirect(url_for("account"))
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return render_template("account.html", user=user)

# ─────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────

COLLECTIONS = [
    {"name":"Casual Collection",      "url":"/casual",      "tags":["casual","everyday","relaxed"]},
    {"name":"Party Collection",       "url":"/party",       "tags":["party","glam","night","evening"]},
    {"name":"Office Collection",      "url":"/office",      "tags":["office","work","formal","professional"]},
    {"name":"Traditional Collection", "url":"/traditional", "tags":["traditional","cultural","heritage"]},
]

@app.route("/search")
def search():
    query   = request.args.get("q","").strip().lower()
    results = []
    if query:
        for col in COLLECTIONS:
            if query in col["name"].lower() or any(query in t for t in col["tags"]):
                results.append(col)
    return jsonify(results)


# ─────────────────────────────────────────────
# CART & CHECKOUT
# ─────────────────────────────────────────────

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")

@app.route("/api/place-order", methods=["POST"])
def place_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    required = ["customer", "phone", "address", "collection", "item", "size", "amount"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing {field}"}), 400

    with get_db() as db:
        cur = db.execute("""
            INSERT INTO orders (customer, email, phone, collection, item, size, amount, status, address, notes, payment)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["customer"],
            data.get("email", ""),
            data["phone"],
            data["collection"],
            data["item"],
            data["size"],
            float(data["amount"]),
            "pending",
            data["address"],
            data.get("notes", ""),
            data.get("payment", "cod")
        ))
        order_id = cur.lastrowid

    return jsonify({"success": True, "order_id": order_id})


# ─────────────────────────────────────────────
# PRODUCT DETAIL PAGE
# ─────────────────────────────────────────────

PRODUCT_DATA = {
    "casual": [
        {"name":"Linen Breeze Dress",   "price":3800, "sizes":["XS","S","M","L","XL"],      "emoji":"👗", "collection":"Casual Wear", "description":"A breathable linen dress perfect for warm days. The relaxed silhouette and neutral tones make it effortlessly stylish for brunch, errands, or casual outings."},
        {"name":"Stripe Wrap Top",      "price":2200, "sizes":["S","M","L","XL"],            "emoji":"👚", "collection":"Casual Wear", "description":"A versatile stripe wrap top that pairs beautifully with jeans or trousers. The adjustable tie waist flatters all body types with ease."},
        {"name":"Relaxed Palazzo Set",  "price":4500, "sizes":["S","M","L","XL","XXL"],      "emoji":"👗", "collection":"Casual Wear", "description":"A coordinated palazzo set in flowing fabric. Effortlessly chic for day-to-night dressing with wide-leg trousers and a matching top."},
        {"name":"Floral Midi Skirt",    "price":2900, "sizes":["XS","S","M","L"],            "emoji":"👗", "collection":"Casual Wear", "description":"A feminine floral midi skirt with a flattering A-line cut. Perfect for spring and summer styling with a simple blouse or tucked-in tee."},
        {"name":"Cotton Crop Blouse",   "price":1800, "sizes":["S","M","L"],                 "emoji":"👕", "collection":"Casual Wear", "description":"A lightweight cotton crop blouse with delicate detailing. Pairs effortlessly with high-waist bottoms for a relaxed yet polished look."},
        {"name":"Casual Knit Cardigan", "price":3200, "sizes":["S","M","L","XL"],            "emoji":"🧥", "collection":"Casual Wear", "description":"A cosy knit cardigan in a neutral tone. Layer over any outfit for a warm, stylish finish on cooler days."},
    ],
    "party": [
        {"name":"Sequin Evening Gown",    "price":8500, "sizes":["XS","S","M","L"],          "emoji":"👘", "collection":"Party Wear", "description":"Turn heads in this dazzling sequin evening gown. Full-length glamour with a fitted silhouette designed for unforgettable nights."},
        {"name":"Velvet Wrap Dress",      "price":6200, "sizes":["S","M","L","XL"],          "emoji":"👗", "collection":"Party Wear", "description":"A luxurious velvet wrap dress in a deep jewel tone. The draped neckline and wrap waist create an elegant, figure-flattering look."},
        {"name":"Embellished Crop Top",   "price":3400, "sizes":["XS","S","M","L"],          "emoji":"✨", "collection":"Party Wear", "description":"A show-stopping embellished crop top covered in intricate beading. Style with wide-leg trousers or a sleek skirt for a glamorous ensemble."},
        {"name":"Satin Slip Dress",       "price":5800, "sizes":["XS","S","M","L","XL"],     "emoji":"👗", "collection":"Party Wear", "description":"A sleek satin slip dress with a fluid silhouette and subtle sheen. Minimalist glamour at its finest for cocktail events and dinner parties."},
        {"name":"Ruffle Cocktail Dress",  "price":7200, "sizes":["S","M","L"],               "emoji":"👗", "collection":"Party Wear", "description":"A flirty ruffle cocktail dress with layers of cascading fabric. Feminine and fun — perfect for celebrations and special occasions."},
        {"name":"Glitter Blazer Set",     "price":9000, "sizes":["S","M","L","XL"],          "emoji":"🥂", "collection":"Party Wear", "description":"A bold glitter blazer co-ord set that makes a statement. Wear together for maximum impact or mix and match for versatile party styling."},
    ],
    "office": [
        {"name":"Classic Tailored Blazer",  "price":7800, "sizes":["XS","S","M","L","XL"],  "emoji":"👔", "collection":"Office Wear", "description":"A sharp tailored blazer in a timeless cut. Structured shoulders and clean lines project confidence and professionalism in any boardroom."},
        {"name":"Structured Pencil Skirt",  "price":3500, "sizes":["XS","S","M","L"],        "emoji":"👗", "collection":"Office Wear", "description":"A classic pencil skirt with structured fabric and a comfortable stretch. A wardrobe essential that pairs with blouses and blazers seamlessly."},
        {"name":"Silk Button-Down Blouse",  "price":4200, "sizes":["S","M","L","XL"],        "emoji":"👚", "collection":"Office Wear", "description":"A refined silk button-down blouse with a relaxed yet polished finish. Elevates any work outfit with understated luxury and comfort."},
        {"name":"Wide-Leg Trousers",        "price":4800, "sizes":["S","M","L","XL","XXL"],  "emoji":"👖", "collection":"Office Wear", "description":"Sophisticated wide-leg trousers in a premium fabric. Flattering and comfortable for long work days while maintaining an impeccable silhouette."},
        {"name":"Power Suit Co-ord Set",    "price":11500,"sizes":["S","M","L","XL"],        "emoji":"💼", "collection":"Office Wear", "description":"A commanding power suit co-ord set that means business. Perfectly matched jacket and trousers for a polished, authoritative presence."},
        {"name":"Shift Dress Navy",         "price":5200, "sizes":["XS","S","M","L","XL"],  "emoji":"👗", "collection":"Office Wear", "description":"A timeless navy shift dress with clean lines and a modest hem. Versatile and professional — dress it up with heels or keep it minimal."},
    ],
    "traditional": [
        {"name":"Handloom Saree Gold",     "price":12500,"sizes":["Free Size"],              "emoji":"🥻", "collection":"Traditional Wear", "description":"An exquisite handloom saree with golden thread work. Woven by skilled artisans, this piece celebrates Sri Lankan heritage with regal elegance."},
        {"name":"Batik Wrap Dress",        "price":6800, "sizes":["S","M","L","XL"],         "emoji":"👗", "collection":"Traditional Wear", "description":"A stunning batik wrap dress featuring hand-dyed patterns unique to each piece. A celebration of traditional craft in a modern silhouette."},
        {"name":"Embroidered Salwar Set",  "price":8200, "sizes":["S","M","L","XL","XXL"],   "emoji":"👘", "collection":"Traditional Wear", "description":"An intricately embroidered salwar set with delicate floral motifs. Elegant and comfortable for festive occasions and cultural celebrations."},
        {"name":"Silk Osaria Blouse",      "price":4500, "sizes":["XS","S","M","L"],         "emoji":"🥻", "collection":"Traditional Wear", "description":"A beautifully crafted silk osaria blouse with traditional pleating. Perfect paired with a saree for weddings, Avurudu, and formal events."},
        {"name":"Kandyan Dress Ivory",     "price":15000,"sizes":["XS","S","M","L","XL"],    "emoji":"👰", "collection":"Traditional Wear", "description":"A breathtaking Kandyan bridal dress in pure ivory with gold trim. A symbol of Sri Lankan elegance — ideal for weddings and ceremonial events."},
        {"name":"Lace Jacket Co-ord",      "price":9500, "sizes":["S","M","L","XL"],         "emoji":"🧣", "collection":"Traditional Wear", "description":"A graceful lace jacket co-ord set blending traditional craftsmanship with contemporary styling. Perfect for formal gatherings and cultural events."},
    ],
}

@app.route("/product/<collection>/<int:index>")
def product_detail(collection, index):
    products = PRODUCT_DATA.get(collection)
    if not products or index >= len(products):
        return redirect(url_for(collection if collection in ["casual","party","office","traditional"] else "index"))
    product = products[index]
    return render_template("product.html", product=product)

# ─────────────────────────────────────────────
# ADMIN AUTH
# ─────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))

# ─────────────────────────────────────────────
# ADMIN DASHBOARD PAGE
# ─────────────────────────────────────────────

@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")

# ─────────────────────────────────────────────
# ADMIN API — STATS
# ─────────────────────────────────────────────

@app.route("/admin/api/stats")
@admin_required
def api_stats():
    with get_db() as db:
        total_orders = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        revenue      = db.execute("SELECT COALESCE(SUM(amount),0) FROM orders WHERE status!='cancelled'").fetchone()[0]
        customers    = db.execute("SELECT COUNT(DISTINCT email) FROM users").fetchone()[0]
        pending      = db.execute("SELECT COUNT(*) FROM orders WHERE status='pending'").fetchone()[0]
        processing   = db.execute("SELECT COUNT(*) FROM orders WHERE status='processing'").fetchone()[0]
        delivered    = db.execute("SELECT COUNT(*) FROM orders WHERE status='delivered'").fetchone()[0]
        cancelled    = db.execute("SELECT COUNT(*) FROM orders WHERE status='cancelled'").fetchone()[0]
    return jsonify({"total_orders":total_orders,"total_revenue":round(revenue,2),"total_customers":customers,
                    "pending_orders":pending,"processing_orders":processing,"delivered_orders":delivered,"cancelled_orders":cancelled})

# ─────────────────────────────────────────────
# ADMIN API — ORDERS
# ─────────────────────────────────────────────

@app.route("/admin/api/orders", methods=["GET"])
@admin_required
def api_orders():
    with get_db() as db:
        rows = db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    return jsonify({"orders": [dict(r) for r in rows]})

@app.route("/admin/api/orders", methods=["POST"])
@admin_required
def api_create_order():
    data     = request.get_json()
    required = ["customer","email","collection","item","size","amount"]
    if not all(data.get(k) for k in required):
        return jsonify({"error":"Missing required fields"}), 400
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO orders (customer,email,phone,collection,item,size,amount,status,address,notes) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (data["customer"],data["email"],data.get("phone",""),data["collection"],
             data["item"],data["size"],float(data["amount"]),
             data.get("status","pending"),data.get("address",""),data.get("notes",""))
        )
        order = db.execute("SELECT * FROM orders WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(order)), 201

@app.route("/admin/api/orders/<int:order_id>", methods=["PATCH"])
@admin_required
def api_update_order(order_id):
    data    = request.get_json()
    allowed = ["status","customer","email","phone","collection","item","size","amount","address","notes"]
    fields  = {k:v for k,v in data.items() if k in allowed}
    if not fields:
        return jsonify({"error":"Nothing to update"}), 400
    set_clause = ", ".join(f"{k}=?" for k in fields)
    with get_db() as db:
        db.execute(f"UPDATE orders SET {set_clause} WHERE id=?", list(fields.values())+[order_id])
        order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    return jsonify(dict(order)) if order else (jsonify({"error":"Not found"}), 404)

@app.route("/admin/api/orders/<int:order_id>", methods=["DELETE"])
@admin_required
def api_delete_order(order_id):
    with get_db() as db:
        db.execute("DELETE FROM orders WHERE id=?", (order_id,))
    return jsonify({"deleted":True})

# ─────────────────────────────────────────────
# ADMIN API — CUSTOMERS & MESSAGES
# ─────────────────────────────────────────────

@app.route("/admin/api/customers")
@admin_required
def api_customers():
    with get_db() as db:
        users = db.execute("SELECT id,name,email,phone,location,created FROM users ORDER BY id DESC").fetchall()
        result = []
        for u in users:
            u = dict(u)
            row = db.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(amount),0) as total FROM orders WHERE email=?",
                             (u["email"],)).fetchone()
            u["order_count"] = row["cnt"]
            u["total_spent"] = round(row["total"],2)
            result.append(u)
    return jsonify({"customers": result})

@app.route("/admin/api/messages")
@admin_required
def api_messages():
    with get_db() as db:
        rows = db.execute("SELECT * FROM contact_messages ORDER BY id DESC").fetchall()
    return jsonify({"messages": [dict(r) for r in rows]})

@app.route("/admin/api/category-stats")
@admin_required
def api_category_stats():
    with get_db() as db:
        rows = db.execute("SELECT collection, COUNT(*) as cnt, COALESCE(SUM(amount),0) as total FROM orders GROUP BY collection").fetchall()
    return jsonify([dict(r) for r in rows])

# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True)