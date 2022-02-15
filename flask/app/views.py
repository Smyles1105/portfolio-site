from app import app
import logging
logging.basicConfig(level=logging.DEBUG)
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email
from flask_mail import Mail, Message
from threading import Thread
import os

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['CONTACT_SUBJECT_PREFIX'] = '[PORTFOLIO SITE CONTACT FORM]'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SENDER'] = os.environ.get('MAIL_SENDER')
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL')
app.config['NAME'] = os.environ.get('NAME')

mail=Mail(app)
def create_email_from_form(subject, template, **formdata):
    message= Message(subject=subject,
                     recipients=[app.config['ADMIN_EMAIL']],
                     sender=app.config['MAIL_SENDER'])
    message.body = render_template(template + '.txt', **formdata)
    message.html = render_template(template + '.html', **formdata)
    return message

def send_email(message):
    thread = Thread(target=send_async_email, args=[app, message])
    thread.start()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
    
class ContactForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField('What is your email?', validators=[DataRequired(), Email()])
    message = TextAreaField('What is your message?', validators=[DataRequired()])
    submit = SubmitField('Send')


@app.route("/")
def home():
    return render_template("index.html", title="Home", name=app.config['NAME'])

@app.route("/posts")
def posts():
    return render_template("posts.html", title="Posts", name=app.config['NAME'])

@app.route("/about")
def about():
    return render_template("about.html", title="About", name=app.config['NAME'])

@app.route("/projects")
def projects():
    return render_template("projects.html", title="Projects", name=app.config['NAME'])

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    logging.info('Contact page')
    form = ContactForm()
    if form.validate_on_submit():
        logging.info('Form validated')
        if app.config['ADMIN_EMAIL']:
            logging.info('trying to send email to ' + app.config['ADMIN_EMAIL'])
            email = create_email_from_form(app.config['CONTACT_SUBJECT_PREFIX'], 'contactemail', name=form.name.data, email=form.email.data, message=form.message.data)
            logging.info('email created')
            start_email_thread(email)
            logging.info('email sent')
        return redirect(url_for('contact'))
    else:
        logging.info("form did not validate on submit")
    return render_template("contact.html", title="Contact", form=form, name=app.config['NAME'])
