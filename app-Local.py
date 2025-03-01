from flask import Flask, request, render_template, redirect, session, url_for, flash
import pymysql
import os
import bcrypt
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from appsettings.env
load_dotenv("appsettings.env")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key')

# MySQL configuration
db_host = os.getenv('DB_HOST_Local')
db_user = os.getenv('DB_USER_Local')
db_password = os.getenv('DB_PASSWORD_Local')
db_name = os.getenv('DB_NAME_Local')

# Initialize MySQL connection with error handling
try:
    db = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
except pymysql.MySQLError as e:
    print(f"Error connecting to the database: {e}")
    exit(1)  # Exit if database connection fails

# Folder to store uploads
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    session.clear()  # Clear session data
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        image = request.files['image']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return redirect(url_for('index') + '?error=exists')  # Redirect with error

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image.save(file_path)
            relative_path = "uploads/{}".format(filename)

            try:
                cursor.execute(
                    "INSERT INTO users (name, email, password, image_url) VALUES (%s, %s, %s, %s)",
                    (name, email, hashed_password, relative_path)
                )
                db.commit()
                session['username'] = name
                session['email'] = email
                session['image_url'] = relative_path
                cursor.close()
                flash("Signup successful!")
                return redirect(url_for('welcome'))

            except Exception as e:
                db.rollback()
                flash(f"An error occurred during signup: {e}")
                return redirect(url_for('index') + '?error=signup_failed')

    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        cursor = db.cursor()
        cursor.execute("SELECT password, name, email, image_url FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            stored_password = result[0].encode('utf-8')
            if bcrypt.checkpw(password, stored_password):
                session['username'] = result[1]
                session['email'] = result[2]
                session['image_url'] = result[3]
                return redirect(url_for('welcome'))

        flash("Invalid Credentials!")
    
    return render_template('index.html')

@app.route('/welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    image_url = url_for('static', filename=session['image_url'])
    return render_template('welcome.html', username=session['username'], email=session['email'], image_url=image_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True  # Enable debug mode for development
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000)