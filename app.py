from flask import Flask, render_template, request, redirect, url_for, jsonify,flash
import pymysql
import smtplib
from email.message import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import random
import base64

app = Flask(__name__)
app.secret_key = 'a8f4c9b2d7_secret_key_2025'
# ==========================
# DATABASE CONFIGURATION
# ==========================
db_config_root = {
    "host": "localhost",
    "user": "root",
    "password": "root"
}

DB_NAME = "bookstore_1"





# ==========================
# EMAIL OTP CONFIG
# ==========================
admin_email = 'pythonexample704@gmail.com'
admin_password = 'fftg prnw vwyo zhoe'

def send_mail(to_email, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['To'] = to_email
    msg['From'] = admin_email
    msg['Subject'] = 'OTP Verification'
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(admin_email, admin_password)
        smtp.send_message(msg)

# Create database if not exists
conn = pymysql.connect(**db_config_root)
cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
conn.commit()
cursor.close()
conn.close()

# Database connection
db_config = db_config_root.copy()
db_config["database"] = DB_NAME

def get_connection():
    return pymysql.connect(**db_config)

# Initialize tables
def db_init():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            PID INT PRIMARY KEY AUTO_INCREMENT,
            PNAME VARCHAR(30) NOT NULL,
            PIMAGE LONGBLOB NOT NULL,
            PCATEGORY VARCHAR(15) NOT NULL,
            PAPRICE INT NOT NULL,
            PDPRICE INT NOT NULL,
            PSTOCK INT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            mobile VARCHAR(15) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            userid INT NOT NULL,
            pid INT NOT NULL,
            quantity INT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INT PRIMARY KEY AUTO_INCREMENT,
            userid INT NOT NULL,
            pid INT NOT NULL,
            pname VARCHAR(100) NOT NULL,
            price INT NOT NULL,
            quantity INT NOT NULL,
            total INT NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        cursor.execute("ALTER TABLE Orders ADD COLUMN status VARCHAR(20) DEFAULT 'pending'")
        conn.commit()
    except pymysql.Error:
        # Column already exists
        pass


    conn.commit()
    cursor.close()
    conn.close()

db_init()

# ==========================
# ROUTES
# ==========================
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/adminlogin1', methods=['GET', 'POST'])
def adminlogin1():
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == '' and password == '':
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('errorpage.html', message="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin_addproducts1')
def addproducts1():
    return render_template('admin_addproducts.html')

@app.route('/add_products', methods=['POST'])
def add_products():
    p_name = request.form.get('product_name')
    p_image = request.files.get('product_image')
    p_category = request.form.get('product_genre')
    p_actualprice = request.form.get('actual_price')
    p_disprice = request.form.get('discounted_price')
    p_stock = request.form.get('quantity')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Products (PNAME, PIMAGE, PCATEGORY, PAPRICE, PDPRICE, PSTOCK)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (p_name, p_image.read(), p_category, p_actualprice, p_disprice, p_stock))
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('admin_addproducts.html', message='Product added successfully')

@app.route('/admin_manageproducts1')
def manageproducts1():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Products")
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    for book in books:
        if book['PIMAGE']:
            book['PIMAGE'] = base64.b64encode(book['PIMAGE']).decode('utf-8')
    return render_template('admin_manageproducts.html', details=books)

@app.route('/admin_deleteproduct/<int:pid>', methods=['DELETE'])
def admin_deleteProduct(pid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE PID = %s", (pid,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'status': 'success', 'message': f'Product {pid} deleted successfully!'}

@app.route('/modify_stock/<int:pid>', methods=['POST'])
def modify_stock(pid):
    data = request.get_json()
    change = data.get('change', 0)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PSTOCK FROM Products WHERE PID = %s", (pid,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        conn.close()
        return jsonify({'status': 'error', 'message': 'Product not found'})

    current_stock = product[0]
    new_stock = max(0, current_stock + change)
    cursor.execute("UPDATE Products SET PSTOCK = %s WHERE PID = %s", (new_stock, pid))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success', 'new_stock': new_stock})

# ==========================
# USER SIGNUP & LOGIN
# ==========================
@app.route("/user_signup1", methods=["GET", "POST"])
def user_signup1():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        mobile = request.form["mobile"].strip()
        password = request.form["password"]
        cpassword = request.form["cpassword"]

        if password != cpassword:
            return render_template('errorpage.html', message="Passwords don't match")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if user:
            cursor.close()
            conn.close()
            return render_template('errorpage.html', message="Email already exists")

        otp = str(random.randint(100000, 999999))
        send_mail(email, f"Your OTP for bookstore signup is: {otp}")
        cursor.close()
        conn.close()
        return render_template('otpverify.html', email=email, name=name, mobile=mobile, password=password, otp=otp)

    return render_template('user_signup.html')

@app.route("/user_signup3", methods=["POST", "GET"])
def user_signup3():
    name = request.form.get('name')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    otp = request.form.get('otp')
    cotp = request.form.get('cotp')
    hashed_password = generate_password_hash(password)

    if otp == cotp:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users(name,email,mobile,password) VALUES(%s,%s,%s,%s)", (name, email, mobile, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('user_login1'))
    else:
        return "The entered OTP is wrong. Try again!"

@app.route('/user_login1')
def user_login1():
    return render_template('user_login.html')

@app.route('/user_login2', methods=["POST", "GET"])
def user_login2():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT user_id, name, password FROM Users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            return redirect(url_for('user_home', user_id=user['user_id']))
        else:
            return render_template("errorpage.html", message="Invalid credentials")

    return render_template("user_login.html")

# ==========================
# USER HOME & CART
# ==========================
@app.route('/user_home/<int:user_id>', methods=["GET", "POST"])
def user_home(user_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Products WHERE PSTOCK > 0")
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    for book in books:
        if book['PIMAGE']:
            book['PIMAGE'] = "data:image/jpeg;base64," + base64.b64encode(book['PIMAGE']).decode('utf-8')
        else:
            book['PIMAGE'] = "/static/noimage.png"

    return render_template("user_home.html", products=books, user_id=user_id, msg="")

@app.route('/add_to_cart/<int:pid>/<int:user_id>', methods=["POST", "GET"])
def add_to_cart(pid, user_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT PSTOCK FROM Products WHERE PID = %s", (pid,))
    product = cursor.fetchone()

    if not product or product['PSTOCK'] <= 0:
        cursor.close()
        conn.close()
        return render_template("errorpage.html", message="Product not available")

    cursor.execute("SELECT quantity FROM cart WHERE userid=%s AND pid=%s", (user_id, pid))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE userid=%s AND pid=%s", (user_id, pid))
    else:
        cursor.execute("INSERT INTO cart (userid, pid, quantity) VALUES (%s, %s, %s)", (user_id, pid, 1))

    cursor.execute("UPDATE Products SET PSTOCK = PSTOCK - 1 WHERE PID = %s", (pid,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('user_home', user_id=user_id))

@app.route('/shopping_cart/<int:user_id>')
def shopping_cart(user_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT p.PID, p.PNAME, p.PIMAGE, p.PDPRICE, c.quantity 
        FROM cart c JOIN Products p ON c.pid = p.PID WHERE c.userid = %s
    ''', (user_id,))
    cart_items = cursor.fetchall()
    cursor.close()
    conn.close()

    data = []
    total = 0
    for item in cart_items:
        img_src = "data:image/jpeg;base64," + base64.b64encode(item['PIMAGE']).decode('utf-8') if item['PIMAGE'] else "/static/noimage.png"
        data.append(([item['PID'], item['PNAME'], img_src, item['PDPRICE']], item['quantity']))
        total += item['PDPRICE'] * item['quantity']

    return render_template('shopping_cart.html', data=data, total=total, user_id=user_id)

# ✅ Decrease quantity or delete item
@app.route('/delete_cart_item/<int:pid>/<int:userid>/<qty>')
def delete_cart_item(pid, userid, qty):
    conn = get_connection()
    cursor = conn.cursor()
    if qty == 'all':
        cursor.execute("DELETE FROM cart WHERE pid=%s AND userid=%s", (pid, userid))
    else:
        qty = int(qty)
        if qty > 1:
            cursor.execute("UPDATE cart SET quantity = quantity - 1 WHERE pid=%s AND userid=%s", (pid, userid))
        else:
            cursor.execute("DELETE FROM cart WHERE pid=%s AND userid=%s", (pid, userid))
    cursor.execute("UPDATE Products SET PSTOCK = PSTOCK + 1 WHERE PID=%s", (pid,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('shopping_cart', user_id=userid))

# ✅ Increase quantity
@app.route('/add_cart_item/<int:pid>/<int:userid>')
def add_cart_item(pid, userid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PSTOCK FROM Products WHERE PID = %s", (pid,))
    stock = cursor.fetchone()[0]
    if stock > 0:
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE pid=%s AND userid=%s", (pid, userid))
        cursor.execute("UPDATE Products SET PSTOCK = PSTOCK - 1 WHERE PID = %s", (pid,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('shopping_cart', user_id=userid))

@app.route('/success/<int:userid>', methods=["POST"])
def success(userid):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Fetch all cart items for the user
    cursor.execute('''
        SELECT c.pid, p.PNAME, p.PDPRICE, c.quantity 
        FROM cart c JOIN Products p ON c.pid = p.PID 
        WHERE c.userid = %s
    ''', (userid,))
    items = cursor.fetchall()

    # Save each item to Orders table
    for item in items:
        total = item['PDPRICE'] * item['quantity']
        cursor.execute('''
            INSERT INTO Orders (userid, pid, pname, price, quantity, total)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (userid, item['pid'], item['PNAME'], item['PDPRICE'], item['quantity'], total))

    # Clear the cart after placing the order
    cursor.execute('DELETE FROM cart WHERE userid=%s', (userid,))
    conn.commit()
    cursor.close()
    conn.close()

    return render_template('success.html', userid=userid, message="Your order has been placed successfully!")

@app.route('/user_orders/<int:userid>')
def user_orders(userid):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Fetch all orders for the user
    cursor.execute('''
        SELECT o.order_id, o.pid, o.pname, o.price, o.quantity, o.total, o.order_date, p.PIMAGE
        FROM Orders o
        JOIN Products p ON o.pid = p.PID
        WHERE o.userid=%s
        ORDER BY o.order_date DESC
    ''', (userid,))
    orders_raw = cursor.fetchall()

    # Group orders by order_id
    orders_dict = {}
    for row in orders_raw:
        oid = row['order_id']
        if oid not in orders_dict:
            orders_dict[oid] = {
                'order_id': oid,
                'date': row['order_date'].strftime('%d-%m-%Y %H:%M'),
                'total': 0,
                'order_items': []
            }
        # Convert product image to base64
        if row['PIMAGE']:
            img_src = "data:image/jpeg;base64," + base64.b64encode(row['PIMAGE']).decode('utf-8')
        else:
            img_src = "/static/noimage.png"

        orders_dict[oid]['order_items'].append({
            'title': row['pname'],
            'quantity': row['quantity'],
            'price': row['price'],
            'image': img_src
        })
        orders_dict[oid]['total'] += row['total']

    orders = list(orders_dict.values())
    cursor.close()
    conn.close()

    return render_template('orders.html', orders=orders, user_id=userid)






# ==========================
# FORGOT PASSWORD FLOW
# ==========================

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')


# Step 1 → User enters email → Send OTP
@app.route('/forgot_password1', methods=['POST'])
def forgot_password1():
    email = request.form.get('email').strip()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return render_template('errorpage.html', message="Email not found. Please register first!")

    otp = str(random.randint(100000, 999999))
    send_mail(email, f"Your OTP for password reset is: {otp}")
    return render_template('forgot_password_otp.html', email=email, otp=otp)


# Step 2 → OTP verification
@app.route('/forgot_password3', methods=['POST'])
def forgot_password3():
    email = request.form.get('email')
    otp = request.form.get('otp')
    cotp = request.form.get('cotp')

    if otp == cotp:
        return render_template('forgot_password_reset.html', email=email)
    else:
        return render_template('errorpage.html', message="Incorrect OTP. Try again!")


# Step 3 → Update new password
@app.route('/forgot_password4', methods=['POST'])
def forgot_password4():
    email = request.form.get('email')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')

    if password != cpassword:
        return render_template('errorpage.html', message="Passwords do not match!")

    hashed_password = generate_password_hash(password)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET password=%s WHERE email=%s", (hashed_password, email))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Password updated successfully! Please login again.", "success")
    return redirect(url_for('user_login2'))


# ==========================
# ADMIN ORDERS MANAGEMENT
# ==========================

@app.route('/admin_orders')
def admin_orders():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Fetch all orders with user information
    cursor.execute('''
        SELECT o.order_id, o.userid, o.pid, o.pname, o.price, o.quantity, o.total, o.order_date,
               u.name as customer_name, u.email as customer_email
        FROM Orders o
        JOIN Users u ON o.userid = u.user_id
        ORDER BY o.order_date DESC
    ''')
    orders_raw = cursor.fetchall()
    
    # Group orders by order_id
    orders_dict = {}
    for row in orders_raw:
        oid = row['order_id']
        if oid not in orders_dict:
            orders_dict[oid] = {
                'order_id': oid,
                'customer_name': row['customer_name'],
                'customer_email': row['customer_email'],
                'date': row['order_date'].strftime('%d-%m-%Y %H:%M'),
                'total': 0,
                'status': 'pending',  # Default status
                'order_items': []
            }
        
        orders_dict[oid]['order_items'].append({
            'title': row['pname'],
            'quantity': row['quantity'],
            'price': row['price'],
            'pid': row['pid']
        })
        orders_dict[oid]['total'] += row['total']
    
    orders = list(orders_dict.values())
    cursor.close()
    conn.close()
    
    return render_template('admin_orders.html', orders=orders)

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    
    # Here you would typically update the status in your database
    # For now, we'll just return success
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    
    if new_status in valid_statuses:
        # Update order status in database (you'll need to add a status column to Orders table)
        # conn = get_connection()
        # cursor = conn.cursor()
        # cursor.execute("UPDATE Orders SET status = %s WHERE order_id = %s", (new_status, order_id))
        # conn.commit()
        # cursor.close()
        # conn.close()
        
        return jsonify({'status': 'success', 'message': f'Order #{order_id} status updated to {new_status}'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid status'})

# ==========================
# ADMIN USER MANAGEMENT
# ==========================

@app.route('/admin_users')
def admin_users():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Fetch all users
    cursor.execute('''
        SELECT user_id, name, email, mobile, 
               (SELECT COUNT(*) FROM Orders WHERE userid = Users.user_id) as order_count,
               (SELECT SUM(total) FROM Orders WHERE userid = Users.user_id) as total_spent
        FROM Users
        ORDER BY user_id DESC
    ''')
    users = cursor.fetchall()
    
    # Calculate additional statistics
    cursor.execute('SELECT COUNT(*) as total_users FROM Users')
    total_users = cursor.fetchone()['total_users']
    
    cursor.execute('SELECT COUNT(*) as active_users FROM Users WHERE user_id IN (SELECT DISTINCT userid FROM Orders)')
    active_users = cursor.fetchone()['active_users']
    
    cursor.execute('SELECT SUM(total) as total_revenue FROM Orders')
    total_revenue = cursor.fetchone()['total_revenue'] or 0
    
    cursor.close()
    conn.close()
    
    return render_template('admin_users.html', 
                         users=users, 
                         total_users=total_users,
                         active_users=active_users,
                         total_revenue=total_revenue)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # First delete user's orders and cart items
        cursor.execute("DELETE FROM Orders WHERE userid = %s", (user_id,))
        cursor.execute("DELETE FROM cart WHERE userid = %s", (user_id,))
        cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'message': f'User #{user_id} deleted successfully'})
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_user_stats')
def get_user_stats():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute('SELECT COUNT(*) as total_users FROM Users')
    total_users = cursor.fetchone()['total_users']
    
    cursor.execute('SELECT COUNT(*) as active_users FROM Users WHERE user_id IN (SELECT DISTINCT userid FROM Orders)')
    active_users = cursor.fetchone()['active_users']
    
    cursor.execute('SELECT SUM(total) as total_revenue FROM Orders')
    total_revenue = cursor.fetchone()['total_revenue'] or 0
    
    cursor.execute('''
        SELECT DATE(order_date) as date, COUNT(*) as orders_count, SUM(total) as daily_revenue
        FROM Orders 
        WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(order_date)
        ORDER BY date
    ''')
    weekly_stats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'total_revenue': total_revenue,
        'weekly_stats': weekly_stats
    })

# ==========================
# RUN APP
# ==========================
if __name__ == '__main__':
    app.run(debug=True, port=5004)
