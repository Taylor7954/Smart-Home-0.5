from flask import (
	Flask, render_template, flash,
	redirect, url_for, session, logging,
	request, make_response, g, redirect
	)
# from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, IntegerField, validators
from passlib.hash import sha256_crypt
from app.models import engine, Session, User
#Flask babel for translation
from flask_babel import Babel, gettext, lazy_gettext
#to import flask_babel do: pip install flask_babel
#next create the .pot file for language localisation
#to create the .pot file run cmd: pipenv run pybabel extract -F babel.cfg -o messages.pot --input-dirs=.
#from there run cmd: pipenv run pybabel init -i messages.pot -d translations -l ja
#this will make the .po file which will house the translation
#I have done the translations and put them in the spare.txt file
#next run cmd: pipenv run pybabel compile -d translations
#this will make the .mo file which is by the code


app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

#Setting main language
@babel.localeselector
def get_locale():
	print(g.lang)
	return g.lang

#Config PostgresSQL

#init PostgresSQL

# handle language switch before rendering page
def get_lang(r):
	lang = r.cookies.get('lang')
	if lang is None:
		lang = 'en'
	g.lang = lang

#Home page1
@app.route('/')
def index():
	get_lang(request)

	return render_template('index.html')

@app.route('/en')
def en():

	get_lang(request)
	g.lang = 'en'

	resp = make_response(render_template('index.html'))
	resp.set_cookie('lang', 'en')
	
	return resp

@app.route('/ja')
def ja():

	get_lang(request)
	g.lang = 'ja'

	resp = make_response(render_template('index.html'))
	resp.set_cookie('lang', 'ja')
	
	return resp
	
#Help page if needed
@app.route('/help')
def help():

	get_lang(request)

	return render_template('help.html')
	
#Group Info
@app.route('/contact')
def contact():

	get_lang(request)

	return render_template('contact.html')

class RegisterForm(Form):
	name = StringField(lazy_gettext('Name'), [validators.Length(min=1, max=50)])
	email = StringField(lazy_gettext('Email'), [validators.Length(min=6, max= 50)])
	address = StringField(lazy_gettext('Address'), [validators.Length(min=6, max= 50)])
	city = StringField(lazy_gettext('City'), [validators.Length(min=6, max= 50)])
	state = StringField(lazy_gettext('State'), [validators.Length(min=6, max= 50)])
	zip = IntegerField(lazy_gettext('Zip Code'))
	password = PasswordField(lazy_gettext('Password'),[
		validators.DataRequired(),
		validators.EqualTo('confirm', message=lazy_gettext("Passwords do not match."))])
	confirm = PasswordField(lazy_gettext('Confirm Password')),

			
	
	#DATABASE FOR USER
	#Create cursor  cursor = (database.connection.cursor())
	#execute query ("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s), (name, username, email, password))
	#commit to db with (database.connect.commit()
	#close connection cursor.close()
	#flash('You are now registered and can log in', 'success') ** this gives success message
	#return redirect(url_for('login')) redirect for login page

@app.route('/registerHouse', methods=['GET', 'POST'])
def registerHouse():

	get_lang(request)

	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		address = form.address.data
		city = form.city.data
		state = form.state.data
		zip = form.zip.data
		
		return render_template('registerHouse.html')
	return render_template('registerHouse.html', form=form)
	
#User Register
@app.route('/register', methods=['GET', 'POST'])
def register():

	get_lang(request)

	form = RegisterForm(request.form)
	if request.method == 'POST':
		name = form.name.data
		email = form.email.data
		password = form.password.data
		
		#create new db session
		session = Session()
		#create new user: A new user is identified by name, email, password
		new_user = User(name=name, email=email, password_hash=password)
	
		#Does the email already exist
		###match = session.query(User).filter(User.email==email)

		match = session.query(User.email)\
        .filter(User.email==email)\
        .all()
		#If the email is unique the user is added
		if not match:
			print(f'Added: {new_user}')
			session.add(new_user)
			#save changes
			session.commit()
		else:
			flash(gettext("Email already registered"))
			return render_template('register.html', form=form)
		
		#close connection
		session.close()
		flash(gettext('You are now registered and can log in'), 'success')

		return redirect(url_for('login'))
	return render_template('register.html', form=form)

#User Login
@app.route('/login', methods=['GET', 'POST'])
def login():

	get_lang(request)

	if request.method == 'POST':
		#Get form fields
		email= request.form['email']
		password_candidate = request.form['password']
		
		sess = Session()
		
		#Query database for email and password
		userMatch = sess.query(User.email)\
        .filter(User.email==email)\
		.filter(User.password_hash==password_candidate)\
        .all()
		
		name = sess.query(User.name).filter(User.email==email).first()
		
		if userMatch:
			session['logged_in'] = True
			session['name'] = name[0]
			flash(gettext("You are now logged in"), gettext("success"))
			return redirect(url_for('index'))
		else:
			error=gettext("Invalid Login")
			return render_template('login.html', error=error)
			
		#create cursor
		#cursor = database.connection.cursor()
		
		#Get user by email
		#result = cursor.execute("SELECT * FROM users WHERE email = %s", [email])
		#if result > 0:
			#get stored hash
			#data = cursor.fetchone()
			#password = data['password'] #gets a tuple if cursorclass is established
			
			#compare passwords
			#if sha256_crypt.verify(password_candidate, password):
				#passed
				#session['logged_in'] = True
				#session['email'] = email
				#flash("You are now logged in", "success")
				#return redirect(url_for('index'))
			#else:
				#error = "Invalid Login"
				#return render_template('login.html', error=error)
		#else:
			#error="User not found"
			#return render_template('login.html', error=error)
	return render_template('login.html')

#Dashboard
@app.route('/dashboard')
def dashboard():
	
	get_lang(request)

	return render_template('dashboard.html')

#log out
@app.route('/logout')
def logout():

	get_lang(request)

	session.clear()
	flash(gettext('You are now logged out'), gettext('success'))
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)
	