from flask import Flask, render_template, request, redirect, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import json
import mysql.connector
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Set your JWT secret key
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "query_string", "json"]
jwt = JWTManager(app)

# MySQL Configuration
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'Ami@1805SQL'

db = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
)
def initialization():
    cur=db.cursor()
    cur.execute("show databases;")
    l=cur.fetchall()
    flag=0
    l=[i[0] for i in l]
    for i in l:
        if i=='user':
            flag=-1
    cur=db.cursor()
    if flag==0:
        query="create database user"
        cur.execute(query)
        query="use user"
        cur.execute(query)
        query="create table userdetails(serialnumber int not null Primary Key, user varchar(1000), email varchar(1000), username varchar(1000), password varchar(300))"
        cur.execute(query)
        db.commit()
        cur.close()
        db.close()
        return
    else:
        query="use user"
        cur.execute(query)
        db.commit()
        cur.close()
        db.close()
        return

def get_users(query):
    try:
        
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
    
def store_users(user, email, username, password):
    try:
        
        if db:
            cur = db.cursor()
            cur.execute(f"INSERT INTO userdetails (user, email, username, password) VALUES ('{user}', '{email}','{username}','{password}')")
            cur.close()
            db.commit()
            db.close()
            return True
        else:
            print("llalalalal")
            return False
    except Exception as e:
        print(f"Error executing query: {e}")
        return False

@app.route('/')
def mainpage():
    initialization()
    return render_template('mainpage.html')

@app.route('/admin')
def admin():
    admin_details="SELECT * FROM userdetails"
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
            resp = jsonify(login == True)
            access_token = create_access_token(identity=user)
            set_access_cookies(resp, access_token)
            return redirect(url_for('userdetails', user=user)) 
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
       
        

        reg=store_users(user, email, username, password)
        if reg:
            # Generate JWT token
            access_token = create_access_token(identity=user)
            resp = jsonify()
            set_access_cookies(resp, access_token)
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/<user>/userdetails')
  # Protect this route with JWT authentication
def userdetails(user):
    user_details_query = f"SELECT username FROM userdetails WHERE username = '{user}'"
    user_details_result = get_users(user_details_query)
    
    if user_details_result:
        user_details = user_details_result[0]
    else:
        return "User not found"

    return render_template('userdetails.html', user=user_details)

@app.route('/editing')
@jwt_required()  # Protect this route with JWT authentication
def editing():
    return render_template('editing.html')

@app.route('/linkandcontribution')
@jwt_required()  # Protect this route with JWT authentication
def linkandcontribution():
    return render_template('linkandcontribution.html')

@app.route('/<user>/project_page')
@jwt_required()  # Protect this route with JWT authentication
def project_page(user):
    return render_template('project_page.html')

if __name__ == '__main__':
    app.run(debug=True)
