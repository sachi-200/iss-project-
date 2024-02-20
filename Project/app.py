from flask import *
import mysql.connector
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Set your JWT secret key
jwt = JWTManager(app)

# MySQL Configuration
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'Matilda+10'

# Connect to MySQL
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
        cur.close()
        return
    else:
        query="use user"
        cur.execute(query)
        cur.close()
        return

def get_users(query):
    try:
        cur=db.cursor()
        cur.execute(query)
        result=cur.fetchall()
        cur.close()
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    
def store_users(query):
    try:
        cur=db.cursor()
        cur.execute(query)
        cur.close()
        return True
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

@app.route('/')
def mainpage():
    initialization()
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
        login_query = f"SELECT * from userdetails WHERE username='{user}' AND password='{password}'"
        user_details = get_users(login_query)
        if user_details:
            # Generate JWT token
            access_token = create_access_token(identity=user)
            return redirect(url_for({user}))
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
        register_details_query = "SELECT serialnumber from userdetails"
        register_details_result = get_users(register_details_query)
        count = len(register_details_result)
        number = count + 1
        register_details_query = f"insert into userdetails values ({number}, '{user}', '{email}', '{username}', '{password}')"
        if store_users(register_details_query):
            # Generate JWT token
            access_token = create_access_token(identity=user)
            return redirect('login')
    return render_template('register.html')

@app.route('/userdetails')
@jwt_required()  # Protect this route with JWT authentication
def userdetails():
    user_details_query = "SELECT username, email FROM userdetails WHERE serialnumber = 1"
    user_details_result = get_users(user_details_query)
    
    if user_details_result:
        user_details = user_details_result[0]
    else:
        return "User not found"

    return render_template('userdetails.html', user_details=user_details)

@app.route('/editing')
@jwt_required()  # Protect this route with JWT authentication
def editing():
    return render_template('editing.html')

@app.route('/linkandcontribution')
@jwt_required()  # Protect this route with JWT authentication
def linkandcontribution():
    return render_template('linkandcontribution.html')

@app.route('/<user>')
@jwt_required()  # Protect this route with JWT authentication
def new_project():
    return render_template('new_project.html')

@app.route('/project_page')
@jwt_required()  # Protect this route with JWT authentication
def project_page():
    return render_template('project_page.html')

if __name__ == '__main__':
    app.run(debug=True)