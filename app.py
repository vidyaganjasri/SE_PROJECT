from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Make sure this folder exists and is writable


# Upload folder config
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)

# ===== DATABASE SETUP =====
def init_db():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY, 
                        user_id INTEGER, 
                        type TEXT, 
                        title TEXT, 
                        description TEXT, 
                        image TEXT, 
                        category TEXT DEFAULT ''
                    )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT)''')

init_db()

# ===== USER CLASS =====
class User(UserMixin):
    def __init__(self, id_, username, role):
        self.id = id_
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    con.close()
    if row:
        return User(row[0], row[1], row[3])
    return None

# ===== ROUTES =====
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/Contact')
def contact_page():
    return render_template('Contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        con.close()

        if user is None:
            flash("User does not exist", "error")
        elif user['password'] != password:
            flash("Incorrect password", "error")
        else:
            user_obj = User(user['id'], user['username'], user['role'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # 'student', 'staff', 'admin'
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        con.commit()
        con.close()
        flash('Registered successfully. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row  # So you can do report['username']
    cur = con.cursor()
    notifications = []

    selected_category = request.args.get('category', None)

    if current_user.role == 'admin':
        if selected_category and selected_category != 'all':
            cur.execute("""
                SELECT reports.*, users.username FROM reports 
                JOIN users ON reports.user_id = users.id
                WHERE category = ?
            """, (selected_category,))
        else:
            cur.execute("SELECT reports.*, users.username FROM reports JOIN users ON reports.user_id = users.id")
        reports = cur.fetchall()
    else:
        cur.execute("SELECT * FROM reports WHERE user_id = ?", (current_user.id,))
        reports = cur.fetchall()
        cur.execute("SELECT message FROM notifications WHERE user_id = ?", (current_user.id,))
        notifications = cur.fetchall()

    con.close()

    categories = ['all', 'electronics', 'mobile phones', 'headphones', 'bags', 'stationary', 'gold', 'belongings']

    return render_template('dashboard.html', reports=reports, notifications=notifications, categories=categories, selected_category=selected_category)


@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    if current_user.role == 'admin':
        return "Admins cannot report items"

    categories = ['electronics', 'mobile phones', 'headphones', 'bags', 'stationary', 'gold', 'belongings']

    if request.method == 'POST':
        type_ = request.form['type']  # lost or found
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']

        image_file = request.files.get('image')
        image_filename = None

        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = filename

        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute(
            "INSERT INTO reports (user_id, type, title, description, image, category) VALUES (?, ?, ?, ?, ?, ?)",
            (current_user.id, type_, title, description, image_filename, category)
        )
        con.commit()
        con.close()
        flash('Report submitted')
        return redirect(url_for('dashboard'))

    return render_template('report.html', categories=categories)

@app.route('/edit_report/<int:report_id>', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    report = cur.fetchone()
    con.close()

    if not report:
        flash("Report not found.", "error")
        return redirect(url_for('dashboard'))

    if current_user.id != report[1]:
        flash("Access denied.", "error")
        return redirect(url_for('dashboard'))

    categories = ['electronics', 'mobile phones', 'headphones', 'bags', 'stationary', 'gold', 'belongings']

    if request.method == 'POST':
        type_ = request.form['type']
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']

        image_file = request.files.get('image')
        image_filename = report[5]  # existing image filename

        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = filename

        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute(
            "UPDATE reports SET type = ?, title = ?, description = ?, image = ?, category = ? WHERE id = ?",
            (type_, title, description, image_filename, category, report_id)
        )
        con.commit()
        con.close()
        flash("Report updated successfully!")
        return redirect(url_for('dashboard'))

    # Prepare report as dict for template
    report_dict = {
        'id': report[0],
        'user_id': report[1],
        'type': report[2],
        'title': report[3],
        'description': report[4],
        'image': report[5],
        'category': report[6],
    }
    return render_template('edit_report.html', report=report_dict, categories=categories)

@app.route('/delete_report/<int:report_id>', methods=['POST'])
@login_required
def delete_report_route(report_id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    report = cur.fetchone()

    if not report:
        flash("Report not found.", "error")
        return redirect(url_for('dashboard'))

    if current_user.id != report[1]:
        flash("Access denied.", "error")
        return redirect(url_for('dashboard'))

    cur.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    con.commit()
    con.close()
    flash("Report deleted successfully!")
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/notify/<int:report_id>', methods=['POST'])
@login_required
def notify(report_id):
    message = request.form.get('message')
    if not message:
        return "Message is required", 400

    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # Assuming you want to save the notification message for the user who owns the report
    # First find the user_id of the report
    cur.execute("SELECT user_id FROM reports WHERE id = ?", (report_id,))
    row = cur.fetchone()
    if row is None:
        con.close()
        return "Report not found", 404

    user_id = row[0]

    # Insert the notification for the user
    cur.execute("INSERT INTO notifications (user_id, message) VALUES (?, ?)", (user_id, message))
    con.commit()
    con.close()

    # Redirect back to dashboard or wherever you want
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
