from flask import Flask, request, render_template, redirect, session, url_for, flash
import os
import requests
import boto3
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError

# Load environment variables from appsettings.env
load_dotenv("appsettings.env")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key')

# API Gateway Endpoints
API_SIGNUP_URL = "https://jp7satmpx0.execute-api.ap-south-2.amazonaws.com/Dev/DigiLib"
API_SIGNIN_URL = "https://jp7satmpx0.execute-api.ap-south-2.amazonaws.com/Dev/DilibSignin"

# S3 Configuration
S3_BUCKET = os.getenv('S3_Bucket_Name')
S3_REGION = os.getenv('AWS_Region')
#AWS_ACCESS_KEY_ID=os.getenv('AWS_KEY_ID')
#AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SEC_KEY_ID')
#AWS_REGION=os.getenv('AWS_Region')

# Initialize S3 Client
s3 = boto3.client('s3',region_name=S3_REGION)
#*s3 = boto3.client(
 #   's3',
 #   aws_access_key_id=AWS_ACCESS_KEY_ID,
 #   aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
 #   region_name=S3_REGION
#)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_s3(file, filename):
    """Upload file to S3 and return the public URL."""
    try:
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            filename,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
        )
        return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
    except NoCredentialsError:
        flash("AWS credentials not available.")
        return None
    except Exception as e:
        flash(f"S3 Upload Error: {str(e)}")
        return None

@app.route('/')
def index():
    """Render the login/signup page and clear session."""
    session.clear()
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        image = request.files['image']

        # Upload image to S3
        image_url = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_url = upload_to_s3(image, filename)

        # Call API Gateway (Lambda) for user signup
        payload = {
            "Fullname": name,
            "EmailId": email,
            "Password": password,
            "userimage": image_url
        }
        response = requests.get(API_SIGNUP_URL, params=payload)

        if response.status_code == 200:
            session['username'] = name
            session['email'] = email
            session['image_url'] = image_url
            flash("Signup successful!")
            return redirect(url_for('welcome'))
        else:
            flash("Signup failed! Try again.")

    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """Handle user signin."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Call API Gateway (Lambda) for user signin
        payload = {"EmailId": email, "Password": password}
        response = requests.get(API_SIGNIN_URL, params=payload)

        print("API Response:", response.text)  # Debugging

        if response.status_code == 200:
            data = response.json()
            session['username'] = data.get('Fullname')
            session['email'] = email
            
            # Ensure 'userimage' is not None or "None"
            image_url = data.get('userimage')
            session['image_url'] =  data.get('userimage')
            
            return redirect(url_for('welcome'))

        flash("Invalid Credentials!")

    return render_template('index.html')



@app.route('/welcome')
def welcome():
    """Render the welcome page after login."""
    if 'username' not in session:
        return redirect(url_for('index'))

    return render_template('welcome.html', username=session['username'], email=session['email'], image_url=session['image_url'])

@app.route('/logout')
def logout():
    """Clear session and redirect to index."""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True  # Enable debug mode for development
    app.run(host='0.0.0.0', port=5000)