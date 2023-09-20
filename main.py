from flask import Flask, render_template, request, redirect,session,url_for
import mysql.connector
import os
import pandas as pd
import numpy as np
import pickle
import tensorflow as tf 
from preprocess import *
from flask_mysqldb import MySQL
import MySQLdb.cursors




app = Flask(__name__)
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'database'

mysql = MySQL(app)



@app.route('/')
def login():
	return render_template('login.html')

# call the register template when the url is http://localhost:5000/register
@app.route('/register')
def register():
	return render_template('register.html')


@app.route('/home')
def home():
	if 'Name' in session:
		return render_template('home.html')
	else:
		return redirect('/')


@app.route('/login_validation', methods=['GET','POST'])
def login_validation():
	msg = ''
	if request.method =='POST' and 'email' in request.form and 'password' in request.form:
		email = request.form['email']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM signup WHERE email = % s AND password = % s', (email,password))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['email'] = account['email']
			msg = 'Logged in successfully !'
			return render_template('home.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)
    

@app.route('/add_user', methods=['GET','POST'])
def add_user():
	msg = ''
	if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
		name = request.form['name']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM signup WHERE username = % s', (name, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@p]+', email):
			msg = 'Invalid email address !'      
		elif not re.match(r'[A-Za-z0-9]+', name):
			msg = 'Username must contain only characters and numbers !'
		elif not name or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO signup VALUES (NULL,% s, % s, % s)', (name,password,email, ))
			mysql.connection.commit()
			return render_template('home.html')
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)



@app.route('/logout')
def logout():
# close the session
	session.pop('Name')
	return redirect('/')



@app.route('/sentiment_analyzer')
def sentiments():
    return render_template('/sentiment_analyzer.html')


@app.route('/predict', methods=['POST'])
def predict():
    text = request.form['text']
    
    encoder = pickle.load(open('encoder.pkl', 'rb'))
    cv = pickle.load(open('CountVectorizer.pkl', 'rb'))
    model = tf.keras.models.load_model('my_model.h5')
    
    input_text = preprocess(text)
    array = cv.transform([input_text]).toarray()
    
    pred = model.predict(array)
    a = np.argmax(pred, axis=1)
    prediction = encoder.inverse_transform(a)[0]
    return render_template('/sentiment_analyzer.html', prediction=prediction)



@app.route('/remove-text', methods=['POST'])
def remove_text():
    # Clear the textbox value by setting it to an empty string
    textbox_value = ""
    return redirect(url_for('sentiments'))



if __name__ == '__main__':
    app.run(debug=True)




