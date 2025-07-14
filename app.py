from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
import traceback
from flask import jsonify
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = 'supersecret'

# DB INIT



#add damaged info
@app.route('/add_damagedinfo', methods=['POST', 'GET'])
def add_damagedinfo():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    if request.method == 'POST':
        date = datetime.today().strftime('%Y-%m-%d')
        name = request.form['name']
        quantity = int(request.form['quantity'] or 1)
        buying_price = float(request.form['buying_price'] or 0 )
        selling_price = float(request.form['selling_price'] or 0)
        loss = (buying_price  - selling_price ) * quantity
        los = abs(loss)
        reason = request.form['reason']
        c.execute('INSERT INTO damaged_info(date, name, quantity, buying_price, selling_price, loss, reason) VALUES ( ?, ?, ?, ?, ?, ?, ?)', 
                  (date, name, quantity, buying_price, selling_price, los,  reason))
        conn.commit()
        conn.close()
        return redirect(url_for('view_damagedinfo'))
    return render_template('add_damagedinfo.html')

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

        return render_template('add_damagedinfo.html', product=product, form_action=url_for('edit_damagedinfo', id=id), button_text='Update Damaged Info')


#delete damagedinfo
@app.route('/delete_damagedinfo/<int:id>')
def delete_damagedinfo(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM damaged_info WHERE id = ?', (id,))
    conn.commit()
    conn.close()
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
        advance = float(request.form['advance_loan'])
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
            total_earnings = basic_salary + bonus +overtime + allowance + commission + leave_pay
            total_deductions = paye + others + paye + advance + nhif
            net_pay = total_earnings - total_deductions

            return render_template('payrolls.html', name=name, member_id=member_id, payment_date=payment_date, allowance=allowance, commission=commission,
                                   basic_salary=basic_salary, bonus=bonus, total_earnings=total_earnings, nhif=nhif, advance=advance, bank_name=bank_name,
                                   paye=paye , others=others,overtime=overtime, total_deductions=total_deductions, net_pay=net_pay)
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Fetch user from database
        conn = sqlite3.connect('furniture.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()

        if result and check_password_hash(result[0], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))

    return render_template('login.html')

from werkzeug.security import generate_password_hash
import sqlite3

def create_default_user():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    # Check if user already exists
    c.execute("SELECT id FROM users WHERE username = ?", ("secretary",))
    if not c.fetchone():
        hashed_pw = generate_password_hash("1234")
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("secretary", hashed_pw))
        conn.commit()
        print("✅ Default user 'secretary' created.")
    else:
        print("ℹ️ User 'secretary' already exists.")

    conn.close()



from werkzeug.security import generate_password_hash, check_password_hash

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
def get_db_connection():
    conn = sqlite3.connect('furniture.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn

@app.route('/create_expense', methods=['GET', 'POST'])
def create_expense():
    conn = sqlite3.connect('furniture.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if request.method == 'POST':
        date = datetime.today().strftime('%Y-%m-%d')
        electricity = float(request.form['electricity'] or 0)
        water = float(request.form['water'] or 0)
        internet = float(request.form['internet'] or 0)
        rent = float(request.form['rent'] or 0)
        supplies = float(request.form['supplies'] or 0)
        ads = float(request.form['ads'] or 0)
        insuarance = float(request.form['insuarance'] or 0) 
        maintanance = float(request.form['maintanance'] or 0)
        transport = float(request.form['transport'] or 0)
        taxes = float(request.form['taxes'] or 0)
        c.execute('''SELECT 
                (SELECT SUM(salary) FROM salaries) AS salary,
                (SELECT SUM(buying_price * quantity) FROM sales) AS cost_of_goods''')
        data = c.fetchone()
        salary, cost_of_goods = data[0] or 0, data[1] or 0
        if data:
            total_expenses = electricity + water+ internet + rent+ supplies + ads + insuarance + maintanance + transport + taxes
            c.execute('''INSERT INTO expenses (date, salaries, cost_of_good, electricity, water, internet, rent, supplies, ads, insuarance, maintanance, transport, taxes, total_expenses) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''', (date, salary, cost_of_goods, electricity, water, internet, rent, supplies, ads, insuarance, maintanance, transport, taxes, total_expenses))
        conn.commit()
        conn.close()

        flash('Expense recorded successfully!', 'success')
        return redirect(url_for('view_expense'))

    return render_template('record_expense.html')  
@app.route('/view_expenses')
def view_expense():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('SELECT * FROM expenses')
    expenses = c.fetchall()
    c.close()
    return render_template('account.html', expenses=expenses)

@app.route('/edit_expense/<int:id>', methods=['POST', 'GET'])
def edit_expense(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    if request.method == 'POST':
        date = datetime.today().strftime('%Y-%m-%d')
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
        salary = data[0] or 0
        cost_of_goods = data[1] or 0

        total_expenses = electricity + water + internet + rent + supplies + ads + insurance + maintenance + transport + taxes

        # ✅ Update the existing expense row
        c.execute('''
            UPDATE expenses
            SET date = ?, salaries = ?, cost_of_good = ?, electricity = ?, water = ?, internet = ?, rent = ?, supplies = ?, ads = ?, insuarance = ?, maintanance = ?, transport = ?, taxes = ?, total_expenses = ?
            WHERE id = ?
        ''', (date, salary, cost_of_goods, electricity, water, internet, rent, supplies, ads, insurance, maintenance, transport, taxes, total_expenses, id))

        conn.commit()
        conn.close()

        flash('✅ Expense updated successfully!', 'success')
        return redirect(url_for('view_expense'))

    # 👉 GET request: fetch existing expense to prefill the form
    c.execute('SELECT * FROM expenses WHERE id = ?', (id,))
    expense = c.fetchone()
    conn.close()

    return render_template('record_expense.html', expense=expense)

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE id = ?',(id,))
    conn.commit()
    conn.close()
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
    return redirect(url_for('view_stockinfo'))



#navigate from dashboard to members

#navigate from dashboard to sales
@app.route('/sales')
def sales():
    return render_template('sales.html')

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

        c.execute('SELECT SUM(selling_price * quantity) FROM sales WHERE date BETWEEN ? AND ?', (start_date, end_date))
        inflow = c.fetchone()[0] or 0

        c.execute('SELECT SUM(buying_price * quantity) FROM sales WHERE date BETWEEN ? AND ?', (start_date, end_date))
        outflow = c.fetchone()[0] or 0

        c.execute('SELECT SUM(total_expenses) FROM expenses WHERE date BETWEEN ? AND ?', (start_date, end_date))
        expenses = c.fetchone()[0] or 0

        total_outflow = outflow + expenses + investments + financial
        net_cashflow = inflow - total_outflow

        c.execute('''
            INSERT INTO cashflow (start_date, end_date, inflow, outflow, expenses, investments, financial, total_outflow, net_cashflow, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (start_date, end_date, inflow, outflow, expenses, investments, financial, total_outflow, net_cashflow, notes))

        conn.commit()
        conn.close()

        flash("✅ Cashflow report generated and saved!", "success")
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
        cursor.execute('SELECT SUM(selling_price * quantity) FROM sales WHERE date BETWEEN ? AND ?', (new_start_date, new_end_date))
        inflow = cursor.fetchone()[0] or 0

        cursor.execute('SELECT SUM(buying_price * quantity) FROM sales WHERE date BETWEEN ? AND ?', (new_start_date, new_end_date))
        outflow = cursor.fetchone()[0] or 0

        cursor.execute('SELECT SUM(total_expenses) FROM expenses WHERE date BETWEEN ? AND ?', (new_start_date, new_end_date))
        expenses = cursor.fetchone()[0] or 0

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
        return redirect('/view_cashflow')

    # Fetch the existing record for pre-filling the form
    cursor.execute('SELECT * FROM cashflow WHERE id = ?', (id,))
    report = cursor.fetchone()
    conn.close()

    return render_template('cashflow.html', report=report)

@app.route('/delete_cashflow/<int:id>')
def delete_cashflow(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM cashflow WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash("🗑️ Sale deleted successfully!", "success")
    return redirect('/view_cashflow')



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
#show all sales from the dashboard sales
@app.route('/dashboard_sales')
def dashboard_sales():
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sales')
    sales = c.fetchall()
    conn.close()
    return render_template('sales.html', sales=sales)

#navigate from sales.html to record_sales.html
@app.route('/record_sales')
def record_sale():
    return render_template('record_sales.html')


# Record Sales
@app.route('/record_sales', methods=["GET", "POST"])
def record_sales():
    if request.method == "POST":
        item_type = request.form['type']
        quantity = int(request.form['quantity'])
        selling_price = float(request.form['selling_price'])
        payment_method = request.form['payment']
        buying_price = float(request.form['buying_price'])

        total_buying = buying_price * quantity
        total_selling = selling_price * quantity
        profit_or_loss = total_selling - total_buying
        date = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect("furniture.db")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sales (type, quantity, selling_price, payment, buying_price, profit_or_loss, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (item_type, quantity, selling_price, payment_method, buying_price, profit_or_loss, date))
        conn.commit()
        conn.close()

        flash("✅ Sale recorded successfully!", "success")
        return redirect('/dashboard_sales')  

    return render_template('record_sales.html', form_action=url_for('record_sales'), sale=None, button_text='Record Sale')


@app.route('/edit_sales/<int:id>', methods=['GET', 'POST'])
def edit_sales(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    if request.method == 'POST':
        new_type = request.form['type']
        new_quantity = int(request.form['quantity'])
        new_selling_price = float(request.form['selling_price'])
        new_payment = request.form['payment']
        new_buying_price = float(request.form['buying_price'])

        new_total_buying = new_buying_price * new_quantity
        new_total_selling = new_selling_price * new_quantity
        new_profit_or_loss = new_total_selling - new_total_buying

        # ✅ This is the correct UPDATE query
        c.execute("""
            UPDATE sales
            SET type = ?, quantity = ?, selling_price = ?, payment = ?, buying_price = ?, profit_or_loss = ?
            WHERE id = ?
        """, (new_type, new_quantity, new_selling_price, new_payment, new_buying_price, new_profit_or_loss, id))

        conn.commit()
        conn.close()

        flash("✅ Sale updated successfully!", "success")
        return redirect('/dashboard_sales')

    # Fetch existing sale to pre-fill form
    c.execute('SELECT * FROM sales WHERE id = ?', (id,))
    sale_row = c.fetchone()
    conn.close()

    sale = {
        'id': sale_row[0],
        'type': sale_row[1],
        'quantity': sale_row[2],
        'selling_price': sale_row[3],
        'payment': sale_row[4],
        'buying_price': sale_row[5],
    }

    return render_template('record_sales.html', form_action=url_for('edit_sales', id=id), sale=sale, button_text='Update Sale')

@app.route('/delete_sales/<int:id>', methods=['POST', 'GET'])
def delete_sales(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()
    c.execute('DELETE FROM sales WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash("🗑️ Sale deleted successfully!", "success")
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
    return render_template('sales.html', summary=summary)



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
    return render_template('sales.html', weekly_sales=weekly_sales)

#monthly summary
@app.route('/monthly_summary')
def monthly_summary():
    conn =sqlite3.connect('furniture.db')
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
    return render_template('sales.html', monthly_sales=monthly_sales)   



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


# Add Member (Create)
@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        role = request.form["role"]
        company_id = request.form["company_id"]
        responsibility = request.form['responsibility']
        status = request.form['status']

        conn = sqlite3.connect("furniture.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM members WHERE name=? AND phone=? AND company_id=?", (name, phone, company_id))
        existing = cur.fetchone()

        if existing:
            flash("❗ Member already exists.", "error")
            conn.close()
            return redirect("/add_member")

        cur.execute("INSERT INTO members (name, phone, role, company_id, responsibilities, status) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, phone, role, company_id, responsibility, status))
        conn.commit()
        conn.close()
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
        responsibility = request.form['responsibility']
        status = request.form['status']

        c.execute('UPDATE members SET name = ?, phone = ?, role = ?, company_id = ?, responsibilities = ?, status = ? WHERE id = ?', 
                  (name, phone, role, company_id, responsibility, status, id))

        conn.commit()
        conn.close()
        flash("✅ Member updated successfully.", "success")
        return redirect(url_for('view_members'))

    else:
        c.execute('SELECT * FROM members WHERE id = ?', (id,))
        mem = c.fetchone()
        conn.close()

        if mem:
            person = {
                'id': mem[0],
                'name': mem[1],
                'phone': mem[2],
                'role': mem[3],
                'company_id': mem[4],
                'responsibilities': mem[5],
                'status': mem[6]
            }
        else:
            person = None

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
    conn = sqlite3.connect("furniture.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM members WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Member deleted successfully.", "success")
    return redirect("/members")



@app.route("/search", methods=["GET"])
def search_members():
    keyword = request.args.get("q", "")
    conn = sqlite3.connect("furniture.db")
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
    conn = sqlite3.connect("furniture.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM members ORDER BY {by} {order}")
    members = cur.fetchall()
    conn.close()
    return render_template("members.html", members=members)


#INVOICE AND QUOTATIONS


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

        # Insert into invoices table — no status here, safe
        cursor.execute(
            "INSERT INTO invoices (customer_name, total_price) VALUES (?, ?)",
            (name, total)
        )
        invoice_id = cursor.lastrowid

        # Insert invoice items with status
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

    return render_template('create_invoice.html')



# Route to show all invoices
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
        """, (inv[0],))
        items = cursor.fetchall()
        invoice_data.append({'invoice': inv, 'items': items})

    conn.close()
    return render_template('invoicing.html', data=invoice_data)




#edit invoice
@app.route('/edit_invoice/<int:id>', methods=['GET', 'POST'])
def edit_invoice(id):
    conn = sqlite3.connect('furniture.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch the invoice and items
    invoice = cursor.execute('SELECT * FROM invoices WHERE id = ?', (id,)).fetchone()
    items = cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = ?', (id,)).fetchall()

    if request.method == 'POST':
        # Get updated data from the form
        customer_name = request.form['customer_name']
        item_type = request.form.getlist('item_type[]')
        quantity = request.form.getlist('quantity[]')      
        price = request.form.getlist('price[]')            
        status = request.form['status']

        # Calculate new total
        new_total = 0
        for a, b in zip(quantity, price):
            if a.strip() and b.strip():
                new_total += int(a) * float(b)

        # Update main invoice
        cursor.execute("UPDATE invoices SET customer_name = ?, total_price = ? WHERE id = ?", (customer_name, new_total, id))

        # Remove old items
        cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (id,))

        # Safe insert using zip
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

#delete invoice


@app.route('/delete_invoice/<int:id>', methods=['POST'])
def delete_invoice(id):
    try:
        conn = sqlite3.connect('furniture.db')
        cursor = conn.cursor()

        # Check if the invoice exists
        invoice = cursor.execute('SELECT id FROM invoices WHERE id = ?', (id,)).fetchone()
        if not invoice:
            conn.close()
            return jsonify({'success': False, 'message': 'Invoice not found'}), 404

        # Delete associated items first
        cursor.execute('DELETE FROM invoice_items WHERE invoice_id = ?', (id,))
        # Delete the invoice
        cursor.execute('DELETE FROM invoices WHERE id = ?', (id,))

        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Invoice deleted successfully'})

    except sqlite3.Error as e:
        conn.close()
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500
    




UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)





def init_db():
    with sqlite3.connect('furniture.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS furniture
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT, 
                      quantity INTEGER,
                      selling_price REAL, 
                      buying_price REAL,
                      image_path TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS damaged_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            name TEXT,
            quantity REAL,
            buying_price REAL,
            selling_price REAL,
            loss REAL,
            reason TEXT
    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS stock_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            supplier_name TEXT,
            supplier_contact TEXT,
            item_name TEXT,
            quantity REAL,
            selling_price REAL,
            buying_price REAL,
            status REAL
                  )''')
        c.execute('''CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY,
        name TEXT,
        phone TEXT,
        role TEXT,
        company_id INTEGER,
        status TEXT,
        responsibilities TEXT
    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        quantity INTEGER,
        selling_price REAL,
        payment TEXT,
        buying_price REAL,
        profit_or_loss REAL,
        date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS meetings(
        id INTEGER PRIMARY KEY,
            title TEXT,
            date TEXT,
            time TEXT
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
    c.execute('''CREATE TABLE IF NOT EXISTS quotations (
        id INTEGER PRIMARY KEY,
            customer_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status DEFAULT 'pending'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            total_price INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            invoice_id INTEGER,
            item_quantity INTEGER NOT NULL,
            selling_price INTEGER NULL,
            is_paid INTEGER DEFAULT 0,
            status TEXT DEFAULT 'not paid',
            created_at INTEGER DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS quotations_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_id INTEGER,
            item_type TEXT,
            quantity INTEGER,
            price REAL,
            total REAL
    )''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS cashflow (
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
        )
    ''')
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
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
      )''')
    c.execute('''CREATE TABLE IF NOT EXISTS salaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            employee_id INTEGER,
            salary REAL,
            status TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    status TEXT,
    client_name TEXT,
    client_contact TEXT,
    contract_amount REAL,
    date_assigned TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS contract_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            date TEXT,
            workers REAL,
            materials REAL,
            others REAL,
            balance REAL,
            profit_or_loss REAL,
            daily_outflow REAL,
            FOREIGN KEY (contract_id) REFERENCES contracts(id)
            )''')
    conn.commit()


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

        return redirect(url_for('dashboard'))  # or wherever you list contracts

    return render_template('add_contract.html')  # GET request: show the form

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

        # 👇 Redirect to the all-contracts page
        return redirect(url_for('view_contracts'))

    return render_template('add_expense.html', contract_id=contract_id)

@app.route('/edit_contract/<int:id>', methods=['GET', 'POST'])
def edit_contract(id):
    conn = sqlite3.connect('furniture.db')
    conn.row_factory = sqlite3.Row
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
        return redirect(url_for('view_contracts', contract_id=id))  # Redirect back to view

    # GET request - fetch the contract
    c.execute("SELECT * FROM contracts WHERE id = ?", (id,))
    contract = c.fetchone()
    conn.close()
    return render_template('add_contract.html', contract=contract)

@app.route('/view_contracts')
def view_contracts():
    conn = sqlite3.connect('furniture.db')
    conn.row_factory = sqlite3.Row
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
    conn.row_factory = sqlite3.Row
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

        conn.commit()
        # Get contract ID to redirect back to view page
        c.execute("SELECT contract_id FROM contract_expenses WHERE id = ?", (id,))
        contract_id = c.fetchone()['contract_id']
        conn.close()
        return redirect(url_for('view_contracts', contract_id=contract_id))

    # GET form
    c.execute("SELECT * FROM contract_expenses WHERE id = ?", (id,))
    expense = c.fetchone()
    conn.close()
    return render_template('add_expense.html', expense=expense)

@app.route('/delete_contract_expense/<int:id>')
def delete_contract_expense(id):
    conn = sqlite3.connect('furniture.db')
    conn.row_factory = sqlite3.Row
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
        return "Contract expense not found", 404

@app.route('/delete_contract/<int:id>')
def delete_contract(id):
    conn = sqlite3.connect('furniture.db')
    c = conn.cursor()

    # Optional: Check if the contract exists before deleting
    c.execute("SELECT * FROM contracts WHERE id = ?", (id,))
    contract = c.fetchone()

    if contract:
        c.execute("DELETE FROM contracts WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_contracts'))
    else:
        conn.close()
        return "Contract not found", 404


    
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("furniture.db")
    conn.row_factory = sqlite3.Row  # 👈 MUST come before cursor
    cur = conn.cursor()

    # Unpaid invoice data
    cur.execute("SELECT DISTINCT invoice_id FROM invoice_items WHERE status = 'not paid'")
    unpaid_invoice_ids = [row[0] for row in cur.fetchall()]
    unpaid_count = len(unpaid_invoice_ids)

    unpaid_invoices = []
    for invoice_id in unpaid_invoice_ids[:3]:
        cur.execute("SELECT id, customer_name, total_price, date FROM invoices WHERE id = ?", (invoice_id,))
        row = cur.fetchone()
        if row:
            unpaid_invoices.append({
                'id': row['id'],
                'customer_name': row['customer_name'],
                'total_price': row['total_price'],
                'date': row['date'],
                'status': 'Unpaid'
            })

    # Low stock items (fix here)
    cur.execute("SELECT id, item_name, quantity FROM stock_info WHERE quantity <= 5 ORDER BY quantity ASC")
    low_stock_items = cur.fetchall()

    conn.close()

    return render_template('dashboard.html',
        unpaid_count=unpaid_count,
        unpaid_invoices=unpaid_invoices,
        low_stock_items=low_stock_items  # ✅ now this works
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

        conn = sqlite3.connect("furniture.db")
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

        sales = row[0] if row[0] else 0
        cost = row[1] if row[1] else 0
        profit = row[2] if row[2] else 0
        predicted_val = sales + 1000  # Simple placeholder logic

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

            with sqlite3.connect('furniture.db') as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO furniture (name, quantity, selling_price, buying_price, image_path) 
                    VALUES (?, ?, ?, ?, ?)''',
                    (name, quantity, selling_price, buying_price, image_path))
                conn.commit()

        return redirect(url_for('view_products'))

    # If GET request → Show the form
    return render_template('add_product.html')


# Route: View all products
@app.route('/view_products')
def view_products():
    with sqlite3.connect('furniture.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM furniture')
        items = c.fetchall()
    return render_template('view_products.html', items=items)  # Make sure this template exists too
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    with sqlite3.connect('furniture.db') as conn:
        c = conn.cursor()
        c.execute('DELETE FROM furniture WHERE id = ?', (product_id,))
        conn.commit()
    return redirect(url_for('view_products'))

#Edit product
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    with sqlite3.connect('furniture.db') as conn:
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
            return redirect(url_for('view_products'))
        else:
            c.execute('SELECT * FROM furniture WHERE id=?', (product_id,))
            row = c.fetchone()
            product = {
                'id': row[0],
                'name': row[1],
                'quantity': row[2],
                'selling_price': row[3],
                'buying_price': row[4],
                'image_path': row[5]
            }
    return render_template('add_product.html', form_action=url_for('edit_product', product_id=product_id), button_text='Update Product', product=product)


# Optional: Logout route


# Initialize the database when the app starts
if __name__ == '__main__':
    init_db()
    create_default_user()
    app.run(debug=True)



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

