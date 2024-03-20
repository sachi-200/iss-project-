from flask import Flask, render_template, request, redirect, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import json

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
import os
from sqlalchemy import create_engine, text


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Set your JWT secret key
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "query_string", "json"]
jwt = JWTManager(app)

# MySQL Configuration
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    serialnumber = Column(Integer, primary_key=True)
    user = Column(String(1000))
    email = Column(String(1000))
    username = Column(String(1000))
    password = Column(String(300))

class Project(Base):
    __tablename__ = 'projects'

    project_number = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.serialnumber'))
    image1_link = Column(String(1000))
    image2_link = Column(String(1000))
    image3_link = Column(String(1000))
    image4_link = Column(String(1000))
    image5_link = Column(String(1000))
    image1_duration = Column(Integer)
    image2_duration = Column(Integer)
    image3_duration = Column(Integer)
    image4_duration = Column(Integer)
    image5_duration = Column(Integer)
    audio1_link = Column(String(1000))
    audio2_link = Column(String(1000))
    audio3_link = Column(String(1000))
    audio1_duration = Column(Integer)
    audio2_duration = Column(Integer)
    audio3_duration = Column(Integer)
    audio1_starting_time = Column(Integer)
    audio2_starting_time = Column(Integer)
    audio3_starting_time = Column(Integer)
    overlay_text1 = Column(String(1000))
    overlay_text2 = Column(String(1000))
    overlay_text3 = Column(String(1000))

def initialize_db(engine):
    Base.metadata.create_all(engine)

def get_session():
    engine = create_engine(os.environ["cockroachdb://amiabuch:AmiBuch@1805CDB@motion-al-9036.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"])
    Session = sessionmaker(bind=engine)
    return Session()

def initialize_user_table(session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS users (
            serialnumber SERIAL PRIMARY KEY,
            user VARCHAR(1000),
            email VARCHAR(1000),
            username VARCHAR(1000),
            password VARCHAR(300)
        )
    """)
    session.commit()

def initialize_project_table(session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_number SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(serialnumber),
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
        )
    """)
    session.commit()

def insert_user(session, user_data):
    new_user = User(**user_data)
    session.add(new_user)
    session.commit()

def insert_project(session, project_data):
    new_project = Project(**project_data)
    session.add(new_project)
    session.commit()

def get_user_projects(session, user_id):
    return session.query(Project).filter_by(user_id=user_id).all()


@app.route('/')
def mainpage():
    initialize_db()
    initialize_user_table()
    initialize_project_table()
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
        image1_link=request.form['image1_link']
        data = (
            user_id,
            image1_link,
            None,  # image2_link
            None,  # image3_link
            None,  # image4_link
            None,  # image5_link
            None,  # image1_duration
            None,  # image2_duration
            None,  # image3_duration
            None,  # image4_duration
            None,  # image5_duration
            None,  # audio1_link
            None,  # audio2_link
            None,  # audio3_link
            None,  # audio1_duration
            None,  # audio2_duration
            None,  # audio3_duration
            None,  # audio1_starting_time
            None,  # audio2_starting_time
            None,  # audio3_starting_time
            None,  # overlay_text1
            None,  # overlay_text2
            None,  # overlay_text3
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
