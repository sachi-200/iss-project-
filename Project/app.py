from flask import *
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import *
from psycopg2 import *
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Set your JWT secret key
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "query_string", "json"]
app.config["JWT_COOKIE_SECURE"] = False
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=300)  # Set token expiration time
jwt = JWTManager(app)

# SQLAlchemy Configuration
Base = declarative_base()

def initialize_db(engine):
    Base.metadata.create_all(engine)

class User(Base):
    __tablename__ = 'users'

    serialnumber = Column(Integer, primary_key=True)
    email = Column(String(1000))
    username = Column(String(1000))
    password = Column(String(300))

def get_session():
    engine = create_engine("cockroachdb://amiabuch:j9qhBc5e8lpkUTGYdria_w@motion-al-9036.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full")
    Session = sessionmaker(bind=engine)
    return Session()

def initialize_user_table(session):
    session.execute(text("""CREATE TABLE IF NOT EXISTS users (
            serialnumber SERIAL PRIMARY KEY,
            email VARCHAR(1000),
            username VARCHAR(1000),
            password VARCHAR(300)
        )"""))
    session.commit()

def insert_user(session, user_data):
    new_user = User(**user_data)
    session.add(new_user)
    try:
        session.commit()
    except:
        session.rollback()
        raise
def get_user_by_username(session, username):
    return session.query(User).filter_by(username=username).first()

@app.route('/')
def mainpage():
    engine = create_engine("cockroachdb://amiabuch:j9qhBc5e8lpkUTGYdria_w@motion-al-9036.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full")
    initialize_db(engine)
    session = get_session()
    initialize_user_table(session)
    session.close()
    return render_template('mainpage.html')
@app.route('/admin')
def a():
    user_details_query = "SELECT * FROM users"
    session = get_session()
    result = session.execute(user_details_query)
    # s = result.fetchone()
    session.close()
    if result:
        return render_template("admin.html", users=result)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        data = request.form
        user_data = {
            "email": data["email"],
            "username": data["username"],
            "password": generate_password_hash(data["password"])
        }
        session = get_session()
        insert_user(session, user_data)
        session.close()
        # Generate JWT token
        access_token = create_access_token(identity=user_data["username"])
        resp = jsonify(login=True)
        set_access_cookies(resp, access_token)
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/new_project')
def np():
    return render_template("new_project.html")
@app.route('/project_page')
def p():
    return render_template("project_page.html")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        password = data["password"]
        session = get_session()
        user1 = get_user_by_username(session, username)
        session.close()    
        if user1 and check_password_hash(user1.password, password):
            # # Generate JWT token
            # access_token = create_access_token(identity=username)
            # resp = jsonify(login=True)
            # set_access_cookies(resp, access_token)
            access_token = create_access_token(identity=username)
            response = make_response(redirect(url_for('userdetails')))
            response.set_cookie('access_token_cookie', value=access_token, max_age=2592000, httponly=True)
            return response
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    return render_template('login.html')
@app.route('/editing')
def r():
    return render_template("editing.html")
@app.route('/userdetails')
@jwt_required()  # Protect this route with JWT authentication
def userdetails():
    user_details_query = "SELECT username, email FROM users WHERE serialnumber = %s"
    user_id = get_jwt_identity()
    session = get_session()
    user_details_result = session.execute(user_details_query, (user_id,))
    user_details = user_details_result.fetchone()
    session.close()

    if user_details:
        return render_template('userdetails.html', user_details=user_details)
    else:
        return "User not found"
@app.route('/linkandcontribution')
def c():
    return render_template("linkandcontribution.html")


if __name__ == "__main__":
    app.run(debug=True)