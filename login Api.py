from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
import os

# Initialize app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Login configuration
app.config['SECRET_KEY'] = 'mysecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'youremail@gmail.com'
app.config['MAIL_PASSWORD'] = 'yourpassword'
mail = Mail(app)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password):
        self.email = email
        self.password = password

# User schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

# Create the database tables
db.create_all()

# Login manager loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Dashboard route (only accessible after login)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Send password reset link through email
def send_password_reset_link(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='youremail@gmail.com',
                  recipients=[user.email])
    msg.body = f'To reset your password, visit the following link: \n{url_for("reset_password", token=token, _external=True)}'
    mail.send(msg)

# Password reset route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        email = request.form['email']