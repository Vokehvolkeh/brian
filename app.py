from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
import traceback
from flask import jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

import psycopg2
from psycopg2.extras import RealDictCursor



import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    conn = psycopg2.connect(
        host='ep-patient-block-abdjeaq8-pooler.eu-west-2.aws.neon.tech',
        port=5432,  # Neon default port
        database='neondb',
        user='neondb_owner',
        password='npg_jBNm9luTR4Pi',
        sslmode='require',
        target_session_attrs='read-write',
        cursor_factory=RealDictCursor
    )
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS furniture (
            item_id SERIAL PRIMARY KEY ,
            name TEXT,
            quantity SERIAL,
            selling_price REAL,
            buying_price REAL,
            image_path TEXT
        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS damaged_info (
            id SERIAL PRIMARY KEY ,
            date TEXT,
            name TEXT,
            quantity REAL,
            buying_price REAL,
            selling_price REAL,
            loss REAL,
            reason TEXT
        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS stock_info (
            item_id SERIAL PRIMARY KEY ,
            date TEXT,
            supplier_name TEXT,
            supplier_contact TEXT,
            item_name TEXT,
            quantity REAL,
            selling_price REAL,
            buying_price REAL,
            status REAL
        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS members (
            id SERIAL PRIMARY KEY ,
            name TEXT,
            phone TEXT,
            role TEXT,
            company_id SERIAL,
            status TEXT,
            email TEXT,
            profile_photo TEXT
        );''')

    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id SERIAL PRIMARY KEY,        -- Auto-increment unique ID for each sale
            item_id INTEGER NOT NULL,          -- References item from stock_info
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,         -- Quantity sold
            selling_price NUMERIC(10, 2) NOT NULL,  -- More precise than REAL for money
            buying_price NUMERIC(10, 2) NOT NULL,
            payment TEXT,
            profit_or_loss NUMERIC(10, 2),
            date DATE NOT NULL
        );
    """)

    c.execute('''CREATE TABLE IF NOT EXISTS meetings (
            id SERIAL PRIMARY KEY ,
            title TEXT,
            date TEXT,
            time TEXT
        );''')

    c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY ,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                profile_photo TEXT,
                email TEXT,
                phone TEXT
            );
        ''')


    c.execute('''CREATE TABLE IF NOT EXISTS quotations (
            id SERIAL PRIMARY KEY ,
            customer_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY ,
            customer_name TEXT,
            total_price SERIAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS invoice_items (
        id SERIAL PRIMARY KEY,
        item_type TEXT NOT NULL,
        invoice_id INT,
        item_quantity INT NOT NULL,
        selling_price NUMERIC(10,2),
        is_paid BOOLEAN DEFAULT FALSE,
        status TEXT DEFAULT 'not paid',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')


    c.execute('''CREATE TABLE IF NOT EXISTS quotations_items (
            id SERIAL PRIMARY KEY ,
            quotation_id SERIAL,
            item_type TEXT,
            quantity SERIAL,
            price REAL,
            total REAL
        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS cashflow (
            id SERIAL PRIMARY KEY ,
            start_date TEXT,
            end_date TEXT,
            inflow TEXT,
            outflow TEXT,
            expenses TEXT,
            investments REAL,
            financial REAL,
            total_outflow REAL,
            net_cashflow REAL,
            notes TEXT
        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY ,
            start_date DATE ,
            end_date DATE,
            salaries REAL,
            cost_of_good REAL,
            electricity REAL,
            water REAL,
            internet REAL,
            rent REAL,
            supplies REAL,
            ads REAL,
            insuarance REAL,
            maintanance REAL,
            transport REAL,
            taxes REAL,
            total_expenses REAL
        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS salaries (
            id SERIAL PRIMARY KEY ,
            date TEXT,
            employee_id SERIAL,
            salary REAL,
            status TEXT
        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS contracts (
            id SERIAL PRIMARY KEY ,
            title TEXT,
            description TEXT,
            status TEXT,
            client_name TEXT,
            client_contact TEXT,
            contract_amount REAL,
            date_assigned TEXT
        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS contract_expenses (
            id SERIAL PRIMARY KEY ,
            contract_id SERIAL,
            date TEXT,
            workers REAL,
            materials REAL,
            others REAL,
            balance REAL,
            profit_or_loss REAL,
            daily_outflow REAL
        );''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY ,
                staff_id TEXT,
                member TEXT, date TEXT,
                check_in_time TEXT,
                check_out_time TEXT, 
                lateness_minutes TEXT,
                early_leave_minutes TEXT, 
                worked_hours TEXT, 
                status TEXT,
                attendance_rate TEXT
    );
''')
    c.execute('''CREATE TABLE IF NOT EXISTS policy (
                  id  SERIAL PRIMARY KEY ,
                time_in TEXT,
                time_out TEXT,
                email TEXT,
                address TEXT,
                  phone TEXT
                  )''')
    c.execute('''CREATE TABLE IF NOT EXISTS respo (
                id SERIAL PRIMARY KEY ,
                name TEXT,
                company_id TEXT,
                respo TEXT,
                tasks TEXT,
                remarks TEXT,
                  description TEXT,
                  date_assigned TEXT,
                  date_checked TEXT
            );
            ''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY ,
            key TEXT,
            value TEXT
        );
        ''')




app = Flask(__name__)
app.secret_key = 'supersecret'

#initialize africastalking 


# Africa's Talking setup


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    import re

    def normalize_kenyan_number(number):
        number = re.sub(r'\D', '', number.strip())  # Remove non-digit chars
        if number.startswith('0') and len(number) == 10:
            return '+254' + number[1:]
        elif number.startswith('254') and len(number) == 12:
            return '+' + number
        elif number.startswith('+254') and len(number) == 13:
            return number
        else:
            return None

    conn = get_connection()
    c = conn.cursor()

    current_data = {
        'time_in': '',
        'time_out': '',
        'email': '',
        'address': '',
        'phone': ''
    }

    # Fetch users (always needed for rendering the page)
    c.execute("SELECT id, username, email, phone, profile_photo FROM users")
    users = c.fetchall()
    user_list = [
        {
            'id': user['id'], # type: ignore
            'username': user['username'], # type: ignore
            'email': user['email'], # type: ignore
            'phone': user['phone'], # type: ignore
            'profile_photo': user['profile_photo'] # type: ignore
        }
        for user in users
    ]

    if request.method == 'POST':
        time_in = request.form['time_in'].strip()
        time_out = request.form['time_out'].strip()
        email = request.form['email'].strip()
        address = request.form['address'].strip()
        phone_raw = request.form['phone'].strip()

        # Normalize phone number
        phone = normalize_kenyan_number(phone_raw)

        if not phone:
            flash('❌ Invalid phone number format. Use 0712345678 or +254...', 'danger')
            return render_template('settings.html', data=current_data, users=user_list)

        try:
            c.execute('SELECT id FROM policy LIMIT 1')
            existing = c.fetchone()

            if existing:
                c.execute('''
                    UPDATE policy
                    SET time_in = %s, time_out = %s, email = %s, address = %s, phone = %s
                    WHERE id = %s
                ''', (time_in, time_out, email, address, phone, existing[0]))
            else:
                c.execute('''
                    INSERT INTO policy (time_in, time_out, email, address, phone)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (time_in, time_out, email, address, phone))

            conn.commit()
            flash('✅ Settings updated successfully!', 'success')

        except Exception as e:
            conn.rollback()
            flash(f'❌ Error: {str(e)}', 'danger')

    # Always fetch current data
    c.execute('SELECT time_in, time_out, email, address, phone FROM policy LIMIT 1')
    row = c.fetchone()
    if row:
        current_data = {
            'time_in': row[0],
            'time_out': row[1],
            'email': row[2],
            'address': row[3],
            'phone': row[4]
        }

    conn.close()
    return render_template('settings.html', data=current_data, users=user_list)









@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('allow_reset'):
        flash("⛔ Unauthorized access", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        current_pass = request.form['current_password']
        new_pass = request.form['new_password']
        confirm_pass = request.form['confirm_password']

        # Check if new and confirm match
        if new_pass != confirm_pass:
            flash("❌ New passwords do not match", "danger")
            return redirect(url_for('reset_password'))

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = %s", (username,))
        row = c.fetchone()

        if not row:
            flash("❌ User not found", "danger")
            return redirect(url_for('reset_password'))

        stored_hash = row[0]
        if not check_password_hash(stored_hash, current_pass):
            flash("❌ Incorrect current password", "danger")
            return redirect(url_for('reset_password'))

        # Save new password
        new_hash = generate_password_hash(new_pass)
        c.execute("UPDATE users SET password = %s WHERE username = %s", (new_hash, username))
        conn.commit()
        conn.close()

        session.pop('allow_reset', None)
        flash(f"✅ Password successfully updated for {username}", "success")
        return redirect(url_for('login'))

    return render_template('reset.html')

#attendance


from flask import jsonify



@app.route('/check_in', methods=['POST'])
def check_in():
    staff_id = request.form['id']
    date = datetime.today().strftime('%d-%m-%Y')
    time_in = datetime.today().strftime('%H:%M:%S')

    conn = get_connection()
    c = conn.cursor()

    # Check if already checked in today
    c.execute('SELECT * FROM attendance WHERE staff_id = %s AND date = %s', (staff_id, date))
    already_checked = c.fetchone()
    if already_checked:
        conn.close()
        return jsonify({"status": "error", "message": "Already checked in today"}), 400

    # Get the staff name from users table
    c.execute('SELECT username FROM users WHERE id = %s', (staff_id,))
    user_row = c.fetchone()
    member_name = user_row['name'] if user_row else 'Unknown' # type: ignore

    # Insert check-in
    c.execute('''
        INSERT INTO attendance (staff_id, member, date, check_in_time, status)
        VALUES (%s, %s, %s, %s, %s)
    ''', (staff_id, member_name, date, time_in, 'Checked In'))
    conn.commit()

    # Fetch phone number from policy table

    return jsonify({"status": "success", "time_in": time_in})


from flask import jsonify

@app.route('/check_out', methods=['POST'])
def check_out():
    staff_id = request.form['id']
    date = datetime.today().strftime('%d-%m-%Y')
    time_out = datetime.today().strftime('%H:%M:%S')
    conn = get_connection()
    c = conn.cursor()

    c.execute('SELECT check_in_time FROM attendance WHERE staff_id = %s AND date = %s', (staff_id, date))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Check-in not found for today."}), 400

    time_in = row['check_in_time'] # type: ignore

    # Get policy
    c.execute('SELECT time_in, time_out FROM policy')
    policy_row = c.fetchone()
    if not policy_row:
        expected_in = datetime.strptime('08:00:00', '%H:%M:%S')
        expected_out = datetime.strptime('17:00:00', '%H:%M:%S')
    else:
        expected_in = datetime.strptime(policy_row[0], '%H:%M:%S')
        expected_out = datetime.strptime(policy_row[1], '%H:%M:%S')

    actual_in = datetime.strptime(time_in, '%H:%M:%S')
    actual_out = datetime.strptime(time_out, '%H:%M:%S')

    lateness = max(0, round((actual_in - expected_in).total_seconds() / 60))
    early_leave = max(0, round((expected_out - actual_out).total_seconds() / 60)) if actual_out < expected_out else 0
    worked_hours = max(0, round((actual_out - actual_in).total_seconds() / 3600, 2))

    status = 'Present' if lateness <= 30 else 'Late'
    if worked_hours == 0:
        status = 'Absent'

    c.execute('SELECT COUNT(*) FROM attendance WHERE staff_id = %s', (staff_id,))
    row = c.fetchone()
    if row:
        total_days = row['id'] # type: ignore

    c.execute('SELECT COUNT(*) FROM attendance WHERE staff_id = %s AND status IN ("Present", "Late")', (staff_id,))
    days = c.fetchone()
    if days:
        present_days = days['id'] # type: ignore
    attendance_rate = round((present_days / total_days) * 100, 2) if total_days else 0.0

    c.execute('''
        UPDATE attendance
        SET check_out_time = %s, lateness_minutes = %s, early_leave_minutes = %s, 
            worked_hours = %s, status = %s, attendance_rate = %s
        WHERE staff_id = %s AND date = %s
    ''', (time_out, lateness, early_leave, worked_hours, status, attendance_rate, staff_id, date))

    conn.commit()
    conn.close()

    # SMS (optional)


    return jsonify({
        "status": "success",
        "check_out_time": time_out,
        "worked_hours": worked_hours,
        "status_text": status,
        "attendance_rate": attendance_rate
    })

from flask import render_template
from datetime import datetime

@app.route('/attendance_view')
def attendance_view():
    conn = get_connection()
    c = conn.cursor()

    today = datetime.today().strftime('%d-%m-%Y')

    # Fetch all members
    c.execute('SELECT name, company_id FROM members')
    all_members = c.fetchall()

    # Fetch today’s attendance
    c.execute('SELECT * FROM attendance WHERE date = %s', (today,))
    attendance_raw = c.fetchall()

    # Convert attendance rows to a dictionary by staff_id
    attendance_data = {}
    for row in attendance_raw:
        # Map the columns by index (adjust depending on your schema)
        attendance_data[row['id']] = { # type: ignore
            'check_in_time': row['check_in_time'], # type: ignore
            'check_out_time': row['check_out_time'], # type: ignore
            'worked_hours': row['worked_hours'], # type: ignore
            'status': row['status'] # type: ignore
        }

    # Merge members and today's attendance
    table_data = []
    for member in all_members: 
        staff_id = member['name']  # type: ignore # company_id
        attendance_row = attendance_data.get(staff_id)

        row = {
            'staff_id': staff_id,
            'member': member['name'],  # name # type: ignore
            'check_in_time': attendance_row['check_in_time'] if attendance_row else '—',
            'check_out_time': attendance_row['check_out_time'] if attendance_row else '—',
            'worked_hours': attendance_row['worked_hours'] if attendance_row else '—',
            'status': attendance_row['status'] if attendance_row else '—'
        }
        table_data.append(row)

    conn.close()
    return render_template('members.html', today=today, today_attendance=table_data)



 

# Attendance route (GET only with staff_id from URL)
import json
@app.route('/available_members')
def available_members():
    today = datetime.today().strftime('%Y-%m-%d')
    conn = get_connection()
    c = conn.cursor()

    # Get members who have NOT checked in today
    c.execute('''
        SELECT name, company_id FROM members
        WHERE company_id NOT IN (
            SELECT staff_id FROM attendance WHERE date = %s
        )
    ''', (today,))
    members = c.fetchall()
    conn.close()
    return jsonify(members)

@app.route('/check_in_member', methods=['POST'])
def check_in_member():
    if not request.is_json:
        return jsonify({"error": "Request content-type must be application/json"}), 415

    data = request.get_json()
    staff_id = data.get('staff_id')
    name = data.get('name')

    if not staff_id or not name:
        return jsonify({"error": "Missing data"}), 400

    time_in = datetime.now().strftime('%H:%M:%S')
    date = datetime.today().strftime('%Y-%m-%d')

    conn = get_connection()
    c = conn.cursor()

    # Fetch expected time from policy
    c.execute('SELECT time_in FROM policy')
    policy_row = c.fetchone()
    expected_time = policy_row[0] if policy_row else '08:00:00'

    # Calculate lateness
    expected = datetime.strptime(expected_time, "%H:%M:%S")
    actual = datetime.strptime(time_in, "%H:%M:%S")
    late_minutes = max(0, int((actual - expected).total_seconds() // 60))

    # Insert into attendance table
    c.execute('''
        INSERT INTO attendance (member, staff_id, date, check_in_time, lateness_minutes, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (name, staff_id, date, time_in, late_minutes, "present"))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"{name} checked in successfully at {time_in}",
        "late_minutes": late_minutes
    })

#navigate to business summary
@app.route('/business_summary')
def business_summary():
    return render_template('new_dashboard.html')
#add damaged info

from flask import Flask, request, redirect, url_for, render_template, flash
import sqlite3


from flask import flash, get_flashed_messages

@app.route('/create_user', methods=['GET', 'POST'])
def register():
    conn = get_connection()
    c = conn.cursor()

    # Count existing users
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()
    user_count = list(count.values())[0] if isinstance(count, dict) else (count[0] if count else 0)

    if user_count >= 3:
        conn.close()
        flash("⚠️ Maximum number of users already registered.", "error")
        return redirect(url_for('settings'))   # redirect instead of plain text

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash("❌ Passwords do not match!", "error")
            return redirect(url_for('register'))
            
        email = request.form['email']
        phone = request.form['phone']
        photo = request.files['profile_photo']

        profile_photo_path = None
        if photo and photo.filename and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            profile_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(profile_photo_path)

        hashed_password = generate_password_hash(password)

        try:
            c.execute(
                'INSERT INTO users (username, password, profile_photo, email, phone) VALUES (%s, %s, %s, %s, %s)',
                (username, hashed_password, profile_photo_path, email, phone)
            )
            conn.commit()
            conn.close()
            flash("✅ User created successfully!", "success")
            return redirect(url_for('normal_user'))
        except psycopg2.IntegrityError:
            conn.rollback()
            conn.close()
            flash("⚠️ Username already taken.", "error")
            return redirect(url_for('register'))

    conn.close()
    return render_template('create_user.html')


from werkzeug.security import check_password_hash



@app.route('/', methods=['GET', 'POST'])  # Login
def normal_user():
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        c.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = c.fetchone()

        if user:
            try:
                # Try dictionary access first (for DB adapters that return dicts)
                if hasattr(user, 'keys'):  # Check if it's dict-like
                    stored_hash = user['password'] # type: ignore
                    user_id = user['id'] # type: ignore
                else:  # Assume it's a tuple/sequence
                    stored_hash = user[2]  # password at index 2
                    user_id = user[0]     # id at index 0
            except (KeyError, IndexError, TypeError) as e:
                conn.close()
                app.logger.error(f"Database access error: {str(e)}")
                return "Login system error", 500

            if check_password_hash(stored_hash, password):
                session['user_id'] = user_id
                session['username'] = username
                conn.close()
                return redirect(url_for('dashboard'))
            else:
                conn.close()
                flash('Invalid password', 'error')
                return redirect(url_for('normal_user'))
        else:
            conn.close()
            flash('User not found', 'error')
            return redirect(url_for('normal_user'))

    conn.close()
    return render_template('login.html')

#Edit user info@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = get_connection()
    c = conn.cursor()

    # Fetch user info to pre-fill form
    c.execute('SELECT username, email, phone, profile_photo FROM users WHERE id = %s', (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        return "User not found."

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']

        # Password update is optional
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        hashed_password = None
        if password:
            if password != confirm_password:
                conn.close()
                return "Passwords do not match."
            hashed_password = generate_password_hash(password)

        # Handle profile photo
        photo = request.files.get('profile_photo')
        profile_photo_path = user[3]  # keep old path unless new uploaded
        if photo and photo.filename and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            profile_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(profile_photo_path)

        try:
            if hashed_password:
                c.execute('''
                    UPDATE users 
                    SET username=%s, password=%s, email=%s, phone=%s, profile_photo=%s
                    WHERE id=%s
                ''', (username, hashed_password, email, phone, profile_photo_path, user_id))
            else:
                c.execute('''
                    UPDATE users 
                    SET username=%s, email=%s, phone=%s, profile_photo=%s
                    WHERE id=%s
                ''', (username, email, phone, profile_photo_path, user_id))

            conn.commit()
            conn.close()
            return redirect(url_for('normal_user'))  # send back to dashboard or list
        except psycopg2.IntegrityError:
            conn.close()
            return "Username already taken."

    conn.close()
    return render_template('create_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_connection()
    c = conn.cursor()

    try:
        # Delete user by id
        c.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User deleted successfully."})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/add_damagedinfo', methods=['GET', 'POST'])
def add_damagedinfo():
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()

        if request.method == 'POST':
            date = datetime.today().strftime('%Y-%m-%d')
            
            # Handle product_id with error checking
            try:
                product_id = int(request.form['product_id'])
            except (ValueError, KeyError):
                flash("Invalid product selection", "error")
                return redirect(url_for('add_damagedinfo'))

            # Handle quantity with better error checking
            try:
                quantity = int(request.form.get('quantity', '1'))
                if quantity <= 0:
                    flash("Quantity must be a positive number", "error")
                    return redirect(url_for('add_damagedinfo'))
            except ValueError:
                flash("Invalid quantity value", "error")
                return redirect(url_for('add_damagedinfo'))

            # Handle selling price
            try:
                selling_price = float(request.form.get('selling_price', 0))
            except ValueError:
                selling_price = 0.0

            reason = request.form.get('reason', '')

            # Fetch product info with explicit column selection
            c.execute('SELECT quantity, buying_price, item_name FROM stock_info WHERE item_id = %s', (product_id,))
            result = c.fetchone()

            if not result:
                flash("Product not found.", "error")
                return redirect(url_for('add_damagedinfo'))

            # Convert all numeric values safely
            try:
                stock_quantity = int(result['quantity']) # type: ignore
                buying_price = float(result['buying_price']) # type: ignore
                product_name = str(result['item_name']) # type: ignore
            except (ValueError, TypeError, IndexError) as e:
                flash("Invalid product data in database", "error")
                return redirect(url_for('add_damagedinfo'))

            if stock_quantity < quantity:
                flash(f"Only {stock_quantity} items available in stock.", "error")
                return redirect(url_for('add_damagedinfo'))

            # Calculate loss
            loss = (buying_price - selling_price) * quantity

            # Record damaged stock
            c.execute('''INSERT INTO damaged_info
                         (id, date, name, quantity, buying_price, selling_price, loss, reason)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                      (product_id, date, product_name, quantity, buying_price, selling_price, loss, reason))

            # Update stock
            c.execute('UPDATE stock_info SET quantity = quantity - %s WHERE item_id = %s', (quantity, product_id))

            conn.commit()
            flash("Damaged stock recorded successfully!", "success")
            
            # SMS Notification (optional)


            return redirect(url_for('view_damagedinfo'))

        # GET request - show form
        c.execute('SELECT item_id, item_name FROM stock_info ORDER BY item_name')
        products = c.fetchall()
        return render_template('add_damagedinfo.html', products=products, button_text='Record Damaged Info')

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('add_damagedinfo'))
    finally:
        if conn:
            conn.close()


#view damaged_info
@app.route('/view_damagedinfo')
def view_damagedinfo():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM damaged_info')
    damagedinfo = c.fetchall()
    conn.commit()
    conn.close()
    return render_template('view_damagedinfo.html', damagedinfo=damagedinfo)

@app.route('/edit_damagedinfo/<int:id>', methods=['GET', 'POST'])
def edit_damagedinfo(id):
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(float(request.form['quantity'] or 1))
        selling_price = float(request.form['selling_price'] or 0)
        reason = request.form['reason']
        c.execute('SELECT quantity, buying_price, item_name FROM stock_info WHERE item_id = %s', (product_id,))
        result = c.fetchone()

        if not result:
            flash("Product not found.", "error")
            return redirect(url_for('edit_damagedinfo'))

            # Convert all numeric values safely
        try:
                stock_quantity = int(result['quantity']) # type: ignore
                buying_price = float(result['buying_price']) # type: ignore
                product_name = str(result['item_name']) # type: ignore
        except (ValueError, TypeError, IndexError) as e:
            flash("Invalid product data in database", "error")
            return redirect(url_for('edit_damagedinfo'))

        if stock_quantity < int(quantity):
                flash(f"Only {stock_quantity} items available in stock.", "error")
                return redirect(url_for('edit_damagedinfo'))

            # Calculate loss
        loss = (buying_price - selling_price) * quantity



        # Fixed: Make sure the columns and values align exactly
        c.execute('''
            UPDATE damaged_info 
            SET name = %s, quantity = %s, buying_price = %s, selling_price = %s, loss = %s, reason = %s
            WHERE id = %s
        ''', (product_name, quantity, buying_price, selling_price, loss, reason, id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_damagedinfo'))

    else:
        c.execute('SELECT * FROM damaged_info WHERE id = %s', (id,))
        damaged_item = c.fetchone()
        conn.close()

        if damaged_item:
            product = {
                'id': damaged_item['id'], # type: ignore
                'date': damaged_item['date'], # type: ignore
                'name': damaged_item['name'], # type: ignore
                'quantity': damaged_item['quantity'], # type: ignore
                'buying_price': damaged_item['buying_price'], # type: ignore
                'selling_price': damaged_item['selling_price'], # type: ignore
                'loss': damaged_item['loss'], # type: ignore
                'reason': damaged_item['reason'] # type: ignore
            }
        else:
            product = None


        return render_template('add_damagedinfo.html', product=product, form_action=url_for('edit_damagedinfo', id=id), button_text='Update Damaged Info')


#delete damagedinfo
@app.route('/delete_damagedinfo/<int:id>')
def delete_damagedinfo(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM damaged_info WHERE id = %s', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_damagedinfo'))

# ADD SALARY
@app.route('/add_salary', methods=['GET', 'POST'])
def add_salary():
    if request.method == 'POST':
        date = datetime.today().strftime('%Y-%m-%d')
        employee_id = request.form['employee_id']
        salary_amount = request.form['salary_amount']
        status = request.form['status']

        conn = get_connection()
        cursor = conn.cursor()

        # Check if employee exists
        cursor.execute('SELECT name FROM members WHERE company_id = %s', (employee_id,))
        member = cursor.fetchone()

        if not member:
            flash("No member with that ID, or not yet registered", "error")
            conn.close()
            return redirect(url_for('add_salary'))

        # If using RealDictCursor
        employee_name = member['name'] if isinstance(member, dict) else member[0] # type: ignore

        # Insert salary record
        cursor.execute('''
            INSERT INTO salaries (date, employee_id, name, salary, status)
            VALUES (%s, %s, %s, %s, %s)
        ''', (date, employee_id, employee_name, salary_amount, status))

        conn.commit()
        conn.close()

        # Send SMS notification


        return redirect(url_for('view_salary'))

    return render_template('salaries.html')


# VIEW SALARY
@app.route('/view_salary')
def view_salary():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM salaries')
    salaries = c.fetchall()
    conn.close()  # fixed
    return render_template('payrolls.html', salaries=salaries, salary=None)

#generate payslip
@app.route('/generate_payslip', methods=['GET', 'POST'])
def generate_payslip():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        member_id = request.form['member_id']
        bank_name = request.form['bank_name']
        payment_date = datetime.today().strftime('%Y-%m-%d')
        allowance = float(request.form['allowance'] or 0)
        overtime = float(request.form['overtime'] or 0)
        commission = float(request.form['commission'] or 0)
        bonus = float(request.form['bonus'] or  0) 
        leave_pay = float(request.form['leave_pay'] or 0)
        paye = float(request.form['paye'] or 0 )
        nhif = float(request.form['nhif'] or 0)
        advance = float(request.form['advance_loan'] or 0)
        others = float(request.form['others'] or 0 )

        # Get member info + salary
        cursor.execute("""
            SELECT members.name, salaries.salary
            FROM salaries
            JOIN members ON salaries.employee_id = members.id
            WHERE members.id = %s
            ORDER BY salaries.date DESC
            LIMIT 1
        """, (member_id,))
        data = cursor.fetchone()

        if data:
            name, basic_salary = data
            total_earnings = basic_salary + bonus + overtime + allowance + commission + leave_pay
            total_deductions = paye + others + advance + nhif
            net_pay = total_earnings - total_deductions



            return render_template('payrolls.html', name=name, member_id=member_id, payment_date=payment_date,
                                   allowance=allowance, commission=commission, basic_salary=basic_salary,
                                   bonus=bonus, total_earnings=total_earnings, nhif=nhif, advance=advance,
                                   bank_name=bank_name, paye=paye, others=others, overtime=overtime,
                                   total_deductions=total_deductions, net_pay=net_pay)
        else:
            message = "Member ID not found or no salary available."
            return render_template('generate_payslip.html', message=message)

    conn.close()
    return render_template('generate_payslip.html')

# Edit Salary Route
@app.route('/edit_salary/<int:id>', methods=['GET', 'POST'])  # FIXED: closing angle bracket
def edit_salary(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_salary = request.form['salary_amount']
        new_status = request.form['status']
        cursor.execute('UPDATE salaries SET salary = %s, status = %s WHERE id = %s', (new_salary, new_status, id))
        conn.commit()
        conn.close()
        return redirect('/payrolls')  
    
    cursor.execute('SELECT * FROM salaries WHERE id = %s', (id,))
    salary = cursor.fetchone()
    conn.close()


    return render_template('salaries.html', salary=salary, salaries=None)  # FIXED: Use correct template and pass data


# ROUTES

#navigate from dashboard to payrolss
@app.route('/payrolls')
def payrolls():
    return render_template('payrolls.html')
@app.route('/')
def index():
    return redirect('/login')
from flask import Flask, request, redirect, url_for, render_template, session, flash
from werkzeug.security import check_password_hash







@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        flash("You must be logged in to change your password.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['user']
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(url_for('change_password'))

        # Fetch current hashed password from DB
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = c.fetchone()

        if not result or not check_password_hash(result[0], current_password):
            flash("Current password is incorrect.")
            conn.close()
            return redirect(url_for('change_password'))

        # Hash and update new password
        new_hashed = generate_password_hash(new_password)
        c.execute("UPDATE users SET password = %s WHERE username = %s", (new_hashed, username))
        conn.commit()
        conn.close()

        flash("Password changed successfully.")
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')


#CASH FLOW SYSTEM


@app.route('/edit_expense/<int:id>', methods=['POST', 'GET'])
def edit_expense(id):
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        electricity = float(request.form['electricity'])
        water = float(request.form['water'])
        internet = float(request.form['internet'])
        rent = float(request.form['rent'])
        supplies = float(request.form['supplies'])
        ads = float(request.form['ads'])
        insurance = float(request.form['insuarance'])  # ✅ Fixed typo
        maintenance = float(request.form['maintanance'])  # ✅ Fixed typo
        transport = float(request.form['transport'])
        taxes = float(request.form['taxes'])

        # Salaries & Cost of Goods
        c.execute('''
            SELECT 
                (SELECT SUM(salary) AS sal FROM salaries) ''')
        data = c.fetchone()

        c.execute('''
                (SELECT SUM(buying_price * quantity) AS cost FROM stock_info) 
        ''')
        price = c.fetchone()
        salary = data['sal'] if data and data['sal'] is not None else  0 # type: ignore
        cost_of_goods = price['cost'] if data and price['cost'] is not None else 0 # type: ignore

        total_expenses = electricity + water + internet + rent + supplies + ads + insurance + maintenance + transport + taxes

        # ✅ Update expense with start/end date
        c.execute('''
            UPDATE expenses
            SET start_date = %s, end_date = %s, salaries = %s, cost_of_good = %s, electricity = %s, water = %s, internet = %s, rent = %s, supplies = %s, ads = %s, insuarance = %s, maintanance = %s, transport = %s, taxes = %s, total_expenses = %s
            WHERE id = %s
        ''', (start_date, end_date, salary, cost_of_goods, electricity, water, internet, rent, supplies, ads, insurance, maintenance, transport, taxes, total_expenses, id))

        conn.commit()
        conn.close()

        flash('✅ Expense updated successfully!', 'success')
        return redirect(url_for('view_expense'))

    # 👉 GET request: fetch existing expense
    c.execute('SELECT * FROM expenses WHERE id = %s', (id,))
    expense = c.fetchone()
    conn.close()

    return render_template('record_expense.html', expense=expense)


from collections import defaultdict

def get_grouped_expenses():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM expenses ORDER BY end_date DESC')
    expenses = c.fetchall()
    conn.close()

    grouped = defaultdict(list)
    for expense in expenses:
        grouped[expense['end_date']].append(expense) # type: ignore

    return grouped

@app.route('/accounting')
def accounting():

    grouped_expenses = get_grouped_expenses()
    return render_template('account.html', grouped_expenses=grouped_expenses)

@app.route('/view_expenses')
def view_expense():
    grouped_expenses = get_grouped_expenses()
    return render_template('account.html', grouped_expenses=grouped_expenses)



@app.route('/create_expense', methods=['GET', 'POST'])
def create_expense():
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        electricity = float(request.form.get('electricity', 0) or 0)
        water = float(request.form.get('water', 0) or 0)
        internet = float(request.form.get('internet', 0) or 0)
        rent = float(request.form.get('rent', 0) or 0)
        supplies = float(request.form.get('supplies', 0) or 0)
        ads = float(request.form.get('ads', 0) or 0)
        insuarance = float(request.form.get('insuarance', 0) or 0)
        maintanance = float(request.form.get('maintanance', 0) or 0)
        transport = float(request.form.get('transport', 0) or 0)
        taxes = float(request.form.get('taxes', 0) or 0)

        # Fetch salaries and cost of goods safely
        c.execute('''
             
                (SELECT SUM(salary) AS total_salary FROM salaries) 
        ''')
        result = c.fetchone()      
        salar = result['total_salary'] if result and result['total_salary'] is not None else 0 # type: ignore
 
        c.execute('''
                (SELECT SUM(buying_price * quantity) AS cost FROM stock_info)  
        ''')
        price = c.fetchone()
        cost_of_goods = price['cost'] if result and price['cost'] is not None else 0 # type: ignore

        total_expenses = (
            electricity + water + internet + rent + supplies + ads +
            insuarance + maintanance + transport + taxes
        )

        # Insert into PostgreSQL
        c.execute('''
            INSERT INTO expenses (
                start_date, end_date, salaries, cost_of_good, electricity, water, internet, rent,
                supplies, ads, insuarance, maintanance, transport, taxes, total_expenses
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            start_date, end_date, salar, cost_of_goods, electricity, water, internet,
            rent, supplies, ads, insuarance, maintanance, transport, taxes, total_expenses
        ))

        conn.commit()
        conn.close()

        flash('✅ Expense recorded successfully!', 'success')

        return redirect(url_for('view_expense'))

    return render_template('record_expense.html')


@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE id = %s',(id,))
    conn.commit()
    conn.close()

    return redirect('/view_expenses')

from flask import request, render_template
from collections import defaultdict

@app.route('/filter_expenses', methods=['GET', 'POST'])
def filter_expenses():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not start_date or not end_date:
            return "Start and End date required", 400

        conn = get_connection()
        c = conn.cursor()

        # 1. Get individual expense entries
        c.execute('''
            SELECT * FROM expenses
            WHERE end_date BETWEEN %s AND %s
            ORDER BY end_date DESC
        ''', (start_date, end_date))
        expenses = c.fetchall()

        # 2. Calculate total sums for each column
        c.execute('''
            SELECT 
                SUM(salaries) AS total_salaries,
                SUM(cost_of_good) AS total_cost_of_good,
                SUM(electricity) AS total_electricity,
                SUM(water) AS total_water,
                SUM(internet) AS total_internet,
                SUM(rent) AS total_rent,
                SUM(supplies) AS total_supplies,
                SUM(ads) AS total_ads,
                SUM(insuarance) AS total_insuarance,
                SUM(maintanance) AS total_maintanance,
                SUM(transport) AS total_transport,
                SUM(taxes) AS total_taxes,
                SUM(total_expenses) AS grand_total
            FROM expenses
            WHERE end_date BETWEEN %s AND %s
        ''', (start_date, end_date))
        totals = c.fetchone()
        conn.close()

        return render_template(
            'account.html',
            expenses=expenses,
            totals=totals,
            start_date=start_date,
            end_date=end_date
        )

    return render_template('filter_form.html')


#Add product stock info
@app.route('/add_stockinfo', methods=['POST', 'GET'])
def add_stockinfo():
    conn = get_connection()
    c = conn.cursor()
    if request.method == 'POST':
        date = datetime.today().strftime('%Y-%m-%d')
        supplier_name = request.form['supplier_name']
        supplier_contact = request.form['supplier_contact']
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'] or 1)
        selling_price = float(request.form['selling_price'] or 0)
        buying_price = float(request.form['buying_price'] or 0)
        c.execute('''
        INSERT INTO stock_info (date, supplier_name, supplier_contact, item_name, quantity, selling_price, buying_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (date, supplier_name, supplier_contact, item_name, quantity, selling_price, buying_price))
        conn.commit()
        conn.close()

        return redirect(url_for('view_stockinfo'))

    return render_template('add_productstock.html')

#view stock info
@app.route('/view_stockinfo')
def view_stockinfo():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM stock_info')
    stockinfo = c.fetchall()
    conn.close()
    return render_template('inventory.html', stockinfo=stockinfo)

#edit stock info
@app.route('/edit_stockinfo/<int:id>', methods=['POST', 'GET'])
def edit_stockinfo(id):
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        date = datetime.today().strftime('%Y-%m-%d')
        supplier_name = request.form['supplier_name']
        supplier_contact = request.form['supplier_contact']
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'] or 1)
        selling_price = float(request.form['selling_price'] or 0)
        buying_price = float(request.form['buying_price'] or 0)

        c.execute('''
            UPDATE stock_info
            SET date = %s, supplier_name = %s, supplier_contact = %s, item_name = %s, quantity = %s, selling_price = %s, buying_price = %s
            WHERE item_id = %s
        ''', (date, supplier_name, supplier_contact, item_name, quantity, selling_price, buying_price, id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_stockinfo'))

    else:
        c.execute('SELECT * FROM stock_info WHERE item_id = %s', (id,))
        row = c.fetchone()
        conn.close()

        if row:
            product = {
                'id': row['item_id'], # type: ignore
                'date': row['date'], # type: ignore
                'supplier_name': row['supplier_name'], # type: ignore
                'supplier_contact': row['supplier_contact'], # type: ignore
                'item_name': row['item_name'], # type: ignore
                'quantity': row['quantity'], # type: ignore
                'selling_price': row['selling_price'], # type: ignore
                'buying_price': row['buying_price'] # type: ignore
                # Remove status if your table doesn’t have it
            }
        else:
            product = None

        return render_template('add_productstock.html', product=product, form_action=url_for('edit_stockinfo', id=id), button_text='Update Stock')

#delete stock info
@app.route('/delete_stockinfo/<int:id>')
def delete_stockinfo(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM stock_info WHERE item_id = %s', (id,))
    conn.commit()
    conn.close()
 
    return redirect(url_for('view_stockinfo'))



#navigate from dashboard to members

@app.route('/sales')
def sales():
    return render_template('sales.html',
                           sales=[],
                           summary=[],
                           weekly_summary=[],
                           monthly_summary=[],
                           page=1,
                           total_pages=1)


#navigate from dashboard to accounting and bookkeeping
from collections import defaultdict




@app.route('/daily_income_expenses')
def daily_income_expenses():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            DATE(date) as day,
            SUM(selling_price * quantity) AS total_sales,
            SUM(buying_price * quantity) AS total_expenses,
            SUM(quantity) AS items_sold
        FROM sales
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    ''')
    
    daily_data = c.fetchall()
    conn.close()
    return render_template('account.html', daily_data=daily_data)


#calculation of profit and loss in accounting and bookkeeping
@app.route('/profit_loss')
def profit_loss():
        conn = get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT 
            DATE(date) as day,
                SUM(CASE WHEN (selling_price * quantity) > (buying_price * quantity)
                        THEN (selling_price * quantity) - (buying_price * quantity)
                        ELSE 0 END) AS profit,
                SUM(CASE WHEN (selling_price * quantity) < (buying_price * quantity)
                        THEN (buying_price * quantity) - (selling_price * quantity)
                        ELSE 0 END) AS loss
            FROM sales
            GROUP BY day
            ORDER BY day DESC
            LIMIT 7
        ''')
        
        profit_loss = c.fetchall()
        conn.close()
        return render_template('account.html', profit_loss=profit_loss)

    



@app.route('/cashflow', methods=['GET', 'POST'])
def cashflow_statements():
    grouped_expenses = get_grouped_expenses()      

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        investments = float(request.form.get('investments', 0) or 0)
        financial = float(request.form.get('financial', 0) or 0)
        notes = request.form.get('notes', '')

        conn = get_connection()
        c = conn.cursor()

        # Use %s placeholders for PostgreSQL
        c.execute('SELECT SUM(selling_price * quantity) AS total_sales FROM sales WHERE date BETWEEN %s AND %s', (start_date, end_date))
        inflow_result = c.fetchone()
        inflow = inflow_result['total_sales'] if inflow_result and inflow_result['total_sales'] is not None else 0 # type: ignore

        c.execute('SELECT SUM(buying_price * quantity) AS total_cost FROM sales WHERE date BETWEEN %s AND %s', (start_date, end_date))
        outflow_result = c.fetchone()
        outflow = outflow_result['total_cost'] if outflow_result and outflow_result['total_cost'] is not None else 0 # type: ignore

        c.execute('SELECT SUM(total_expenses) AS expense FROM expenses WHERE start_date >= %s AND end_date <= %s', (start_date, end_date))
        expenses_result = c.fetchone()
        expenses = expenses_result['expense'] if expenses_result and expenses_result['expense'] is not None else 0 # type: ignore

        total_outflow = float(outflow) + float(expenses) + investments + financial
        net_cashflow = float(inflow) - total_outflow

        # Insert data
        c.execute('''
            INSERT INTO cashflow (start_date, end_date, inflow, outflow, expenses, investments, financial, total_outflow, net_cashflow, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (start_date, end_date, inflow, outflow, expenses, investments, financial, total_outflow, net_cashflow, notes))

        conn.commit()
        conn.close()

        flash("✅ Cashflow report generated and saved!", "success")


        return redirect(url_for('view_cashflow'))


    return render_template('cashflow.html', grouped_expenses=grouped_expenses)


@app.route('/view_cashflow')
def view_cashflow():
    grouped_expenses = get_grouped_expenses()      

    conn = get_connection()
    c = conn.cursor()

    c.execute('SELECT * FROM cashflow ORDER BY id DESC')
    reports = c.fetchall()

    conn.close()
    return render_template('account.html', reports=reports, grouped_expenses=grouped_expenses)

@app.route('/edit_cashflow/<int:id>', methods=['GET', 'POST'])
def edit_cashflow(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_start_date = request.form.get('start_date')
        new_end_date = request.form.get('end_date')
        new_investments = float(request.form.get('investments', 0) or 0)
        new_financial = float(request.form.get('financial', 0) or 0)
        new_notes = request.form.get('notes', '')

        # Recalculate inflow, outflow, expenses based on new dates
# inflow
        cursor.execute('SELECT SUM(selling_price * quantity) AS total_sales FROM sales WHERE date BETWEEN %s AND %s', (new_start_date, new_end_date))
        row = cursor.fetchone()
        inflow = row['total_sales'] if row and row['total_sales'] is not None else 0 # type: ignore

        # outflow
        cursor.execute('SELECT SUM(buying_price * quantity) AS total_cost FROM sales WHERE date BETWEEN %s AND %s', (new_start_date, new_end_date))
        row = cursor.fetchone()
        outflow = row['total_cost'] if row and row['total_cost'] is not None else 0 # type: ignore

        # expenses
        cursor.execute('SELECT SUM(total_expenses) AS expense FROM expenses WHERE start_date >= %s AND end_date <= %s', (new_start_date, new_end_date))
        row = cursor.fetchone()
        expenses = row['expense'] if row and row['expense'] is not None else 0 # type: ignore

        total_outflow = float(outflow) + float(expenses) + new_investments + new_financial
        net_cashflow = float(inflow) - float(total_outflow)

        # ✅ Update the cashflow record
        cursor.execute('''
            UPDATE cashflow
            SET start_date = %s, end_date = %s, inflow = %s, outflow = %s, expenses = %s, investments = %s, financial = %s, total_outflow = %s, net_cashflow = %s, notes = %s
            WHERE id = %s
        ''', (new_start_date, new_end_date, inflow, outflow, expenses, new_investments, new_financial, total_outflow, net_cashflow, new_notes, id))

        conn.commit()
        conn.close()

        flash("✅ Cashflow report updated successfully!", "success")

        return redirect('/view_cashflow')

    # Fetch the existing record for pre-filling the form
    cursor.execute('SELECT * FROM cashflow WHERE id = %s', (id,))
    report = cursor.fetchone()
    conn.close()
    if report:
        cashflow = {
            'id': report['id'], # type: ignore
            'start_date': report['start_date'], # type: ignore
            'end_date': report['end_date'], # type: ignore
            'inflow': report['inflow'], # type: ignore
            'outflow': report['outflow'], # type: ignore
            'expenses': report['expenses'], # type: ignore
            'investments': report['investments'], # type: ignore
            'financial': report['financial'], # type: ignore
            'total_outflow': report['total_outflow'], # type: ignore
            'net_cashflow': report['net_cashflow'], # type: ignore
            'notes': report['notes'] # type: ignore
        }
    else:
        cashflow = {}

    return render_template('cashflow.html', cashflow=cashflow, form_action=url_for('edit_cashflow', id=id))

@app.route('/delete_cashflow/<int:id>')
def delete_cashflow(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM cashflow WHERE id = %s', (id,))
    conn.commit()
    conn.close()

    flash("🗑️ Sale deleted successfully!", "success")

    return redirect('/view_cashflow')

#assign tasks and responsibilties@app.route('/assign_tasks', methods=['POST', 'GET'])
@app.route('/assign_tasks', methods=['POST', 'GET'])
def assign_tasks():
    if request.method == 'POST':
        conn = get_connection()
        c = conn.cursor()
        try:
            company_id = request.form['company_id']
            tasks = request.form.getlist('tasks[]')
            responsibilities = request.form.getlist('responsibilities[]')
            description = request.form['description']  # Now single value
            date_assigned = request.form['date_assigned']

            if len(tasks) != len(responsibilities):
                flash("❌ Error: Mismatched task and responsibility count.", "danger")
                return redirect(url_for('assign_tasks'))

            c.execute('SELECT name FROM members WHERE company_id = %s', (company_id,))
            result = c.fetchone()
            if not result:
                flash("❌ Error: No employee found with that ID.", "danger")
                return redirect(url_for('assign_tasks'))
            name = result['name'] # type: ignore

            for task, respo in zip(tasks, responsibilities):
                c.execute('INSERT INTO respo (name, company_id, respo, tasks, description, date_assigned) VALUES (%s, %s, %s, %s, %s, %s)',
                          (name, company_id, respo, task, description, date_assigned))

            conn.commit()

            flash("✅ Tasks assigned successfully!", "success")
            return redirect(url_for('view_tasks'))

        except Exception as e:
            flash(f"❌ Error: {e}", "danger")
        finally:
            conn.close()

    return render_template('assign_tasks.html')



@app.route('/check_tasks/<int:id>', methods=['GET', 'POST'])
def check_tasks(id):
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        date_checked = request.form['date_checked']
        remarks = request.form['remarks']

        try:
            score = float(remarks.strip().split('/')[0])
            if score > 10 or score < 0:
                flash("❌ Remarks should be out of 10.", "danger")
                return redirect(request.url)
        except:
            flash("❌ Invalid remarks format. Use format like 7/10.", "danger")
            return redirect(request.url)

        try:
            c.execute('''
                UPDATE respo
                SET date_checked = %s, remarks = %s
                WHERE id = %s
            ''', (date_checked, remarks, id))
            conn.commit()
            flash("✅ Task checked and remarks saved!", "success")
            return redirect(url_for('view_tasks'))

        except Exception as e:
            flash(f"❌ Error: {e}", "danger")

    c.execute('SELECT * FROM respo WHERE id = %s', (id,))
    task = c.fetchone()
    conn.close()

    return render_template('check_task.html', task=task)

 

@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = get_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        task = request.form['task']
        respo = request.form['respo']
        description = request.form['description']
        remarks = request.form['remarks']
        date_checked = request.form['date_checked']

        c.execute('''
            UPDATE respo
            SET tasks = %s, respo = %s, description = %s, remarks = %s, date_checked = %s
            WHERE id = %s
        ''', (task, respo, description, remarks, date_checked, id))

        conn.commit()
        conn.close()

        flash("✅ Task updated successfully", "success")
        return redirect(url_for('view_tasks'))
    
    # GET request — load data into form
    c.execute('SELECT * FROM respo WHERE id = %s', (id,))
    files = c.fetchone()
    conn.close()
    return render_template('edit_task.html', files=files)
@app.route('/delete_task/<int:id>')
def delete_task(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM respo WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Task deleted successfully", "success")

    return redirect(url_for('view_tasks'))

from collections import defaultdict

@app.route('/view_tasks')
def view_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, name, company_id, respo, tasks, date_assigned, date_checked, remarks, description FROM respo')
    rows = c.fetchall()
    conn.close()

    # Group by (name, company_id)
    grouped = defaultdict(list)
    for row in rows:
        key = (row['name'], row['company_id'])  # type: ignore # name, company_id
        grouped[key].append(row)

    return render_template('members.html', grouped_tasks=grouped)

@app.route('/view_employee_details')
def view_employee_details():
    return "comming soon"

@app.route('/tax_tracking')
def tax_tracking():
    return "coming soon...."

@app.route('/financial_report')
def generate_financial_report():
    return "coming soon...."


#navigate from dashboard to view products




#navigate from dashboard to invoicing and quotations
@app.route('/invoicing')
def invoicing():
    return render_template('invoicing.html')

#navigate from dashboard to inventory management
@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

#navigate from dashboard to business summary
@app.route('/summary')
def summary():
    return render_template('summary.html')

@app.route('/print_contract')
def print_contract():
    return render_template('contract.html')


#SALES
@app.route('/dashboard_sales')
def dashboard_sales():
    conn = get_connection()
    c = conn.cursor()

    # Fetch the latest 40 sales, ordered from oldest to newest
    c.execute("SELECT * FROM sales ORDER BY sale_id DESC LIMIT 40")
    recent_sales = c.fetchall()

    # Now reverse the list so the oldest (lowest ID) appears first
    sales = recent_sales[::-1]

    conn.close()

    return render_template('sales.html', sales=sales)





#navigate from sales.html to record_sales.html


@app.route('/record_sales', methods=["GET", "POST"])
def record_sales():
    if request.method == "POST":
        conn = get_connection()
        cur = conn.cursor() # type: ignore

        try:
            # Convert form inputs
            try:
                item_id = int(request.form['item_id'])
                quantity_sold = int(request.form['quantity'])
                selling_price = float(request.form['selling_price'])
            except ValueError:
                flash("❌ Please enter valid numeric values", "danger")
                return redirect(url_for('record_sales'))

            payment_method = request.form['payment']

            # Fetch product
            cur.execute("SELECT item_name, quantity, buying_price FROM stock_info WHERE item_id = %s", (item_id,))
            item = cur.fetchone()

            if not item:
                flash("❌ Product with that ID does not exist.", "danger")
                return redirect(url_for('record_sales'))
            name = item['item_name'] # type: ignore
            stock_qty = int(float(item['quantity'])) # type: ignore # type: ignore))
            buying_price = item['buying_price'] # type: ignore

            try:
                
                # Debug: Print raw values before conversion
                print(f"Raw values - stock_qty: {stock_qty} (type: {type(stock_qty)}), buying_price: {buying_price} (type: {type(buying_price)})")
                # Convert quantities
                stock_quntity = stock_qty if stock_qty not in [None, ''] else 0
                buying_price = float(buying_price) if buying_price not in [None, ''] else 0.0
                
                # Debug: Print converted values
                print(f"Converted - stock_qty: {stock_quntity}, buying_price: {buying_price}")
                
            except (ValueError, TypeError) as e:
                flash(f"❌ Database contains invalid values. Error: {str(e)}", "danger")
                print(f"Conversion error. Raw values: stock_qty={stock_qty}, buying_price={buying_price}")
                return redirect(url_for('record_sales'))

            # Validate quantities
            if stock_qty <= 0:
                flash("❌ Product is out of stock", "danger")
                return redirect(url_for('record_sales'))

            if quantity_sold > stock_qty:
                flash("❌ Quantity exceeds stock available.", "danger")
                return redirect(url_for('record_sales'))

            # Calculate values
            total_selling = selling_price * quantity_sold
            total_buying = buying_price * quantity_sold
            profit_or_loss = total_selling - total_buying
            date = datetime.now().strftime("%Y-%m-%d")

            # Save sale
            cur.execute("""
                INSERT INTO sales (item_id, item_name, quantity, selling_price, buying_price, payment, profit_or_loss, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (item_id, name, quantity_sold, selling_price, buying_price, payment_method, profit_or_loss, date))

            # Update stock
            new_qty = stock_qty - quantity_sold
            cur.execute("UPDATE stock_info SET quantity = %s WHERE item_id = %s", (new_qty, item_id))

            conn.commit()
            


            return redirect('/dashboard_sales')

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error processing sale: {str(e)}", "danger")
            print(f"Unexpected error: {str(e)}")
            return redirect(url_for('record_sales'))
        finally:
            conn.close()

    return render_template('record_sales.html', 
                         form_action=url_for('record_sales'),
                         sale=None,
                         button_text='Record Sale')



@app.route('/edit_sales/<int:id>', methods=['GET', 'POST'])
def edit_sales(id):
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        try:
            # 1. Fetch the existing sale first
            c.execute("SELECT item_id, quantity FROM sales WHERE sale_id = %s", (id,))
            old_sale = c.fetchone()
            if not old_sale:
                flash("❌ Sale not found.", "danger")
                return redirect('/dashboard_sales')

            old_quantity = old_sale['quantity'] # type: ignore
            item_id = old_sale['item_id'] # type: ignore

            # 2. Get updated values from form
            new_type = request.form.get('item_name', '')
            new_quantity = int(request.form.get('quantity', 0))
            new_selling_price = float(request.form.get('selling_price', 0))
            new_payment = request.form.get('payment', '')
            new_buying_price = float(request.form.get('buying_price', 0))

            new_total_buying = new_buying_price * new_quantity
            new_total_selling = new_selling_price * new_quantity
            new_profit_or_loss = new_total_selling - new_total_buying

            # 3. Calculate the stock difference
            qty_diff = new_quantity - old_quantity
            # If qty_diff > 0 → sold more → reduce stock
            # If qty_diff < 0 → sold less → restore stock
            c.execute("UPDATE stock_info SET quantity = quantity - %s WHERE item_id = %s", (qty_diff, item_id))

            # 4. Update the sale
            c.execute("""
                UPDATE sales
                SET item_name = %s,
                    quantity = %s,
                    selling_price = %s,
                    payment = %s,
                    buying_price = %s,
                    profit_or_loss = %s
                WHERE sale_id = %s
            """, (new_type, new_quantity, new_selling_price, new_payment,
                  new_buying_price, new_profit_or_loss, id))

            conn.commit()



            return redirect('/dashboard_sales')

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error: {e}", "danger")
        finally:
            conn.close()

    # GET request: fetch sale
    c.execute('SELECT * FROM sales WHERE sale_id = %s', (id,))
    sale_row = c.fetchone()
    conn.close()

    if not sale_row:
        flash('❌ Sale not found.', 'danger')
        return redirect('/dashboard_sales')

    sale = {
        'id': sale_row['sale_id'], # type: ignore
        'type': sale_row['item_name'], # type: ignore
        'quantity': sale_row['quantity'], # type: ignore
        'selling_price': sale_row['selling_price'], # type: ignore
        'payment': sale_row['payment'], # type: ignore
        'buying_price': sale_row['buying_price'] # type: ignore
    }

    return render_template(
        'record_sales.html',
        form_action=url_for('edit_sales', id=id),
        sale=sale,
        items=[],
        button_text='Update Sale'
    )

 

@app.route('/delete_sales/<int:id>', methods=['GET'])
def delete_sales(id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Fetch sale info
        cur.execute("SELECT item_id, quantity FROM sales WHERE sale_id = %s", (id,))
        sale = cur.fetchone()
        if not sale:
            flash("❌ Sale not found", "danger")
            return redirect('/dashboard_sales')

        item_id = sale['item_id'] # type: ignore
        quantity_sold = sale['quantity'] # type: ignore

        # 2. Restore stock
        cur.execute("UPDATE stock_info SET quantity = quantity + %s WHERE item_id = %s",
                    (quantity_sold, item_id))

        # 3. Delete the sale
        cur.execute("DELETE FROM sales WHERE sale_id = %s", (id,))
        conn.commit()

        flash("✅ Sale deleted and stock restored", "success")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error deleting sale: {e}", "danger")
    finally:
        conn.close()

    return redirect('/dashboard_sales')


#daily summary
@app.route('/daily_summary')
def daily_summary():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            DATE(date) as day,
            SUM(selling_price * quantity) AS total_sales,
            SUM(CASE WHEN (selling_price * quantity) > (buying_price * quantity)
                     THEN (selling_price * quantity) - (buying_price * quantity)
                     ELSE 0 END) AS profit,
            SUM(CASE WHEN (selling_price * quantity) < (buying_price * quantity)
                     THEN (buying_price * quantity) - (selling_price * quantity)
                     ELSE 0 END) AS loss,
            SUM(quantity) AS items_sold
        FROM sales
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    ''')
    
    summary = c.fetchall()
    conn.close()
    return render_template('sales.html',
                       sales=[],
                       summary=summary,  # <- this should be the result from the DB
                       weekly_summary=[],
                       monthly_summary=[],
                       page=1,
                       total_pages=1)


#weekly summmary
@app.route('/weekly_summary')
def weekly_summary():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT
            TO_CHAR(DATE_TRUNC('week', date::DATE), 'IYYY-IW') AS week,
            SUM(selling_price * quantity) AS total_sales,
            SUM(
                CASE 
                    WHEN (selling_price * quantity) > (buying_price * quantity)
                    THEN (selling_price * quantity) - (buying_price * quantity)
                    ELSE 0 
                END
            ) AS profit,
            SUM(
                CASE 
                    WHEN (selling_price * quantity) < (buying_price * quantity)
                    THEN (buying_price * quantity) - (selling_price * quantity)
                    ELSE 0 
                END
            ) AS loss,
            SUM(quantity) AS items_sold
        FROM sales
        GROUP BY DATE_TRUNC('week', date::DATE)
        ORDER BY week DESC
    """)


    weekly_sales = c.fetchall()
    conn.close()

    return render_template(
        'sales.html',
        sales=[],
        summary=[],
        weekly_summary=weekly_sales,
        monthly_summary=[],
        page=1,
        total_pages=1
    )


#monthly summary
@app.route('/monthly_summary')
def monthly_summary():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT
            TO_CHAR(date::DATE, 'YYYY-MM') AS month,
            SUM(selling_price * quantity) AS total_sales,
            SUM(
                CASE 
                    WHEN (selling_price * quantity) > (buying_price * quantity)
                    THEN (selling_price * quantity) - (buying_price * quantity)
                    ELSE 0 
                END
            ) AS profit,
            SUM(
                CASE 
                    WHEN (selling_price * quantity) < (buying_price * quantity)
                    THEN (buying_price * quantity) - (selling_price * quantity)
                    ELSE 0 
                END
            ) AS loss,
            SUM(quantity) AS items_sold
        FROM sales
        GROUP BY TO_CHAR(date::DATE, 'YYYY-MM')
        ORDER BY month DESC
    """)

    monthly_sales = c.fetchall()
    conn.close()

    return render_template(
        'sales.html',
        sales=[],
        summary=[],
        weekly_summary=[],
        monthly_summary=monthly_sales,
        page=1,
        total_pages=1
    )


#MEMBERS
@app.route('/members')
def members():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM members")
    data = c.fetchall()
    conn.close()
    return render_template('members.html', members=data)


def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Add Member (Create)
@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        role = request.form["role"]
        company_id = request.form["company_id"]
        status = request.form['status']
        email = request.form['email']

        # Handle profile photo
        photo = request.files.get('profile_photo')
        photo_filename = None

        if photo and photo.filename and allowed_image_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_filename = f"{phone}_{filename}"
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        # Connect to DB and check if member already exists
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM members WHERE name=%s AND phone=%s AND company_id=%s", (name, phone, company_id))
        existing = cur.fetchone()

        if existing:
            flash("❗ Member already exists.", "error")
            conn.close()
            return redirect("/add_member")

        # Insert new member
        cur.execute("INSERT INTO members (name, phone, role, company_id, status, email,  profile_photo) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, phone, role, company_id, status, email, photo_filename))
        conn.commit()
        conn.close()

        flash("✅ Member added successfully.", "success")
        return redirect(url_for('view_members'))

    return render_template("add_member.html", form_action=url_for('add_member'), person=None)

# Edit Member (Update)
@app.route('/edit_member/<int:id>', methods=['GET', 'POST'])
def edit_member(id):
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form["name"]
        phone = request.form["phone"]
        role = request.form["role"]
        company_id = request.form["company_id"]
        responsibility = request.form['email']
        status = request.form['status']
        photo = request.files.get('profile_photo')
        photo_filename = None

        if photo and photo.filename and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_filename = f"{phone}_{filename}"
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

            # With photo
            c.execute('UPDATE members SET name = %s, phone = %s, role = %s, company_id = %s, status = %s, email = %s, profile_photo = %s WHERE id = %s', 
                      (name, phone, role, company_id, status, responsibility, photo_filename, id))
        else:
            # Without changing photo
            c.execute('UPDATE members SET name = %s, phone = %s, role = %s, company_id = %s, status = %s, email = %s WHERE id = %s', 
                      (name, phone, role, company_id, status, responsibility, id))

        conn.commit()
        conn.close()

        flash("✅ Member updated successfully.", "success")
        return redirect(url_for('view_members'))

    # GET request - load member data
    c.execute('SELECT * FROM members WHERE id = %s', (id,))
    mem = c.fetchone()
    conn.close()

    person = {
        'id': mem['id'], # type: ignore
        'name': mem['name'], # type: ignore
        'phone': mem['phone'], # type: ignore
        'role': mem['role'], # type: ignore
        'company_id': mem['company_id'], # type: ignore
        'responsibilities': mem['email'], # type: ignore
        'status': mem['status'], # type: ignore
        'profile_photo': mem['profile_photo'] if len(mem) > 7 else None # type: ignore
    } if mem else None

    return render_template('add_member.html', form_action=url_for('edit_member', id=id), person=person)


# View Members Page (for table)
@app.route('/members')
def view_members():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM members')
    members = c.fetchall()
    conn.close()
    return render_template('view_members.html', members=members)

@app.route("/delete/<int:id>")
def delete_member(id):  # Added 'id' as a function argument
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM members WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Member deleted successfully.", "success")

    return redirect("/members")



@app.route("/search", methods=["GET"])
def search_members():
    keyword = request.args.get("q", "")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM members WHERE name LIKE %s OR role LIKE %s",
                (f"%{keyword}%", f"%{keyword}%"))
    members = cur.fetchall()
    conn.close()
    return render_template("members.html", members=members)


@app.route("/sort")
def sort_members():
    by = request.args.get("by", "id")
    order = request.args.get("order", "asc").upper()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM members ORDER BY {by} {order}")
    members = cur.fetchall()
    conn.close()
    return render_template("members.html", members=members)


@app.route('/create_invoice', methods=['GET', 'POST'])
def create_invoice():
    if request.method == 'POST':
        name = request.form['customer_name']
        item_type = request.form.getlist('item_type[]')
        item_quantity = request.form.getlist('item_quantity[]')
        selling_price = request.form.getlist('selling_price[]')
        status = request.form['status']

        total = 0
        for p, q, r in zip(item_type, item_quantity, selling_price):
            if p.strip() == "" or q.strip() == "" or r.strip() == "":
                continue
            total += int(q) * float(r)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO invoices (customer_name, total_price) VALUES (%s, %s) RETURNING id",
            (name, total)
        )
        result = cursor.fetchone()
        if result:
            invoice_id = result[0]

            for i in range(len(item_type)):
                if item_type[i].strip() == "" or item_quantity[i].strip() == "" or selling_price[i].strip() == "":
                    continue
                cursor.execute(
                    "INSERT INTO invoice_items (invoice_id, item_type, item_quantity, selling_price, status) VALUES (%s, %s, %s, %s, %s)",
                    (
                        invoice_id,
                        item_type[i],
                        int(item_quantity[i]),
                        float(selling_price[i]),
                        status
                    )
                )

            conn.commit()
            conn.close()
            return redirect(url_for('all_invoices'))
        else:
            conn.rollback()
            conn.close()
            return "Failed to insert invoice and retrieve ID", 500

    invoice = {'status': 'not paid'}
    return render_template('create_invoice.html', invoice=invoice)


@app.route('/invoices')
def all_invoices():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM invoices")
    invoices = cursor.fetchall()

    invoice_data = []
    for inv in invoices:
        cursor.execute("""
            SELECT item_type, item_quantity, selling_price, status
            FROM invoice_items
            WHERE invoice_id = %s
        """, (inv[0],))  # assuming invoice ID is at index 0
        items = cursor.fetchall()
        invoice_data.append({'invoice': inv, 'items': items})

    conn.close()
    return render_template('invoicing.html', data=invoice_data)





# --- EDIT INVOICE ---
@app.route('/edit_invoice/<int:id>', methods=['GET', 'POST'])
def edit_invoice(id):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch invoice and items
    cursor.execute('SELECT * FROM invoices WHERE id = %s', (id,))
    invoice = cursor.fetchone()

    cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = %s', (id,))
    items = cursor.fetchall()

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        item_type = request.form.getlist('item_type[]')
        quantity = request.form.getlist('quantity[]')      
        price = request.form.getlist('price[]')            
        status = request.form['status']

        new_total = 0
        for a, b in zip(quantity, price):
            if a.strip() and b.strip():
                new_total += int(a) * float(b)

        cursor.execute("UPDATE invoices SET customer_name = %s, total_price = %s WHERE id = %s", 
                       (customer_name, new_total, id))

        cursor.execute("DELETE FROM invoice_items WHERE invoice_id = %s", (id,))

        added_any = False
        for t, q, p in zip(item_type, quantity, price):
            if t.strip() and q.strip() and p.strip():
                cursor.execute("""
                    INSERT INTO invoice_items (invoice_id, item_type, item_quantity, selling_price, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id, t.strip(), int(q), float(p), status))
                added_any = True

        if not added_any:
            print("⚠️ No items were added for invoice ID", id)

        conn.commit()
        conn.close()
        return redirect(url_for('all_invoices'))

    conn.close()
    return render_template('edit_invoice.html', invoice=invoice, items=items)


# --- DELETE INVOICE ---
@app.route('/delete_invoice/<int:id>', methods=['POST'])
def delete_invoice(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM invoices WHERE id = %s', (id,))
        invoice = cursor.fetchone()
        if not invoice:
            conn.close()
            return jsonify({'success': False, 'message': 'Invoice not found'}), 404

        cursor.execute('DELETE FROM invoice_items WHERE invoice_id = %s', (id,))
        cursor.execute('DELETE FROM invoices WHERE id = %s', (id,))

        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Invoice deleted successfully'})

    except Exception as e:
        conn.close()
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500

# Show meetings dashboard (GET) and handle meeting creation (POST)
@app.route('/meetings', methods=['GET', 'POST'])
def meetings():
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        time = request.form['time']
        c.execute("INSERT INTO meetings (title, date, time) VALUES (%s, %s, %s)", (title, date, time))
        conn.commit()
        flash("✅ Meeting added successfully", "success")
        conn.close()
        return redirect(url_for('view_meetings'))  # Redirect to dashboard after saving

    # fallback GET — just in case
    c.execute("SELECT * FROM meetings ORDER BY date, time")
    all_meetings = c.fetchall()
    conn.close()

    return render_template('meetings.html', meetings=all_meetings)
@app.route('/view_meetings')
def view_meetings():
    if 'user' not in session:
        flash("❌ Please log in", "danger")
        return redirect(url_for('login'))

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT title, date, time FROM meetings ORDER BY date ASC")
    rows = c.fetchall()
    conn.close()

    return render_template('new_dashboard.html', meetings=rows)





UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)









@app.route('/add_contract', methods=['GET', 'POST'])
def add_contract():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        client_name = request.form['client_name']
        client_contact = request.form['client_contact']
        contract_amount = float(request.form['contract_amount'])
        date_assigned = request.form['date_assigned']

        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO contracts (title, description, status, client_name, client_contact, contract_amount, date_assigned)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (title, description, status, client_name, client_contact, contract_amount, date_assigned))
        conn.commit()
        conn.close()


        return redirect(url_for('dashboard'))  

    return render_template('add_contract.html')  


@app.route('/add_expense/<int:contract_id>', methods=['GET', 'POST'])
def add_expense(contract_id):
    if request.method == 'POST':
        date = request.form['date']
        workers = float(request.form['workers'])
        materials = float(request.form['materials'])
        others = float(request.form['others'])

        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO contract_expenses (contract_id, date, workers, materials, others)
            VALUES (%s, %s, %s, %s, %s)
        ''', (contract_id, date, workers, materials, others))
        conn.commit()
        conn.close()


        return redirect(url_for('view_contracts'))

    return render_template('add_expense.html', contract_id=contract_id)


@app.route('/edit_contract/<int:id>', methods=['GET', 'POST'])
def edit_contract(id):
    conn = get_connection()
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        client_name = request.form['client_name']
        client_contact = request.form['client_contact']
        contract_amount = float(request.form['contract_amount'])
        date_assigned = request.form['date_assigned']

        c.execute('''
            UPDATE contracts
            SET title = %s, description = %s, status = %s, client_name = %s, client_contact = %s, contract_amount = %s, date_assigned = %s
            WHERE id = %s
        ''', (title, description, status, client_name, client_contact, contract_amount, date_assigned, id))

        conn.commit()
        conn.close()
      
        return redirect(url_for('view_contracts', contract_id=id))

    # GET request - fetch the contract
    c.execute("SELECT * FROM contracts WHERE id = %s", (id,))
    contract = c.fetchone()
    conn.close()
    return render_template('add_contract.html', contract=contract)


@app.route('/view_contracts')
def view_contracts():
    conn = get_connection()
    c = conn.cursor()

    # Fetch all contracts
    c.execute("SELECT * FROM contracts")
    contracts = c.fetchall()

    # Fetch all expenses
    c.execute("SELECT * FROM contract_expenses")
    expenses = c.fetchall()

    conn.close()
    return render_template("view_contracts.html", contracts=contracts, expenses=expenses)



@app.route('/edit_contract_expense/<int:id>', methods=['GET', 'POST'])
def edit_contract_expense(id):
    conn = get_connection()
    c = conn.cursor()  

    if request.method == 'POST':
        date = request.form['date']
        workers = float(request.form['workers'])
        materials = float(request.form['materials'])
        others = float(request.form['others'])

        c.execute('''
            UPDATE contract_expenses
            SET date = %s, workers = %s, materials = %s, others = %s
            WHERE id = %s
        ''', (date, workers, materials, others, id))

        # Get contract ID to redirect
        c.execute("SELECT contract_id FROM contract_expenses WHERE id = %s", (id,))
        contract_row = c.fetchone()
        conn.commit()
        conn.close()

        contract_id = contract_row[0] if contract_row else None
        return redirect(url_for('view_contracts', contract_id=contract_id))

    # GET method – fetch data to populate form
    c.execute("SELECT * FROM contract_expenses WHERE id = %s", (id,))
    expense = c.fetchone()
    conn.close()

    return render_template('add_expense.html', expense=expense)


@app.route('/delete_contract_expense/<int:id>')
def delete_contract_expense(id):
    conn = get_connection()
    c = conn.cursor()

    # Try to get contract_id from the expense
    c.execute("SELECT contract_id FROM contract_expenses WHERE id = %s", (id,))
    row = c.fetchone()

    if row:
        # If using default cursor, row is a tuple
        contract_id = row[0]  # instead of row['contract_id']

        # Delete the expense
        c.execute("DELETE FROM contract_expenses WHERE id = %s", (id,))
        conn.commit()
        conn.close()

        return redirect(url_for('view_contracts', contract_id=contract_id))

    else:
        conn.close()

        # Notify admin (optional but clarified)


        return "Contract expense not found", 404


@app.route('/delete_contract/<int:id>')
def delete_contract(id):
    conn = get_connection()
    c = conn.cursor()  # Added DictCursor for consistency

    c.execute("SELECT * FROM contracts WHERE id = %s", (id,))
    contract = c.fetchone()

    if contract:
        c.execute("DELETE FROM contracts WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_contracts'))
    else:
        conn.close()
     
        return "Contract not found", 404



@app.route('/dashboard')
def dashboard():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT username, email, phone, profile_photo FROM users WHERE username = %s", (session.get('username'),))
    user_data = cur.fetchone()  # Type hint to tell Pylance it's a dict or None
    conn.close()



    return render_template('dashboard.html', username=session.get('username', 'Guest'), user=user_data)

@app.route('/new_dashboard')
def new_dashboard():
    conn = get_connection()
    cur = conn.cursor()

    # Unpaid Invoices


    # Contracts
    cur.execute("""
        SELECT id, title, client_name, status
        FROM contracts
        ORDER BY date_assigned DESC
        LIMIT 3
    """)
    contract_snaps = [dict(row) for row in cur.fetchall()]

    # Meetings
    cur.execute("""
        SELECT title, date, time
        FROM meetings
        ORDER BY date ASC, time ASC
        LIMIT 5
    """)
    meetings = [dict(row) for row in cur.fetchall()]

    # Top & Least Sellers
    cur.execute('''
        SELECT type, SUM(quantity) AS total_quantity
        FROM sales
        GROUP BY type
        ORDER BY total_quantity DESC
    ''')
    sales_data = cur.fetchall()

    top_sellers = sales_data[:2]
    least_sellers = sales_data[-2:] if len(sales_data) >= 2 else []

    conn.close()

    return render_template(
        'new_dashboard.html',
        contract_snaps=contract_snaps,
        top_sellers=top_sellers,
        least_sellers=least_sellers,
        meetings=meetings
    )


@app.route('/sales_data')
def sales_data():
    today = datetime.today()
    labels = []
    real_sales = []
    profits = []
    predicted = []
    losses = []

    for i in range(6, -1, -1):  # Past 7 days
        day = today - timedelta(days=i)
        day_name = day.strftime('%a')  # e.g., 'Mon'
        date_str = day.strftime('%Y-%m-%d')
        labels.append(day_name)

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT 
                SUM(selling_price * quantity), 
                SUM(buying_price * quantity),
                SUM(profit_or_loss)
            FROM sales 
            WHERE date = %s
        """, (date_str,))
        row = c.fetchone()
        conn.close()



        if row and any(row):
            sales = row[0] if row[0] else 0
            cost = row[1] if row[1] else 0
            profit = row[2] if row[2] else 0

        else:
            sales = cost = profit = 0
        predicted_val = sales + 1000



        # Loss: if profit_or_loss total < 0
        loss = abs(profit) if profit < 0 else 0
        profit = profit if profit > 0 else 0

        real_sales.append(sales)
        profits.append(profit)
        predicted.append(predicted_val)
        losses.append(loss)

    return jsonify({
        "labels": labels,
        "real_sales": real_sales,
        "profits": profits,
        "predicted": predicted,
        "losses": losses
    })



@app.route('/print_receipt')
def print_receipt():
    return render_template('receipt.html')


 

import psycopg2.extras

import psycopg2.extras

@app.route('/receipt/<int:receipt_no>')
def render_receipt(receipt_no):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Fetch all sales tied to this receipt
    cur.execute('SELECT * FROM sales WHERE sale_id = %s', (receipt_no,))
    sales = cur.fetchall()
    conn.close()

    if not sales:
        return "No receipt found."

    # Calculate subtotal from all rows
    subtotal = sum(s['quantity'] * s['selling_price'] for s in sales)
    tax = round(subtotal * 0.16, 2)
    grand_total = round(subtotal + tax, 2)

    return render_template(
        'receipt.html',
        sale=sales,  # list of dicts for the for-loop
        date=sales[0]['date'],  # assuming all have the same date
        receipt_no=sales[0]['sale_id'],
        customer_no=1000 + sales[0]['sale_id'],
        subtotal=subtotal,
        tax=tax,
        grand_total=grand_total
    )



# Check if uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route: Show the form to add new furniture


# Route: Handle the form submission (insertion)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(url_for('view_products'))

        file = request.files['image']
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        selling_price = request.form.get('selling_price')
        buying_price = request.form.get('buying_price')

        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = os.path.join('uploads', filename)

            conn = get_connection()
            c = conn.cursor()
            c.execute('''
                    INSERT INTO furniture (name, quantity, selling_price, buying_price, image_path) 
                    VALUES (%s, %s, %s, %s, %s)''',
                    (name, quantity, selling_price, buying_price, image_path))
            conn.commit()
    

        return redirect(url_for('view_products'))

    # If GET request → Show the form
    return render_template('add_product.html')


# Route: View all products
@app.route('/view_products')
def view_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM furniture')
    items = c.fetchall()
    c.close()
    conn.close()
    return render_template('view_products.html', items=items)
@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM furniture WHERE id = %s', (id,))
    conn.commit()

    return redirect(url_for('view_products'))

#Edit product
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_connection()
    c = conn.cursor()
    if request.method == 'POST':
            name = request.form.get('name')
            quantity = request.form.get('quantity')
            selling_price = request.form.get('selling_price')
            buying_price = request.form.get('buying_price')
            c.execute('''
                UPDATE furniture 
                SET name=%s, quantity=%s, selling_price=%s, buying_price=%s
                WHERE item_id=%s
            ''', (name, quantity, selling_price, buying_price, id))
            conn.commit()

            return redirect(url_for('view_products'))

    c.execute('SELECT * FROM furniture WHERE item_id=%s', (id,))
    row = c.fetchone()
    if row:
            product = {
                'id': row['item_id'], # type: ignore
                'name': row['name'], # type: ignore
                'quantity': row['quantity'], # type: ignore
                'selling_price': row['selling_price'], # type: ignore
                'buying_price': row['buying_price'], # type: ignore
                'image_path': row['image_path'] # type: ignore
            }
    else:
        product = None

    c.close()
    conn.close()

    return render_template('add_product.html', form_action=url_for('edit_product', id=id), button_text='Update Product', product=product)
#Create a user


# Optional: Logout route

if __name__ == '__main__':
    init_db()
    app.run(debug=True)



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

