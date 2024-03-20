from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
import os
import psycopg2
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Set your JWT secret key
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "query_string", "json"]
jwt = JWTManager(app)

# MySQL Configuration
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
    engine = create_engine("cockroachdb://amiabuch:jaWHu24ejIX9F_vQ-KciWA@motion-al-9036.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full")
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
    # <use session>
        session.commit()
    except:
        session.rollback()
        raise

def get_user_by_username(session, username):
    return session.query(User).filter_by(username=username).first()

@app.route('/')
def mainpage():
    engine = create_engine("cockroachdb://amiabuch:jaWHu24ejIX9F_vQ-KciWA@motion-al-9036.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full")
    initialize_db(engine)
    session = get_session()
    initialize_user_table(session)

    session.close()
    return render_template('mainpage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        data = request.form
        user_data =  {
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

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        password = data["password"]
        session = get_session()
        user1 = get_user_by_username(session, username)
        session.close()
        if user1 and check_password_hash(user1.password, password):
            # Generate JWT token
            access_token = create_access_token(identity=username)
            resp = jsonify(login=True)
            set_access_cookies(resp, access_token)
            return redirect(url_for('userdetails')) 
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
