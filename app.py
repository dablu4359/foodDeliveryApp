from flask import Flask, render_template, request, redirect, url_for, session
import flask

import MySQLdb.cursors
import re

app = Flask(__name__)
from configure import config
mysql = config(app)

from restaurant import restaurant
from customer import customer
from delivery import delivery
# app.register_blueprint(restaurant)
app.register_blueprint(customer)
app.register_blueprint(delivery)

@app.route('/home')
def home():
    session.clear()
    return render_template('index.html')


@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'useremail' in request.form and 'password' in request.form and 'authority' in request.form:
        useremail = request.form['useremail']
        password = request.form['password']
        authority = request.form['authority']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if (authority == "Customer"):
            cursor.execute("SELECT * FROM Customers WHERE email = % s AND password = % s", (useremail, password,))
            account = cursor.fetchone()
            if account:
                session['customerbool'] = True
                session['restbool'], session['agentbool'] = False, False
                session['customer_ID'] = str(account['customer_ID'])
                msg = 'Logged in successfully !'
                flask.flash(msg)
                return redirect(url_for('customer.dashboard'))
            else:
                msg = 'Incorrect username / password !'
        elif (authority == "Delivery Agent"):
            cursor.execute("SELECT * FROM delivery_agent WHERE email = % s AND password = % s", (useremail, password, ))
            account = cursor.fetchone()
            if account:
                session['agentbool'] = True
                session['cutomerbool'], session['restbool'] = False, False
                session['agent_ID'] = account['agent_ID']
                msg = 'Logged in successfully !'
                flask.flash(msg)
                return redirect(url_for('delivery.agentdetail'))
            else:
                msg = 'Incorrect username / password !'
        elif (authority == "Restaurant"):
            cursor.execute("SELECT * FROM restaurant WHERE email = % s AND password = % s", (useremail, password, ))
            account = cursor.fetchone()
            if account:
                session['restbool'] = True
                session['agentbool'], session['customerbool'] = False, False
                session['restaurant_ID'] = account['restaurant_ID']
                msg = 'Logged in successfully !'
                flask.flash(msg)
                return redirect(url_for('restaurant.restdetail'))
            else:
                msg = 'Incorrect username / password !'
        else:
            msg = 'Incorrect username / password !'
        flask.flash(msg)
    return render_template('login.html', msg = msg)


# making rout for sign up for all three types of users
@app.route('/signupcustomer',methods=['GET', 'POST'])
def signupcustomer():
    if request.method == 'POST':
        msg = 'CUSTOMER: Please fill out the form again'
        userdetails = request.form
        firstname = userdetails['firstname']
        lastname = userdetails['lastname']
        email = userdetails['email']
        DOB = userdetails['DOB']
        phone_number = userdetails['phone_number']
        password = userdetails['password']
        cur = mysql.connection.cursor()
        cur.execute("select max(customer_ID) from customers")
        ID = cur.fetchone()
        ID = str(int(ID[0]) + 1)
        cur.execute("insert into customers(customer_ID, first_name, last_name, email, phone_no, password, DOB) values(%s, %s, %s, %s, %s , %s, %s)", (ID, firstname, lastname, email, phone_number, password, DOB))
        mysql.connection.commit()
        cur.close()
        msg = 'CUSTOMER: sigup successfully!!'
        flask.flash(msg)
        return redirect(url_for('login'))
    return render_template('customersignup.html')

@app.route('/signuprestaurant', methods=['GET', 'POST'])
def signuprestaurant():
    if request.method == 'POST':
        msg = 'Restaurant please fill out the form again'
        restdetail = request.form
        name = restdetail['name']
        email = restdetail['email']
        phoneno = restdetail['Phone number']
        password = restdetail['password']
        # Keeping weekend_time and weekday_time as null values
        # For now keeping rest_address from our side
        rest_address = str(3)
        cur = mysql.connection.cursor()
        cur.execute('select max(restaurant_ID) from restaurant')
        ID = cur.fetchone()
        ID = str(int(ID[0]) + 1)
        cur.execute('insert into restaurant(restaurant_ID, name, email, phone_number, rest_address, password) values(%s, %s, %s, %s, %s, %s)', (ID, name, email, phoneno, rest_address, password))
        mysql.connection.commit()
        cur.close()
        msg = 'RESTAURANT sigup successfully!!'
        flask.flash(msg)
        return redirect(url_for('login'))
    return render_template('restaurantsignup.html')

@app.route('/signupdeliveryagent', methods=['GET', 'POST'])
def signupdeliveryagent():
    if request.method == 'POST':
        msg = 'Agent please fill out the form again'
        agentdetail = request.form
        cur = mysql.connection.cursor()
        cur.execute('select max(agent_ID) from delivery_agent;')
        ID = cur.fetchone()
        ID = str(int(ID[0]) + 1)
        cur.execute('insert into delivery_agent(agent_ID, first_name, middle_name, last_name, phone_no, email, DOB, password) values(%s, %s, %s, %s, %s, %s, %s, %s)', (ID, agentdetail['firstName'], agentdetail['MiddleName'], agentdetail['lastName'], agentdetail['Phone number'], agentdetail['email'], agentdetail['DOB'], agentdetail['password']))
        mysql.connection.commit()
        cur.close()
        msg = 'AGENT sigup successfully!!'
        flask.flash(msg)
        return redirect(url_for('login'))
    return render_template('deliveryagentsignup.html')

# about us url
@app.route('/aboutus', methods=["GET", "POST"])
def aboutus():
    if (request.method=="POST"):
        cur = mysql.connection.cursor()
        renaming_col =str( request.values.get("col_name"))
        rename_value =str( request.values.get("new_name"))
        if (rename_value != ""):
            query = f"ALTER TABLE `team_details` RENAME COLUMN `{renaming_col}` TO `{rename_value}`;"
            cur.execute(query)
            mysql.connection.commit()
            cur.close()
            flask.flash("Successfully renamed the column")
        else:
            flask.flash("Please put up rename value of the column.")
    query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
    tablename = 'Team_details'  
    cur = mysql.connection.cursor()
    cur.execute(query, ("Team_details",))
    col_name = cur.fetchall();

    table ={
        'roll_number':col_name[0][0],
        'first_name':col_name[1][0],
        'last_name':col_name[2][0],
        'emailid':col_name[3][0],
    }

    cur.execute("select * from Team_details")
    students = cur.fetchall();
    student_details=[]
    for student in students:
        temp = {
            'roll_number':student[0],
            'first_name':student[1],
            'last_name':student[2],
            'emailid':student[3]
        }
        student_details.append(temp)
    
    return render_template('aboutus.html',tablename=tablename, table = table, student_details= student_details)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

if __name__ == '__main__':
    app.run(debug=True, port=8000)