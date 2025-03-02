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

pip install flask git
pip install pymysql
pip install bcrypt
pip install python-dotenv
pip install boto3
pip install requests

Database setup
********************************************
https://dev.mysql.com/downloads/installer/
********************************************


netsh advfirewall firewall add rule name="Flask 5000" dir=in action=allow protocol=TCP localport=5000
