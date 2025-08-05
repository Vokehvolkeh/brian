from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
import traceback
from flask import jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import africastalking

import sqlite3

def init_db():
    with sqlite3.connect('furniture.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS furniture (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            quantity INTEGER,
            selling_price REAL,
            buying_price REAL,
            image_path TEXT
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS damaged_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            name TEXT,
            quantity REAL,
            buying_price REAL,
            selling_price REAL,
            loss REAL,
            reason TEXT
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS stock_info (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            role TEXT,
            company_id INTEGER,
            status TEXT,
            email TEXT,
            profile_photo TEXT
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            item_name TEXT,
            quantity INTEGER,
            selling_price REAL,
            buying_price REAL,
            payment TEXT,
            profit_or_loss REAL,
            date TEXT
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date TEXT,
            time TEXT
        );''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                profile_photo TEXT,
                email TEXT,
                phone TEXT
            );
        ''')


        c.execute('''CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            total_price INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            invoice_id INTEGER,
            item_quantity INTEGER NOT NULL,
            selling_price INTEGER,
            is_paid INTEGER DEFAULT 0,
            status TEXT DEFAULT 'not paid',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS quotations_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_id INTEGER,
            item_type TEXT,
            quantity INTEGER,
            price REAL,
            total REAL
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS cashflow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT,
            end_date TEXT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            employee_id INTEGER,
            salary REAL,
            status TEXT
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            status TEXT,
            client_name TEXT,
            client_contact TEXT,
            contract_amount REAL,
            date_assigned TEXT
        );''')

        c.execute('''CREATE TABLE IF NOT EXISTS contract_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            date TEXT,
            workers REAL,
            materials REAL,
            others REAL,
            balance REAL,
            profit_or_loss REAL,
            daily_outflow REAL
        );''')
        c.execute('''CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                  id  INTEGER PRIMARY KEY AUTOINCREMENT,
                time_in TEXT,
                time_out TEXT,
                email TEXT,
                address TEXT,
                  phone TEXT
                  )''')
        c.execute('''CREATE TABLE IF NOT EXISTS respo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            value TEXT
        );
        ''')




app = Flask(__name__)
app.secret_key = 'supersecret'

#initialize africastalking 
import africastalking
import sqlite3

# Africa's Talking setup
username = "sandbox"
api_key = "atsk_59e13e2d3ea2984cad5a658b8ff327d2bdb35b6eab7fbc1935aacafe9e2c6f8e984e3888"

africastalking.initialize(username, api_key)
from typing import Any

sms: Any = africastalking.SMS

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    current_data = {
        'time_in': '',
        'time_out': '',
        'email': '',
        'address': '',
        'phone': ''
    }

    if request.method == 'POST':
        time_in = request.form['time_in'].strip()
        time_out = request.form['time_out'].strip()
        email = request.form['email'].strip()
        address = request.form['address'].strip()
        phone = request.form['phone'].strip()
        c.execute("SELECT id, username, email, phone, profile_photo FROM users")
        users = c.fetchall()

                # Convert to list of dicts for easier use in Jinja
        user_list = [
                    {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'phone': user[3],
                        'profile_photo': user[4]
                    }
        for user in users
                ]

        try:
            # Check if there's an existing record (you can change logic if needed)
            c.execute('SELECT id FROM policy LIMIT 1')
            existing = c.fetchone()

            if existing:
                c.execute('''
                    UPDATE policy
                    SET time_in = ?, time_out = ?, email = ?, address = ?, phone = ?
                    WHERE id = ?
                ''', (time_in, time_out, email, address, phone, existing[0]))
            else:
                c.execute('''
                    INSERT INTO policy (time_in, time_out, email, address, phone)
                    VALUES (?, ?, ?, ?, ?)
                ''', (time_in, time_out, email, address, phone))



            conn.commit()

            flash('✅ Settings updated successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'❌ Error: {str(e)}', 'danger')

    # For GET or after POST to fetch current data
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




def get_admin_phone():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = 'admin_phone'")
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def send_sms(message):
    phone = get_admin_phone()
    if phone:
        try:
            response = sms.send(message, [phone])
            print("SMS sent:", response)
        except Exception as e:
            print("SMS failed:", str(e))
    else:
        print("No phone number found for admin.")



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

        conn = sqlite3.connect('furniture.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
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
        c.execute("UPDATE users SET password = ? WHERE username = ?", (new_hash, username))
        conn.commit()
        conn.close()

        session.pop('allow_reset', None)
        flash(f"✅ Password successfully updated for {username}", "success")
        return redirect(url_for('login'))

    return render_template('reset.html')

#attendance


from flask import jsonify

@app.route('/check_in', methods=['POST'])
@app.route('/check_in', methods=['POST'])
def check_in():
    staff_id = request.form['id']
    date = datetime.today().strftime('%d-%m-%Y')
    time_in = datetime.today().strftime('%H:%M:%S')

    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    # Check if already checked in today
    c.execute('SELECT * FROM attendance WHERE staff_id = ? AND date = ?', (staff_id, date))
    member = c.fetchone()
    if member:
        conn.close()
        return jsonify({"status": "error", "message": "Already checked in today"}), 400
    member_name = member[0] if member else 'Unknown'

    # Continue to insert
    ...


    # Insert check-in
    c.execute('''
        INSERT INTO attendance (staff_id, member, date, check_in_time, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (staff_id, member_name, date, time_in, 'Checked In'))
    conn.commit()
    conn.close()

    # Optional: SMS Notification
    number = get_admin_phone()
    message = f"{member_name} was checked in at {time_in}"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
            print("SMS failed:", e)

    # Return check-in time to frontend
    return jsonify({"status": "success", "time_in": time_in})

from flask import jsonify

@app.route('/check_out', methods=['POST'])
def check_out():
    staff_id = request.form['id']
    date = datetime.today().strftime('%d-%m-%Y')
    time_out = datetime.today().strftime('%H:%M:%S')
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    c.execute('SELECT check_in_time FROM attendance WHERE staff_id = ? AND date = ?', (staff_id, date))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Check-in not found for today."}), 400

    time_in = row[0]

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

    c.execute('SELECT COUNT(*) FROM attendance WHERE staff_id = ?', (staff_id,))
    total_days = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM attendance WHERE staff_id = ? AND status IN ("Present", "Late")', (staff_id,))
    present_days = c.fetchone()[0]
    attendance_rate = round((present_days / total_days) * 100, 2) if total_days else 0.0

    c.execute('''
        UPDATE attendance
        SET check_out_time = ?, lateness_minutes = ?, early_leave_minutes = ?, 
            worked_hours = ?, status = ?, attendance_rate = ?
        WHERE staff_id = ? AND date = ?
    ''', (time_out, lateness, early_leave, worked_hours, status, attendance_rate, staff_id, date))

    conn.commit()
    conn.close()

    # SMS (optional)
    try:
        number = get_admin_phone()
        if number:
            sms.send(f"{staff_id} checked out at {time_out}", [number])
    except:
        pass

    return jsonify({
        "status": "success",
        "check_out_time": time_out,
        "worked_hours": worked_hours,
        "status_text": status,
        "attendance_rate": attendance_rate
    })

@app.route('/attendance_view')
def attendance_view():
    conn = sqlite3.connect('furniture.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    today = datetime.today().strftime('%d-%m-%Y')

    # Fetch all members
    c.execute('SELECT name, company_id FROM members')
    all_members = c.fetchall()

    # Fetch today’s attendance
    c.execute('SELECT * FROM attendance WHERE date = ?', (today,))
    attendance_data = {row['staff_id']: row for row in c.fetchall()}

    # Merge members and today's attendance
    table_data = []
    for member in all_members:
        staff_id = member['company_id']
        attendance_row = attendance_data.get(staff_id)

        row = {
            'staff_id': staff_id,
            'member': member['name'],
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
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    # Get members who have NOT checked in today
    c.execute('''
        SELECT name, company_id FROM members
        WHERE company_id NOT IN (
            SELECT staff_id FROM attendance WHERE date = ?
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

    conn = sqlite3.connect('furniture.db')
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
        VALUES (?, ?, ?, ?, ?, ?)
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


@app.route('/create_user', methods=['GET', 'POST'])
def register():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    # Count existing users
    c.execute('SELECT COUNT(*) FROM users')
    user_count = c.fetchone()[0]

    if user_count >= 2:
        conn.close()
        return "Maximum number of users already registered."

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Hash in production!
        email = request.form['email']
        phone = request.form['phone']
        photo = request.files['profile_photo']  # <-- match the form field name

        profile_photo_path = None
        if photo and photo.filename and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            profile_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(profile_photo_path)

        hashed_password = generate_password_hash(password)

        try:
            c.execute('INSERT INTO users (username, password, profile_photo, email, phone) VALUES (?, ?, ?, ?, ?)', (username, hashed_password, profile_photo_path, email, phone))
            conn.commit()
            conn.close()
            return redirect(url_for('normal_user'))  # or home/dashboard
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already taken."

    conn.close()
    return render_template('create_user.html')

from werkzeug.security import check_password_hash



@app.route('/', methods=['GET', 'POST'])  # Login
def normal_user():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()

        if user:
            stored_hash = user[2]  # assuming password is column 3 (index 2)

            if check_password_hash(stored_hash, password):
                session['user'] = username
                conn.close()
                return redirect(url_for('dashboard'))  # or homepage
            else:
                conn.close()
                return "Wrong password"
        else:
            conn.close()
            return "User does not exist"

    return render_template('login.html')


@app.route('/add_damagedinfo', methods=['GET', 'POST'])
def add_damagedinfo():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    if request.method == 'POST':
        date = datetime.today().strftime('%Y-%m-%d')
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'] or 1)
        selling_price = float(request.form['selling_price'] or 0)
        reason = request.form['reason']

        # Fetch product info
        c.execute('SELECT quantity, buying_price,  name FROM stock_info WHERE id = ?', (product_id,))
        result = c.fetchone()

        if not result:
            conn.close()
            return "Product not found."

        stock_quantity, buying_price, product_name = result

        if stock_quantity < quantity:
            conn.close()
            return f"Only {stock_quantity} items available in stock."

        # Calculate loss
 
        # Record damaged stock
        c.execute('''INSERT INTO damaged_info
                     ( product_id, date, name, quantity, buying_price, selling_price, loss, reason)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  ( product_id, date, product_name, quantity, buying_price, selling_price,  reason))

        # Update stock
        c.execute('UPDATE stock_info SET quantity = quantity - ? WHERE id = ?', (quantity, product_id))

        conn.commit()
        conn.close()

        # SMS Notification
        number = get_admin_phone()
        message = f"Damaged stock recorded: {product_name}, Quantity: {quantity}, Date: {date}"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:", e)
        else:
            print("No admin number found")

        return redirect(url_for('view_damagedinfo'))

    # On GET, fetch products for the dropdown
    c.execute('SELECT id, name FROM stock_info')
    products = c.fetchall()
    conn.close()

    return render_template('add_damagedinfo.html', products=products)


#view damaged_info
@app.route('/view_damagedinfo')
def view_damagedinfo():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('SELECT * FROM damaged_info')
    damagedinfo = c.fetchall()
    conn.commit()
    conn.close()
    return render_template('view_damagedinfo.html', damagedinfo=damagedinfo)

@app.route('/edit_damagedinfo/<int:id>', methods=['GET', 'POST'])
def edit_damagedinfo(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'] or 1)
        selling_price = float(request.form['selling_price'] or 0)
        buying_price = float(request.form['buying_price'] or 0)
        reason = request.form['reason']
        loss = abs((buying_price - selling_price) * quantity)

        # Fixed: Make sure the columns and values align exactly
        c.execute('''
            UPDATE damaged_info 
            SET name = ?, quantity = ?, buying_price = ?, selling_price = ?, loss = ?, reason = ?
            WHERE id = ?
        ''', (name, quantity, buying_price, selling_price, loss, reason, id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_damagedinfo'))

    else:
        c.execute('SELECT * FROM damaged_info WHERE id = ?', (id,))
        damaged_item = c.fetchone()
        conn.close()

        if damaged_item:
            product = {
                'id': damaged_item[0],
                'date': damaged_item[1],
                'name': damaged_item[2],
                'quantity': damaged_item[3],
                'buying_price': damaged_item[4],
                'selling_price': damaged_item[5],
                'loss': damaged_item[6],
                'reason': damaged_item[7]
            }
        else:
            product = None
        number = get_admin_phone()
        message = f"Damaged info was edited"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")

        return render_template('add_damagedinfo.html', product=product, form_action=url_for('edit_damagedinfo', id=id), button_text='Update Damaged Info')


#delete damagedinfo
@app.route('/delete_damagedinfo/<int:id>')
def delete_damagedinfo(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM damaged_info WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    number = get_admin_phone()
    message = f"Damaged info with ID: {id} was deleted"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
            print("SMS failed:",e)
    else:
        print("No admin number found")
    return redirect(url_for('view_damagedinfo'))

# ADD SALARY
@app.route('/add_salary', methods=['GET', 'POST'])
def add_salary():
    if request.method == 'POST':  # fixed
        date = datetime.today().strftime('%Y-%m-%d')
        employee_id = request.form['employee_id']
        salary_amount = request.form['salary_amount']
        status = request.form['status']
        conn = sqlite3.connect('furniture.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO salaries(date,employee_id, salary, status) VALUES (?, ?, ?, ?)',
                       (date, employee_id,  salary_amount, status))
        conn.commit()  # fixed
        conn.close()   # fixed
        number = get_admin_phone()
        message = f"Employee ID :{employee_id} salary was recorded"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")
        return redirect(url_for('view_salary'))
    return render_template('salaries.html')


# VIEW SALARY
@app.route('/view_salary')
def view_salary():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('SELECT * FROM salaries')
    salaries = c.fetchall()
    conn.close()  # fixed
    return render_template('payrolls.html', salaries=salaries, salary=None)

#generate payslip
@app.route('/generate_payslip', methods=['GET', 'POST'])
def generate_payslip():
    conn = sqlite3.connect('furniture.db')
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
            WHERE members.id = ?
            ORDER BY salaries.date DESC
            LIMIT 1
        """, (member_id,))
        data = cursor.fetchone()

        if data:
            name, basic_salary = data
            total_earnings = basic_salary + bonus + overtime + allowance + commission + leave_pay
            total_deductions = paye + others + advance + nhif
            net_pay = total_earnings - total_deductions

            # ✅ SMS after successful generation
            number = get_admin_phone()
            message = f"Payslip generated for {name} ({member_id})"
            if number:
                try:
                    sms.send(message, [number])
                except Exception as e:
                    print("SMS failed:", e)

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
    conn = sqlite3.connect('furniture.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        new_salary = request.form['salary_amount']
        new_status = request.form['status']
        cursor.execute('UPDATE salaries SET salary = ?, status = ? WHERE id = ?', (new_salary, new_status, id))
        conn.commit()
        conn.close()
        return redirect('/payrolls')  
    
    cursor.execute('SELECT * FROM salaries WHERE id = ?', (id,))
    salary = cursor.fetchone()
    conn.close()
    number = get_admin_phone()
    message = f"Employee ID :{id} salary's was edited"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
                print("SMS failed:",e)
    else:
        print("No admin number found")

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
        conn = sqlite3.connect('furniture.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()

        if not result or not check_password_hash(result[0], current_password):
            flash("Current password is incorrect.")
            conn.close()
            return redirect(url_for('change_password'))

        # Hash and update new password
        new_hashed = generate_password_hash(new_password)
        c.execute("UPDATE users SET password = ? WHERE username = ?", (new_hashed, username))
        conn.commit()
        conn.close()

        flash("Password changed successfully.")
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')


#CASH FLOW SYSTEM


@app.route('/edit_expense/<int:id>', methods=['POST', 'GET'])
def edit_expense(id):
    conn = sqlite3.connect('furniture.db')
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
                (SELECT SUM(salary) FROM salaries) AS salary,
                (SELECT SUM(buying_price * quantity) FROM sales) AS cost_of_goods
        ''')
        data = c.fetchone()
        salary = data[0] if data and data[0] is not None else  0
        cost_of_goods = data[1] if data and data[1] is not None else 0

        total_expenses = electricity + water + internet + rent + supplies + ads + insurance + maintenance + transport + taxes

        # ✅ Update expense with start/end date
        c.execute('''
            UPDATE expenses
            SET start_date = ?, end_date = ?, salaries = ?, cost_of_good = ?, electricity = ?, water = ?, internet = ?, rent = ?, supplies = ?, ads = ?, insuarance = ?, maintanance = ?, transport = ?, taxes = ?, total_expenses = ?
            WHERE id = ?
        ''', (start_date, end_date, salary, cost_of_goods, electricity, water, internet, rent, supplies, ads, insurance, maintenance, transport, taxes, total_expenses, id))

        conn.commit()
        conn.close()

        flash('✅ Expense updated successfully!', 'success')
        return redirect(url_for('view_expense'))

    # 👉 GET request: fetch existing expense
    c.execute('SELECT * FROM expenses WHERE id = ?', (id,))
    expense = c.fetchone()
    conn.close()

    return render_template('record_expense.html', expense=expense)


@app.route('/view_expenses')
def view_expense():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('SELECT * FROM expenses')
    expenses = c.fetchall()
    c.close()
    return render_template('account.html', expenses=expenses)

@app.route('/create_expense', methods=['GET', 'POST'])
def create_expense():
    conn = sqlite3.connect('furniture.db')
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
            SELECT 
                (SELECT SUM(salary) FROM salaries) AS salary,
                (SELECT SUM(buying_price * quantity) FROM sales) AS cost_of_goods
        ''')
        result = c.fetchone()
        salary = result[0] if result and result[0] is not None else 0
        cost_of_goods = result[1] if result and result[1] is not None else 0

        total_expenses = (
            electricity + water + internet + rent + supplies + ads +
            insuarance + maintanance + transport + taxes
        )

        # Insert into PostgreSQL
        c.execute('''
            INSERT INTO expenses (
                start_date, end_date, salaries, cost_of_good, electricity, water, internet, rent,
                supplies, ads, insuarance, maintanance, transport, taxes, total_expenses
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            start_date, end_date, salary, cost_of_goods, electricity, water, internet,
            rent, supplies, ads, insuarance, maintanance, transport, taxes, total_expenses
        ))

        conn.commit()
        conn.close()

        flash('✅ Expense recorded successfully!', 'success')
        number = get_admin_phone()
        message = "New Expense was recorded"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")
        return redirect(url_for('view_expense'))

    return render_template('record_expense.html')


@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE id = ?',(id,))
    conn.commit()
    conn.close()
    number = get_admin_phone()
    message = f"{id} Expense was deleted"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
                print("SMS failed:",e)
    else:
        print("No admin number found")
    return redirect('/view_expenses')



#Add product stock info
@app.route('/add_stockinfo', methods=['POST', 'GET'])
def add_stockinfo():
    conn = sqlite3.connect('furniture.db')
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
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, supplier_name, supplier_contact, item_name, quantity, selling_price, buying_price))
        conn.commit()
        conn.close()
        number = get_admin_phone()
        message = "New Stock  was recorded"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")
        return redirect(url_for('view_stockinfo'))

    return render_template('add_productstock.html')

#view stock info
@app.route('/view_stockinfo')
def view_stockinfo():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('SELECT * FROM stock_info')
    stockinfo = c.fetchall()
    conn.close()
    return render_template('inventory.html', stockinfo=stockinfo)

#edit stock info
@app.route('/edit_stockinfo/<int:id>', methods=['POST', 'GET'])
def edit_stockinfo(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    if request.method == 'POST':
        date = datetime.today().strftime('%Y-%m-%d')
        supplier_name = request.form['supplier_name']
        supplier_contact = request.form['supplier_contact']
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'] or 1)
        selling_price = float(request.form['selling_price'] or 0)
        buying_price = float(request.form['buying_price'] or 0)
        number = get_admin_phone()
        message = f"{id} salary was edited"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")
        c.execute('''
            UPDATE stock_info
            SET date = ?, supplier_name = ?, supplier_contact = ?, item_name = ?, quantity = ?, selling_price = ?, buying_price = ?
            WHERE id = ?
        ''', (date, supplier_name, supplier_contact, item_name, quantity, selling_price, buying_price, id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_stockinfo'))

    else:
        c.execute('SELECT * FROM stock_info WHERE id = ?', (id,))
        row = c.fetchone()
        conn.close()

        if row:
            product = {
                'id': row[0],
                'date': row[1],
                'supplier_name': row[2],
                'supplier_contact': row[3],
                'item_name': row[4],
                'quantity': row[5],
                'selling_price': row[6],
                'buying_price': row[7]
                # Remove status if your table doesn’t have it
            }
        else:
            product = None

        return render_template('add_productstock.html', product=product, form_action=url_for('edit_stockinfo', id=id), button_text='Update Stock')

#delete stock info
@app.route('/delete_stockinfo/<int:id>')
def delete_stockinfo(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM stock_info WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    number = get_admin_phone()
    message = f"{id} salary was edited"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
            print("SMS failed:",e)
    else:
        print("No admin number found")    
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
@app.route('/accounting')
def accounting():
    if 'user' not in session:
        return redirect('/login')
    return render_template('account.html')

@app.route('/daily_income_expenses')
def daily_income_expenses():
    conn = sqlite3.connect('furniture.db')
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
        conn = sqlite3.connect('furniture.db')
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
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        investments = float(request.form.get('investments', 0) or 0)
        financial = float(request.form.get('financial', 0) or 0)
        notes = request.form.get('notes', '')

        conn = sqlite3.connect('furniture.db')
        c = conn.cursor()

        # Use ? placeholders for PostgreSQL
        c.execute('SELECT SUM(selling_price * quantity) FROM sales WHERE date BETWEEN ? AND ?', (start_date, end_date))
        inflow_result = c.fetchone()
        inflow = inflow_result[0] if inflow_result and inflow_result[0] is not None else 0

        c.execute('SELECT SUM(buying_price * quantity) FROM sales WHERE date BETWEEN ? AND ?', (start_date, end_date))
        outflow_result = c.fetchone()
        outflow = outflow_result[0] if outflow_result and outflow_result[0] is not None else 0

        c.execute('SELECT SUM(total_expenses) FROM expenses WHERE start_date >= ? AND end_date <= ?', (start_date, end_date))
        expenses_result = c.fetchone()
        expenses = expenses_result[0] if expenses_result and expenses_result[0] is not None else 0

        total_outflow = outflow + expenses + investments + financial
        net_cashflow = inflow - total_outflow

        # Insert data
        c.execute('''
            INSERT INTO cashflow (start_date, end_date, inflow, outflow, expenses, investments, financial, total_outflow, net_cashflow, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (start_date, end_date, inflow, outflow, expenses, investments, financial, total_outflow, net_cashflow, notes))

        conn.commit()
        conn.close()

        flash("✅ Cashflow report generated and saved!", "success")
        number = get_admin_phone()
        message = "New Cashflow was recorded"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")        
        return redirect(url_for('view_cashflow'))

    return render_template('cashflow.html')


@app.route('/view_cashflow')
def view_cashflow():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    c.execute('SELECT * FROM cashflow ORDER BY id DESC')
    reports = c.fetchall()

    conn.close()
    return render_template('account.html', reports=reports)

@app.route('/edit_cashflow/<int:id>', methods=['GET', 'POST'])
def edit_cashflow(id):
    conn = sqlite3.connect('furniture.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        new_start_date = request.form.get('start_date')
        new_end_date = request.form.get('end_date')
        new_investments = float(request.form.get('investments', 0) or 0)
        new_financial = float(request.form.get('financial', 0) or 0)
        new_notes = request.form.get('notes', '')

        # Recalculate inflow, outflow, expenses based on new dates
# inflow
        cursor.execute('SELECT SUM(selling_price * quantity) FROM sales WHERE date BETWEEN ? AND ?', (new_start_date, new_end_date))
        row = cursor.fetchone()
        inflow = row[0] if row and row[0] is not None else 0

        # outflow
        cursor.execute('SELECT SUM(buying_price * quantity) FROM sales WHERE date BETWEEN ? AND ?', (new_start_date, new_end_date))
        row = cursor.fetchone()
        outflow = row[0] if row and row[0] is not None else 0

        # expenses
        cursor.execute('SELECT SUM(total_expenses) FROM expenses WHERE start_date >= ? AND end_date <= ?', (new_start_date, new_end_date))
        row = cursor.fetchone()
        expenses = row[0] if row and row[0] is not None else 0

        total_outflow = outflow + expenses + new_investments + new_financial
        net_cashflow = inflow - total_outflow

        # ✅ Update the cashflow record
        cursor.execute('''
            UPDATE cashflow
            SET start_date = ?, end_date = ?, inflow = ?, outflow = ?, expenses = ?, investments = ?, financial = ?, total_outflow = ?, net_cashflow = ?, notes = ?
            WHERE id = ?
        ''', (new_start_date, new_end_date, inflow, outflow, expenses, new_investments, new_financial, total_outflow, net_cashflow, new_notes, id))

        conn.commit()
        conn.close()

        flash("✅ Cashflow report updated successfully!", "success")
        number = get_admin_phone()
        message = f"Cashflow:{id} salary was edited"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")
        return redirect('/view_cashflow')

    # Fetch the existing record for pre-filling the form
    cursor.execute('SELECT * FROM cashflow WHERE id = ?', (id,))
    report = cursor.fetchone()
    conn.close()
    if report:
        cashflow = {
            'id': report[0],
            'start_date': report[1],
            'end_date': report[2],
            'inflow': report[3],
            'outflow': report[4],
            'expenses': report[5],
            'investments': report[6],
            'financial': report[7],
            'total_outflow': report[8],
            'net_cashflow': report[9],
            'notes': report[10]
        }
    else:
        cashflow = {}

    return render_template('cashflow.html', cashflow=cashflow, form_action=url_for('edit_cashflow', id=id))

@app.route('/delete_cashflow/<int:id>')
def delete_cashflow(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM cashflow WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash("🗑️ Sale deleted successfully!", "success")
    number = get_admin_phone()
    message = f"Cashflow :{id} salary was deleted"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
            print("SMS failed:",e)
    else:
        print("No admin number found")
    return redirect('/view_cashflow')

#assign tasks and responsibilties@app.route('/assign_tasks', methods=['POST', 'GET'])
@app.route('/assign_tasks', methods=['POST', 'GET'])
def assign_tasks():
    if request.method == 'POST':
        conn = sqlite3.connect('furniture.db')
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

            c.execute('SELECT name FROM members WHERE company_id = ?', (company_id,))
            result = c.fetchone()
            if not result:
                flash("❌ Error: No employee found with that ID.", "danger")
                return redirect(url_for('assign_tasks'))
            name = result[0]

            for task, respo in zip(tasks, responsibilities):
                c.execute('INSERT INTO respo (name, company_id, respo, tasks, description, date_assigned) VALUES (?, ?, ?, ?, ?, ?)',
                          (name, company_id, respo, task, description, date_assigned))

            conn.commit()
            number = get_admin_phone()
            message = f"Member:{company_id} was assigned tasks"
            if number:
                try:
                    sms.send(message, [number])
                except Exception as e:
                    print("SMS failed:",e)
            else:
                print("No admin number found")
            flash("✅ Tasks assigned successfully!", "success")
            return redirect(url_for('view_tasks'))

        except Exception as e:
            flash(f"❌ Error: {e}", "danger")
        finally:
            conn.close()

    return render_template('assign_tasks.html')



@app.route('/check_tasks/<int:id>', methods=['GET', 'POST'])
def check_tasks(id):
    conn = sqlite3.connect('furniture.db')
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
                SET date_checked = ?, remarks = ?
                WHERE id = ?
            ''', (date_checked, remarks, id))
            conn.commit()
            flash("✅ Task checked and remarks saved!", "success")
            return redirect(url_for('view_tasks'))

        except Exception as e:
            flash(f"❌ Error: {e}", "danger")

    c.execute('SELECT * FROM respo WHERE id = ?', (id,))
    task = c.fetchone()
    conn.close()

    return render_template('check_task.html', task=task)

 

@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        task = request.form['task']
        respo = request.form['respo']
        description = request.form['description']
        remarks = request.form['remarks']
        date_checked = request.form['date_checked']

        c.execute('''
            UPDATE respo
            SET tasks = ?, respo = ?, description = ?, remarks = ?, date_checked = ?
            WHERE id = ?
        ''', (task, respo, description, remarks, date_checked, id))

        conn.commit()
        conn.close()
        number = get_admin_phone()
        message = f"Member:{id} tasks were edited"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                    print("SMS failed:",e)
            else:
                print("No admin number found")
        flash("✅ Task updated successfully", "success")
        return redirect(url_for('view_tasks'))
    
    # GET request — load data into form
    c.execute('SELECT * FROM respo WHERE id = ?', (id,))
    files = c.fetchone()
    conn.close()
    return render_template('edit_task.html', files=files)
@app.route('/delete_task/<int:id>')
def delete_task(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM respo WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Task deleted successfully", "success")
    number = get_admin_phone()
    message = f"Member:{id}  tasks were deleted"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
                print("SMS failed:",e)
        else:
                print("No admin number found")
    return redirect(url_for('view_tasks'))

from collections import defaultdict

@app.route('/view_tasks')
def view_tasks():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('SELECT id, name, company_id, respo, tasks, date_assigned, date_checked, remarks, description FROM respo')
    rows = c.fetchall()
    conn.close()

    # Group by (name, company_id)
    grouped = defaultdict(list)
    for row in rows:
        key = (row[1], row[2])  # name, company_id
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

#SALES
@app.route('/dashboard_sales')
def dashboard_sales():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    # Fetch the latest 40 sales, ordered from oldest to newest
    c.execute("SELECT * FROM sales ORDER BY sale_id DESC LIMIT 40")
    recent_sales = c.fetchall()

    # Now reverse the list so the oldest (lowest ID) appears first
    sales = recent_sales[::-1]

    conn.close()

    return render_template('sales.html', sales=sales)

@app.route('/sale')
def sale():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    # Fetch the latest 40 sales, ordered from oldest to newest
    c.execute("SELECT * FROM sales ORDER BY sale_id DESC LIMIT 40")
    recent_sales = c.fetchall()

    # Now reverse the list so the oldest (lowest ID) appears first
    sales = recent_sales[::-1]

    conn.close()

    return render_template('receipt .html', sales=sales)

@app.route('/print_contract')
def print_contract():
    return render_template('contract.html')


#navigate from sales.html to record_sales.html
@app.route('/record_sales')
def record_sale():
    return render_template('record_sales.html')


@app.route('/record_sales', methods=["GET", "POST"])
def record_sales():
    if request.method == "POST":
        conn = sqlite3.connect('furniture.db')
        cur = conn.cursor()

        try:
            item_id = int(request.form['item_id'])
            quantity_sold = int(request.form['quantity'])
            selling_price = float(request.form['selling_price'])
            payment_method = request.form['payment']

            # Fetch product from stock_info by ID
            cur.execute("SELECT item_name, quantity, buying_price FROM stock_info WHERE rowid = ?", (item_id,))
            item = cur.fetchone()

            if not item:
                flash("❌ Error: Product with that ID not found.", "danger")
                return redirect(url_for('record_sales'))

            item_name, stock_qty, buying_price = item

            if quantity_sold > stock_qty:
                flash(f"❌ Not enough stock. Only {stock_qty} available.", "warning")
                return redirect(url_for('record_sales'))

            total_selling = selling_price * quantity_sold
            total_buying = buying_price * quantity_sold
            profit_or_loss = total_selling - total_buying
            date = datetime.now().strftime("%Y-%m-%d")

            # Save sale
            cur.execute("""
                INSERT INTO sales (item_id, item_name, quantity, selling_price, buying_price, payment, profit_or_loss, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item_name, quantity_sold, selling_price, buying_price, payment_method, profit_or_loss, date))

            # Update stock quantity
            new_qty = stock_qty - quantity_sold
            cur.execute("UPDATE stock_info SET quantity = ? WHERE rowid = ?", (new_qty, item_id))

            conn.commit()
            number = get_admin_phone()
            message = "New sale was recorded"
            if number:
                try:
                    sms.send(message, [number])
                except Exception as e:
                    print("SMS failed:",e)
            else:
                print("No admin number found")
            return redirect('/dashboard_sales')

        except ValueError:
            flash("❌ Please enter valid numeric values.", "danger")
        except Exception as e:
            flash(f"❌ Unexpected error: {str(e)}", "danger")
        finally:
            conn.close()

    return render_template(
        'record_sales.html',
        form_action=url_for('record_sales'),
        sale=None,
        button_text='Record Sale'
    )

@app.route('/edit_sales/<int:id>', methods=['GET', 'POST'])
def edit_sales(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    if request.method == 'POST':
        try:
            new_type = request.form.get('item_name', '')  # This is read-only field when editing
            new_quantity = int(request.form.get('quantity', 0))
            new_selling_price = float(request.form.get('selling_price', 0))
            new_payment = request.form.get('payment', '')
            new_buying_price = float(request.form.get('buying_price', 0))

            new_total_buying = new_buying_price * new_quantity
            new_total_selling = new_selling_price * new_quantity
            new_profit_or_loss = new_total_selling - new_total_buying

            # Update the sale
            c.execute("""
                UPDATE sales
                SET item_name = ?, quantity = ?, selling_price = ?, payment = ?, buying_price = ?, profit_or_loss = ?
                WHERE sale_id = ?
            """, (new_type, new_quantity, new_selling_price, new_payment, new_buying_price, new_profit_or_loss, id))

            conn.commit()
            number = get_admin_phone()
            message = f"Sales:{id} were edited"
            if number:
                try:
                    sms.send(message, [number])
                except Exception as e:
                    print("SMS failed:",e)
            else:
                print("No admin number found")
            return redirect('/dashboard_sales')

        except Exception as e:
            flash(f"❌ Error: {e}", "danger")
        finally:
            conn.close()

    # GET method: fetch existing sale record
    c.execute('SELECT * FROM sales WHERE sale_id = ?', (id,))
    sale_row = c.fetchone()
    conn.close()

    if not sale_row:
        flash('❌ Sale not found.', 'danger')
        return redirect('/dashboard_sales')

    sale = {
        'id': sale_row[0],
        'type': sale_row[2],  # item_name
        'quantity': sale_row[3],
        'selling_price': sale_row[4],
        'payment': sale_row[6],
        'buying_price': sale_row[5]
    }

    return render_template(
        'record_sales.html',
        form_action=url_for('edit_sales', id=id),
        sale=sale,
        items=[],  # still pass this to avoid template error
        button_text = 'Update Sale'
    )

@app.route('/delete_sales/<int:id>', methods=['POST', 'GET'])
def delete_sales(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM sales WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    number = get_admin_phone()
    message = f"Sales:{id} were deleted"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
            print("SMS failed:",e)
    else:
        print("No admin number found")
    return redirect('/dashboard_sales')


#daily summary
@app.route('/daily_summary')
def daily_summary():
    conn = sqlite3.connect('furniture.db')
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
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute("""
        SELECT
              strftime('%Y-%W', date) as week,
            SUM(selling_price * quantity) AS total_sales,
            SUM(CASE WHEN (selling_price * quantity) > (buying_price * quantity)
                     THEN (selling_price * quantity) - (buying_price * quantity)
                     ELSE 0 END) AS profit,
            SUM(CASE WHEN (selling_price * quantity) < (buying_price * quantity)
                     THEN (buying_price * quantity) - (selling_price * quantity)
                     ELSE 0 END) AS loss,
            SUM(quantity) AS items_sold
            FROM sales
            GROUP BY week
            ORDER BY week DESC
            """)
    weekly_sales = c.fetchall()
    conn.close()
    return render_template('sales.html',
                       sales=[],
                       summary=[],
                       weekly_summary=weekly_sales,
                       monthly_summary=[],
                       page=1,
                       total_pages=1)

#monthly summary
@app.route('/monthly_summary')
def monthly_summary():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute("""
        SELECT
              strftime('%Y-%m', date) as month,
            SUM(selling_price * quantity) AS total_sales,
            SUM(CASE WHEN (selling_price * quantity) > (buying_price * quantity)
                     THEN (selling_price * quantity) - (buying_price * quantity)
                     ELSE 0 END) AS profit,
            SUM(CASE WHEN (selling_price * quantity) < (buying_price * quantity)
                     THEN (buying_price * quantity) - (selling_price * quantity)
                     ELSE 0 END) AS loss,
            SUM(quantity) AS items_sold
            FROM sales
            GROUP BY month
            ORDER BY month DESC
            """)
    monthly_sales = c.fetchall()
    conn.close()
    return render_template('sales.html',
                       sales=[],
                       summary=[],
                       weekly_summary=[],
                       monthly_summary=monthly_sales,
                       page=1,
                       total_pages=1)



#MEMBERS
@app.route('/members')
def members():
    if 'user' not in session:
        return redirect('/login')
    conn = sqlite3.connect('furniture.db')
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
        conn = sqlite3.connect('furniture.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM members WHERE name=? AND phone=? AND company_id=?", (name, phone, company_id))
        existing = cur.fetchone()

        if existing:
            flash("❗ Member already exists.", "error")
            conn.close()
            return redirect("/add_member")

        # Insert new member
        cur.execute("INSERT INTO members (name, phone, role, company_id, status, email,  profile_photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, phone, role, company_id, status, email, photo_filename))
        conn.commit()
        conn.close()
        number = get_admin_phone()
        message = f"Member:{company_id} was registered to the company"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")
        flash("✅ Member added successfully.", "success")
        return redirect(url_for('view_members'))

    return render_template("add_member.html", form_action=url_for('add_member'), person=None)

# Edit Member (Update)
@app.route('/edit_member/<int:id>', methods=['GET', 'POST'])
def edit_member(id):
    conn = sqlite3.connect('furniture.db')
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
            c.execute('UPDATE members SET name = ?, phone = ?, role = ?, company_id = ?, status = ?, email = ?, profile_photo = ? WHERE id = ?', 
                      (name, phone, role, company_id, status, responsibility, photo_filename, id))
        else:
            # Without changing photo
            c.execute('UPDATE members SET name = ?, phone = ?, role = ?, company_id = ?, status = ?, email = ? WHERE id = ?', 
                      (name, phone, role, company_id, status, responsibility, id))

        conn.commit()
        conn.close()
        number = get_admin_phone()
        message = f"Member:{company_id} info was edited"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")
        flash("✅ Member updated successfully.", "success")
        return redirect(url_for('view_members'))

    # GET request - load member data
    c.execute('SELECT * FROM members WHERE id = ?', (id,))
    mem = c.fetchone()
    conn.close()

    person = {
        'id': mem[0],
        'name': mem[1],
        'phone': mem[2],
        'role': mem[3],
        'company_id': mem[4],
        'responsibilities': mem[5],
        'status': mem[6],
        'profile_photo': mem[7] if len(mem) > 7 else None
    } if mem else None

    return render_template('add_member.html', form_action=url_for('edit_member', id=id), person=person)


# View Members Page (for table)
@app.route('/members')
def view_members():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('SELECT * FROM members')
    members = c.fetchall()
    conn.close()
    return render_template('view_members.html', members=members)

@app.route("/delete/<int:id>")
def delete_member(id):  # Added 'id' as a function argument
    conn = sqlite3.connect('furniture.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM members WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Member deleted successfully.", "success")
    number = get_admin_phone()
    message = f"Member:{id} was deleted"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
            print("SMS failed:",e)
    else:
        print("No admin number found")
    return redirect("/members")



@app.route("/search", methods=["GET"])
def search_members():
    keyword = request.args.get("q", "")
    conn = sqlite3.connect('furniture.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM members WHERE name LIKE ? OR role LIKE ?",
                (f"%{keyword}%", f"%{keyword}%"))
    members = cur.fetchall()
    conn.close()
    return render_template("members.html", members=members)


@app.route("/sort")
def sort_members():
    by = request.args.get("by", "id")
    order = request.args.get("order", "asc").upper()
    conn = sqlite3.connect('furniture.db')
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

        conn = sqlite3.connect('furniture.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO invoices (customer_name, total_price) VALUES (?, ?) RETURNING id",
            (name, total)
        )
        result = cursor.fetchone()
        if result:
            invoice_id = result[0]

            for i in range(len(item_type)):
                if item_type[i].strip() == "" or item_quantity[i].strip() == "" or selling_price[i].strip() == "":
                    continue
                cursor.execute(
                    "INSERT INTO invoice_items (invoice_id, item_type, item_quantity, selling_price, status) VALUES (?, ?, ?, ?, ?)",
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
    conn = sqlite3.connect('furniture.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM invoices")
    invoices = cursor.fetchall()

    invoice_data = []
    for inv in invoices:
        cursor.execute("""
            SELECT item_type, item_quantity, selling_price, status
            FROM invoice_items
            WHERE invoice_id = ?
        """, (inv[0],))  # assuming invoice ID is at index 0
        items = cursor.fetchall()
        invoice_data.append({'invoice': inv, 'items': items})

    conn.close()
    return render_template('invoicing.html', data=invoice_data)





# --- EDIT INVOICE ---
@app.route('/edit_invoice/<int:id>', methods=['GET', 'POST'])
def edit_invoice(id):
    conn = sqlite3.connect('furniture.db')
    cursor = conn.cursor()

    # Fetch invoice and items
    cursor.execute('SELECT * FROM invoices WHERE id = ?', (id,))
    invoice = cursor.fetchone()

    cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = ?', (id,))
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

        cursor.execute("UPDATE invoices SET customer_name = ?, total_price = ? WHERE id = ?", 
                       (customer_name, new_total, id))

        cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (id,))

        added_any = False
        for t, q, p in zip(item_type, quantity, price):
            if t.strip() and q.strip() and p.strip():
                cursor.execute("""
                    INSERT INTO invoice_items (invoice_id, item_type, item_quantity, selling_price, status)
                    VALUES (?, ?, ?, ?, ?)
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
        conn = sqlite3.connect('furniture.db')
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM invoices WHERE id = ?', (id,))
        invoice = cursor.fetchone()
        if not invoice:
            conn.close()
            return jsonify({'success': False, 'message': 'Invoice not found'}), 404

        cursor.execute('DELETE FROM invoice_items WHERE invoice_id = ?', (id,))
        cursor.execute('DELETE FROM invoices WHERE id = ?', (id,))

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
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        time = request.form['time']
        c.execute("INSERT INTO meetings (title, date, time) VALUES (?, ?, ?)", (title, date, time))
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

    conn = sqlite3.connect('furniture.db')
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

        conn = sqlite3.connect('furniture.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO contracts (title, description, status, client_name, client_contact, contract_amount, date_assigned)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, status, client_name, client_contact, contract_amount, date_assigned))
        conn.commit()
        conn.close()
        number = get_admin_phone()
        message = "New contract was added"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
            else:
                print("No admin number found")

        return redirect(url_for('dashboard'))  

    return render_template('add_contract.html')  


@app.route('/add_expense/<int:contract_id>', methods=['GET', 'POST'])
def add_expense(contract_id):
    if request.method == 'POST':
        date = request.form['date']
        workers = float(request.form['workers'])
        materials = float(request.form['materials'])
        others = float(request.form['others'])

        conn = sqlite3.connect('furniture.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO contract_expenses (contract_id, date, workers, materials, others)
            VALUES (?, ?, ?, ?, ?)
        ''', (contract_id, date, workers, materials, others))
        conn.commit()
        conn.close()
        number = get_admin_phone()
        message = f"Expense of contract:{contract_id} recorded"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")

        return redirect(url_for('view_contracts'))

    return render_template('add_expense.html', contract_id=contract_id)


@app.route('/edit_contract/<int:id>', methods=['GET', 'POST'])
def edit_contract(id):
    conn = sqlite3.connect('furniture.db')
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
            SET title = ?, description = ?, status = ?, client_name = ?, client_contact = ?, contract_amount = ?, date_assigned = ?
            WHERE id = ?
        ''', (title, description, status, client_name, client_contact, contract_amount, date_assigned, id))

        conn.commit()
        conn.close()
        number = get_admin_phone()
        message = f"Expense of contract:{id} was edited"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")        
        return redirect(url_for('view_contracts', contract_id=id))

    # GET request - fetch the contract
    c.execute("SELECT * FROM contracts WHERE id = ?", (id,))
    contract = c.fetchone()
    conn.close()
    return render_template('add_contract.html', contract=contract)


@app.route('/view_contracts')
def view_contracts():
    conn = sqlite3.connect('furniture.db')
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
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()  

    if request.method == 'POST':
        date = request.form['date']
        workers = float(request.form['workers'])
        materials = float(request.form['materials'])
        others = float(request.form['others'])

        c.execute('''
            UPDATE contract_expenses
            SET date = ?, workers = ?, materials = ?, others = ?
            WHERE id = ?
        ''', (date, workers, materials, others, id))

        # Get contract ID to redirect
        c.execute("SELECT contract_id FROM contract_expenses WHERE id = ?", (id,))
        contract_row = c.fetchone()
        conn.commit()
        conn.close()

        contract_id = contract_row['contract_id'] if contract_row else None
        return redirect(url_for('view_contracts', contract_id=contract_id))

    # GET method – fetch data to populate form
    c.execute("SELECT * FROM contract_expenses WHERE id = ?", (id,))
    expense = c.fetchone()
    conn.close()
    number = get_admin_phone()
    message = f"Expense of contract:{id} was edited"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
            print("SMS failed:",e)
    else:
        print("No admin number found")
    return render_template('add_expense.html', expense=expense)


@app.route('/delete_contract_expense/<int:id>')
def delete_contract_expense(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    c.execute("SELECT contract_id FROM contract_expenses WHERE id = ?", (id,))
    row = c.fetchone()
    if row:
        contract_id = row['contract_id']
        c.execute("DELETE FROM contract_expenses WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_contracts', contract_id=contract_id))
    else:
        conn.close()
        number = get_admin_phone()
        message = f"Expense of contract:{id} was deleted"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                    print("SMS failed:",e)
        else:
                print("No admin number found")
        return "Contract expense not found", 404


@app.route('/delete_contract/<int:id>')
def delete_contract(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()  # Added DictCursor for consistency

    c.execute("SELECT * FROM contracts WHERE id = ?", (id,))
    contract = c.fetchone()

    if contract:
        c.execute("DELETE FROM contracts WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_contracts'))
    else:
        conn.close()
        number = get_admin_phone()
        message = f"contract:{id} was deleted"
        if number:
            try:
                sms.send(message, [number])
            except Exception as e:
                print("SMS failed:",e)
        else:
            print("No admin number found")        
        return "Contract not found", 404





@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('furniture.db')
    cur = conn.cursor()  # ✅ Use DictCursor directly

    # Unpaid Invoices

    cur.execute("SELECT username, email, phone, profile_photo FROM users WHERE username = ?", (session['user'],))
    user_data = cur.fetchone()
    conn.close()

    user = {
        'username': user_data[0],
        'email': user_data[1],
        'phone': user_data[2],
        'profile_photo': user_data[3] or 'default.jpg'  # fallback photo
    }


    # Top & Least Sellers


    return render_template(
        'dashboard.html',
        username=session.get('username', 'Guest'), user=user
    )

@app.route('/new_dashboard')
def new_dashboard():
        conn = sqlite3.connect('furniture.db')
        cur = conn.cursor()
        cur.execute("""
        SELECT invoices.id, invoices.customer_name, invoices.total_price, invoices.date
        FROM invoices
        JOIN invoice_items ON invoices.id = invoice_items.invoice_id
        WHERE invoice_items.status = 'not paid'
        GROUP BY invoices.id, invoices.customer_name, invoices.total_price, invoices.date
        LIMIT 3
        """)
        unpaid_invoices = [{
        'id': row['id'],
        'customer_name': row['customer_name'],
        'total_price': row['total_price'],
        'date': row['date'].strftime('%Y-%m-%d'),  # ✅ Safe date format
        'status': 'Unpaid'
        } for row in cur.fetchall()]

    # Contracts
        cur.execute("""
            SELECT id, title, client_name, status
            FROM contracts
            ORDER BY date_assigned DESC
            LIMIT 3
        """)
        contract_snaps = [{
            'id': row['id'],
            'title': row['title'],
            'client_name': row['client_name'],
            'status': row['status']
        } for row in cur.fetchall()]

        # Meetings
        cur.execute("""
            SELECT title, date, time
            FROM meetings
            ORDER BY date ASC, time ASC
            LIMIT 5
        """)
        meetings = cur.fetchall()
        cur.execute('''
            SELECT type, SUM(quantity) as total_quantity
            FROM sales
            GROUP BY type
            ORDER BY total_quantity DESC
        ''')
        sales_data = cur.fetchall()

        top_sellers = sales_data[:2]
        least_sellers = sales_data[-2:] if len(sales_data) >= 2 else []

        conn.close()
        return render_template('new_dashboard.html',
                                unpaid_invoices=unpaid_invoices,
                                contract_snaps=contract_snaps,        
                                top_sellers=top_sellers,
                                least_sellers=least_sellers, 
                                meetings=meetings)


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

        conn = sqlite3.connect('furniture.db')
        c = conn.cursor()
        c.execute("""
            SELECT 
                SUM(selling_price * quantity), 
                SUM(buying_price * quantity),
                SUM(profit_or_loss)
            FROM sales 
            WHERE date = ?
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


def get_db_connection():
    conn = sqlite3.connect('furniture.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/receipt/<int:receipt_no>')
def render_receipt(receipt_no):
    conn = get_db_connection()
    sales = conn.execute('SELECT * FROM sales WHERE sale_id = ?', (receipt_no,)).fetchall()
    conn.close()

    if not sales:
        return "No receipt found."

    sale = sales[0]  # if only 1 item, you can also use directly
    # Assume 16% tax
    subtotal = sale['quantity'] * sale['selling_price']
    tax = round(subtotal * 0.16, 2)
    grand_total = round(subtotal + tax, 2)

    return render_template('receipt.html',
                           sale=sales,
                           date=sale['date'],
                           receipt_no=sale['sale_id'],
                           customer_no=1000 + sale['sale_id'],  # example customer number
                           subtotal=subtotal,
                           tax=tax,
                           grand_total=grand_total)

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

            conn = sqlite3.connect('furniture.db')
            c = conn.cursor()
            c.execute('''
                    INSERT INTO furniture (name, quantity, selling_price, buying_price, image_path) 
                    VALUES (?, ?, ?, ?, ?)''',
                    (name, quantity, selling_price, buying_price, image_path))
            conn.commit()
            number = get_admin_phone()
            message = "New Product recorded"
            if number:
                try:
                    sms.send(message, [number])
                except Exception as e:
                    print("SMS failed:",e)
            else:
                print("No admin number found")           

        return redirect(url_for('view_products'))

    # If GET request → Show the form
    return render_template('add_product.html')


# Route: View all products
@app.route('/view_products')
def view_products():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('SELECT * FROM furniture')
    items = c.fetchall()
    c.close()
    conn.close()
    return render_template('view_products.html', items=items)
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM furniture WHERE id = ?', (product_id,))
    conn.commit()
    number = get_admin_phone()
    message = f"Product :{id} was deleted"
    if number:
        try:
            sms.send(message, [number])
        except Exception as e:
            print("SMS failed:",e)
    else:
        print("No admin number found")
    return redirect(url_for('view_products'))

#Edit product
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    if request.method == 'POST':
            name = request.form.get('name')
            quantity = request.form.get('quantity')
            selling_price = request.form.get('selling_price')
            buying_price = request.form.get('buying_price')
            c.execute('''
                UPDATE furniture 
                SET name=?, quantity=?, selling_price=?, buying_price=?
                WHERE id=?
            ''', (name, quantity, selling_price, buying_price, product_id))
            conn.commit()
            number = get_admin_phone()
            message = f"Product:{product_id} was edited"
            if number:
                try:
                    sms.send(message, [number])
                except Exception as e:
                    print("SMS failed:",e)
            else:
                print("No admin number found")
            return redirect(url_for('view_products'))

    c.execute('SELECT * FROM furniture WHERE id=?', (product_id,))
    row = c.fetchone()
    if row:
            product = {
                'id': row[0],
                'name': row[1],
                'quantity': row[2],
                'selling_price': row[3],
                'buying_price': row[4],
                'image_path': row[5]
            }
    else:
        product = None

    c.close()
    conn.close()

    return render_template('add_product.html', form_action=url_for('edit_product', product_id=product_id), button_text='Update Product', product=product)


# Optional: Logout route

if __name__ == '__main__':
    init_db()
    app.run(debug=True)



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

