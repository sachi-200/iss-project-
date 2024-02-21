from flask import Flask, render_template, request, redirect, jsonify, url_for
import mysql.connector
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_jwt_extended import set_access_cookies

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Set your JWT secret key
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "query_string", "json"]
jwt = JWTManager(app)

# MySQL Configuration
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'spnpft267'
mysql_db = 'user'

def initialize_user_table():
    try:
        db = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_db
        )
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS userdetails(serialnumber INT NOT NULL AUTO_INCREMENT PRIMARY KEY, user VARCHAR(1000), email VARCHAR(1000), username VARCHAR(1000), password VARCHAR(300))")
        db.commit()
        cur.close()
        db.close()
    except mysql.connector.Error as e:
        print(f"Error initializing database: {e}")

initialize_user_table()

def initialize_project_table():
    try:
        db = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_db
        )
        cur = db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS projects (
                        project_number INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        FOREIGN KEY (user_id) REFERENCES userdetails(serialnumber),
                        image1_link VARCHAR(1000),
                        image2_link VARCHAR(1000),
                        image3_link VARCHAR(1000),
                        image4_link VARCHAR(1000),
                        image5_link VARCHAR(1000),
                        image1_duration INT,
                        image2_duration INT,
                        image3_duration INT,
                        image4_duration INT,
                        image5_duration INT,
                        audio1_link VARCHAR(1000),
                        audio2_link VARCHAR(1000),
                        audio3_link VARCHAR(1000),
                        audio1_duration INT,
                        audio2_duration INT,
                        audio3_duration INT,
                        audio1_starting_time INT,
                        audio2_starting_time INT,
                        audio3_starting_time INT,
                        overlay_text1 VARCHAR(1000),
                        overlay_text2 VARCHAR(1000),
                        overlay_text3 VARCHAR(1000)
                        )""")
        db.commit()
        cur.close()
        db.close()
    except mysql.connector.Error as e:
        print(f"Error initializing project table: {e}")

initialize_project_table()

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_db
        )
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_users(query):
    try:
        db = get_db_connection()
        if db:
            cur = db.cursor()
            cur.execute(query)
            result = cur.fetchall()
            cur.close()
            db.close()
            return result
        else:
            return None
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    
def store_users(query, data):
    try:
        db = get_db_connection()
        if db:
            cur = db.cursor()
            cur.execute(query, data)
            db.commit()
            cur.close()
            db.close()
            return True
        else:
            return False
    except Exception as e:
        print(f"Error executing query: {e}")
        return False

def insert_project(data):
    try:
        db = get_db_connection()
        if db:
            cur = db.cursor()
            cur.execute("""INSERT INTO projects 
                            (user_id, image1_link, image2_link, image3_link, image4_link, image5_link,
                             image1_duration, image2_duration, image3_duration, image4_duration, image5_duration,
                             audio1_link, audio2_link, audio3_link, audio1_duration, audio2_duration, audio3_duration,
                             audio1_starting_time, audio2_starting_time, audio3_starting_time,
                             overlay_text1, overlay_text2, overlay_text3) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                         data)
            db.commit()
            cur.close()
            db.close()
            return True
        else:
            print("Database connection error.")
            return False
    except Exception as e:
        print(f"Error inserting project record: {e}")
        return False

def get_user_projects(user_id):
    try:
        db = get_db_connection()
        if db:
            cur = db.cursor()
            cur.execute("SELECT * FROM projects WHERE user_id = %s", (user_id,))
            projects = cur.fetchall()
            cur.close()
            db.close()
            return projects
        else:
            print("Database connection error.")
            return None
    except Exception as e:
        print(f"Error retrieving user projects: {e}")
        return None

@app.route('/')
def mainpage():
    return render_template('mainpage.html')

@app.route('/admin')
def admin():
    admin_details="SELECT serialnumber, user, username, email FROM userdetails"
    users = get_users(admin_details)
    return render_template('admin.html', users=users)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == "POST":
        data = request.form
        user = data["username"]
        password = data["password"]
        login_query = "SELECT * FROM userdetails WHERE username=%s AND password=%s"
        user_details = get_users(login_query, (user, password))
        if user_details:
            # Generate JWT token
            resp = jsonify(login=True)
            access_token = create_access_token(identity=user)
            set_access_cookies(resp, access_token)
            return redirect(url_for('userdetails')) 
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        data = request.form
        user = data["user"]
        email = data["email"]
        username = data["username"]
        password = data["password"]
        register_details_query = "INSERT INTO userdetails (user, email, username, password) VALUES (%s, %s, %s, %s)"
        if store_users(register_details_query, (user, email, username, password)):
            # Generate JWT token
            access_token = create_access_token(identity=user)
            resp = jsonify(login=True)
            set_access_cookies(resp, access_token)
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/userdetails')
@jwt_required()  # Protect this route with JWT authentication
def userdetails():
    user_details_query = "SELECT username, email FROM userdetails WHERE serialnumber = %s"
    user_id = get_jwt_identity()
    user_details_result = get_users(user_details_query, (user_id,))
    
    if user_details_result:
        user_details = user_details_result[0]
    else:
        return "User not found"

    return render_template('userdetails.html', user_details=user_details)

@app.route('/new_project', methods=['GET', 'POST'])
@jwt_required()  # Protect this route with JWT authentication
def new_project():
    if request.method == 'POST':
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        # Retrieve project details from the form data
        # Adjust these lines to retrieve all the project details from the form
        data = (
            user_id,
            request.form['image1_link'],
            request.form['image2_link'],
            request.form['image3_link'],
            request.form['image4_link'],
            request.form['image5_link'],
            request.form['image1_duration'],
            request.form['image2_duration'],
            request.form['image3_duration'],
            request.form['image4_duration'],
            request.form['image5_duration'],
            request.form['audio1_link'],
            request.form['audio2_link'],
            request.form['audio3_link'],
            request.form['audio1_duration'],
            request.form['audio2_duration'],
            request.form['audio3_duration'],
            request.form['audio1_starting_time'],
            request.form['audio2_starting_time'],
            request.form['audio3_starting_time'],
            request.form['overlay_text1'],
            request.form['overlay_text2'],
            request.form['overlay_text3']
        )
        # Insert the new project record into the database
        if insert_project(data):
            return redirect(url_for('project_page'))
        else:
            return "Failed to create project."
    return render_template('new_project.html')

@app.route('/project_page')
@jwt_required()  # Protect this route with JWT authentication
def project_page():
    user_id = get_jwt_identity()
    projects = get_user_projects(user_id)
    return render_template('project_page.html', projects=projects)

if __name__ == '__main__':
    app.run(debug=True)
