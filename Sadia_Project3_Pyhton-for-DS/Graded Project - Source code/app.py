from flask import Flask,render_template,request,jsonify,redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle
import numpy as np
import sklearn
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)



app=Flask(__name__)
model=pickle.load(open('loan_approval_predictor_final.pkl','rb'))

app.secret_key = os.urandom(32)
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'God4Isu#'
app.config['MYSQL_DB'] = 'user_info'
 
mysql = MySQL(app)
 

@app.route('/',methods=['GET'])
def Home():
    return render_template('home.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_credentials WHERE username = % s AND password = % s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('predict.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form :
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_credentials WHERE username = % s', (username))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user_credentials(username,password) VALUES ( % s, % s)', (username, password))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


# @app.route('/',methods=['GET'])
# def Home():
#     return render_template('home.html')

@app.route("/predict",methods=['POST'])
def predict():
    if request.method == 'POST':
        dependents=request.form['dependents']
        applicantincome = float(request.form['applicantincome'])
        coapplicantincome = float(request.form['coapplicantincome'])
        loanamount = float(request.form['loanamount'])
        loan_amount_term =float(request.form['loan_amount_term'])
        credit_history =request.form['credit_history']
        property_area=request.form['property_area']
        gender_male=request.form['gender_male']
        married_yes=request.form['married_yes']
        education_notGrad=request.form['education_notGrad']
        self_employed_yes=request.form['self_employed_yes']
        prediction=model.predict([[dependents,applicantincome,coapplicantincome,loanamount,loan_amount_term,credit_history,property_area,gender_male,married_yes,education_notGrad,self_employed_yes]])
        if prediction[0]==1:
            pred_text = "Congrats!! You are eligible for the loan"
        else :
            pred_text = "Sorry , you are not eligible for the loan"

        return render_template('predict.html',prediction_text=pred_text)


if __name__=="__main__":
    app.run(debug=True)
        

