import os
import requests
import json
import pandas as pd
from flask import redirect, render_template, request, session
from functools import wraps



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
    """
    THIS IS NOT ACCURATE JUST IMPLEMENTED THE FUNCTIONALITY
    """
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
