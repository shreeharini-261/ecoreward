from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'damn',
    'database': 'ecorewards'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# User Class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = str(id)  # Ensure ID is stored as a string
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, username FROM users WHERE id = %s", (int(user_id),))  # Convert user_id to int
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()
        if user_data:
            return User(user_data[0], user_data[1])
    return None

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            connection.commit()
            cursor.close()
            connection.close()

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                print(f"DEBUG: User found -> {user}")  # Check if user is retrieved correctly
                if bcrypt.check_password_hash(user[1], password):
                    login_user(User(user[0], username))
                    print("DEBUG: Login successful!")  # Verify if login succeeds
                    return redirect(url_for('dashboard'))
                else:
                    print("DEBUG: Incorrect password")  # Check if password is wrong
                    flash("Invalid username or password", "danger")
            else:
                print("DEBUG: User not found")  # Debug if user is missing
                flash("Invalid username or password", "danger")

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    print(f"DEBUG: Current user -> {current_user}")  # Check if user is logged in
    print(f"DEBUG: Current user ID -> {current_user.id}")  

    connection = get_db_connection()
    data = None
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT total_rewards, activities_completed FROM dashboard WHERE user_id = %s", (current_user.id,))
        data = cursor.fetchone()
        cursor.close()
        connection.close()

    return render_template('dashboard.html', data=data)

@app.route('/rewards')
@login_required
def rewards():
    connection = get_db_connection()
    rewards = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT reward_name, points, earned_at FROM rewards WHERE user_id = %s", (current_user.id,))
        rewards = cursor.fetchall()
        cursor.close()
        connection.close()

    return render_template('rewards.html', rewards=rewards)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
