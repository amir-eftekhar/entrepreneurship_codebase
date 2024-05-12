from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)  
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Concern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_request
def create_tables():
    db.create_all()

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/")
def index():
    return redirect(url_for('home'))

@app.route("/home")
@login_required
def home():
    return render_template('home.html')

@app.route("/upload_image", methods=['GET', 'POST'])
@login_required
def upload_image():
    if request.method == 'POST':
        image = request.files['image']
        image_filename = image.filename
        image.save(f'static/uploads/{image_filename}')
        new_image = Image(image_file=image_filename, user_id=current_user.id)
        db.session.add(new_image)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('upload_image.html')

@app.route("/frequency_slider")
@login_required
def frequency_slider():
    return render_template('frequency_slider.html')

@app.route("/chatbot", methods=['GET', 'POST'])
@login_required
def chatbot():
    if request.method == 'POST':
        concern_text = request.form.get('concern')
        new_concern = Concern(text=concern_text, user_id=current_user.id)
        db.session.add(new_concern)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('chatbot.html')

if __name__ == "__main__":
    app.run(debug=True)
