Install MySQL for local DB settings:
**********************************************
https://dev.mysql.com/downloads/installer/

CREATE Database ccituserdb;
USE ccituserdb;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Install Python and related packages
*****************************************
https://www.python.org/downloads/
(use pip3 command for the Linux instances)
yum install -y git python3 python3-pip
pip3 install flask git
pip3 install pymysql
pip3 install bcrypt
pip3 install python-dotenv
pip3 install boto3
pip3 install requests

(optional)
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 app:app --daemon


Database setup
********************************************
https://dev.mysql.com/downloads/installer/
********************************************


netsh advfirewall firewall add rule name="Flask 5000" dir=in action=allow protocol=TCP localport=5000
