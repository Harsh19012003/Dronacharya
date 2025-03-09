import os
import re
import requests
import json
import pandas as pd
from flask import redirect, render_template, request, session
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from datetime import datetime

# Check Email basic need
def email_check(email):
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(email_regex, email))



# Apology renders memetemplate as an userside error
def apology(message, code=400):
    # Render message as an error to user.
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code



# Function used above every other function which ensures user is logged in
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



# Checks password requirements
def password_check(ps):
    # Ensures password contains atleast one uppercase, one lowercase and one numeric.
    uc = False
    lc = False
    nm = False
    print(type(uc))
    for char in ps:
        if char.isupper():
            uc = True
        if char.islower():
            lc = True
        if char.isdigit():
            nm = True

    if uc and lc and nm:
        return True
    else:
        return False



# Tracks users location via geolocation api
def user_tracked_location():
    # Returns bunch of user location info along with latitude and longitude
    request_url = 'https://geolocation-db.com/jsonp/'
    response = requests.get(request_url)
    result = response.content.decode()
    result = result.split("(")[1].strip(")")
    result  = json.loads(result)
    print(result)
    lat = result["latitude"]
    lon = result["longitude"]
    location = [lat, lon]
    return location



# Geolocation api for location name to coordinates(latitude and longitude)
def input_location_coords(l):
    """
    # COULDNT FIND GEOCOORDINATE'S FREE API

    1) POSITIONSTACK.COM (not accurate)
    api_key = "f5e4086ff8d0e514ad9ab4d30b203ffe"
    base_url = "http://api.positionstack.com/v1/forward?access_key=f5e4086ff8d0e514ad9ab4d30b203ffe&query=nallsopara"
    response = requests.get(base_url).json()
    print(response)

    2) GOOGLE API
    api_key = "AIzaSyCp2GycvRmkfGlcaK4eJiCsOE1x_NOoVRs" (requires bank details)
    base_url = "https://maps.googleapis.com/maps/api/geocode/json?address=nallasopara&key=AIzaSyCp2GycvRmkfGlcaK4eJiCsOE1x_NOoVRs"
    response = requests.get(base_url).json()
    """

# Sends me email notifying someone has visited site
def send_notification_email(name, email):
    # Basic config
    sender_email = 'dronacharya.counsellor@gmail.com'
    sender_password = 'ncmltbtaqqkhtmsv'
    recipient_email = 'harshdevmurari007@gmail.com'
    visit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Email content
    if name=="NONE":
        subject = 'New Visitor Detected, Sir'
        body = f"SUBJECT: New Visitor Detected, Sir.\n\nAttention, Mr. Devmurari.\n\nI'm here to report a new visitor on your website. They entered at the landing page at {visit_time}.\n\nWhile I don't have further details about the visitor at this time, I am standing by for any additional instructions or if you wish to analyze their activity.\n\nAt your service,\nJarvis"
    else:
        subject = 'Attention Required, Mr. Devmurari. New Visitor Details.'
        # body = f"Hello Mr.Harshkumar Devmurari,\n\nThis mail is a notification to you that your website has a new visitor.\n\nClient Details:\nVisitor Name: {name}\nVisitor Email: {email}\nVisit Time: {visit_time}\n\nThis mail is one of the functionalities you have implemented in your project commiting to maintain active online presence\n\nBest regards,\nDronacharya(College Reccomandation System)"
        body = f"SUBJECT: Attention Required, Mr. Devmurari. I now have full details of Visitor.\n\nMr. Devmurari,\n\nJarvis here, with an update regarding that visitor. A new person, identified as {name}, has landed on your site at {visit_time}. Additionally, I have their email address: {email}.\n\n Should you require further investigation or wish to initiate contact, I stand ready to assist.\n\nAlways at your service,\n\nJarvis"

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach the message body
    message.attach(MIMEText(body, 'plain'))

    # Connect to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)

        # Send email
        server.sendmail(sender_email, recipient_email, message.as_string())