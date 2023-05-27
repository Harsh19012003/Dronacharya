import os
import sqlite3
# import cv2 as cv
import numpy as nu
# import pyzbar.pyzbar as pyzbar (Scanning QR Code)
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
import flask_session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, user_tracked_location, input_location_coords, password_check


# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Connecting to database
conn = sqlite3.connect("database.db", timeout = 50, check_same_thread=False)
db = conn.cursor()
try:
    sqliteConnection = sqlite3.connect("database.db")
    print("Database created and succcessfully connected to SQLite")

    sqlite_select_Query = "select sqlite_version();"
    db.execute(sqlite_select_Query)
    record = db.fetchall()
    print("SQlite database version is: ", record)
except:
    print(f"Error while connecting to sqlite")



# Database one time generating table
'''
db.execute("CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT, email TEXT, password TEXT)")

db.execute(""" /*hjhj*/
CREATE TABLE colleges(
SrNo DOUBLE,
Merit_Score VARCHAR(100),
Choice_Code DOUBLE,
Institute VARCHAR(100),
Course_Name VARCHAR(100),
Exam_JEEMHT__CET VARCHAR(100),
Type VARCHAR(100),
Seat_Type VARCHAR(100)
);""")
'''



# Loading colleges info in SQLite table
"""
with open('cetcell 2020.csv','r') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['Sr.No.'], i['Merit (Score)'], i['Choice Code'], i['Institute'], i['Course Name'], i['Exam (JEE/MHT  CET)'], i['Type'], i['Seat Type']) for i in dr]
db.executemany("INSERT INTO colleges (SrNo, Merit_Score, Choice_Code, Institute, Course_Name, Exam_JEEMHT__CET, Type, Seat_Type) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
conn.commit()
print("clg insertion successfull")
"""



# APP ROUTES

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    # If user reached route via POST
    if request.method == "POST":
        # Getting info
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check whether password is strong enough
        x = password_check(password)
        if x is False:
            return apology("Please satisfy password requirements")

        # Checking if password equal to confirmation
        if not password == confirmation:
            return apology("Password and confirmation didnt matched")

        # Generating hash to store in database
        hash = generate_password_hash(password)

        # Storing in database
        db.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", [name, email, hash])
        # print("tables interior: ")
        db.execute("SELECT * FROM users")
        # print(f"fetch of register", db.fetchall())

        return redirect("/login")
    
    # If user reached route via GET
    else:
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    # If user reached route via POST
    if request.method == "POST":
        # Forget any previous user

        # Getting info
        name = request.form.get("name")
        password = request.form.get("password")

        # Validating info with database
        db.execute("SELECT * FROM users")
        rows = db.fetchall()
        # print(f"fetch of login: {rows}")
        for row in rows:
            if row[1] == name:
                # Remember which user has logged in
                #session["id"] = rows[0][0]
                print("successfull login")
                return redirect("/details")
        return apology("Please register if you havent")

    # If user reached route via GET
    else:
        return render_template("login.html")



@app.route("/details", methods=["GET", "POST"])
def details():
    # If user reached route via POST
    if request.method == "POST":
        # Getting user info
        cet = request.form.get("cet") # Getting input via scanning QR of marklist
        jee = request.form.get("jee")
        location = request.form.get("location") # Location tracking using ip address
        entered_location = request.form.get("entered_location")
        ce = request.form.get("Computer Engineering")
        it = request.form.get("Information Technology")
        cse = request.form.get("Computer Science and Engineering(Data Science)")
        ai = request.form.get("Artificial Intelligence and Data Science")
        mech = request.form.get("Mechanical Engineering")
        ee = request.form.get("Electronics Engineering")
        che = request.form.get("Chemical Engineering")
        et = request.form.get("Electronics and Telecommunication\nEngg")
        ae = request.form.get("Automobile Engineering")

        # Basic errorhandeling
        if cet=="" and jee=="":
            return apology("Atleast one marks are required")
        
        if location == "enter":
            # Find and use API
            print(f"Users entered location is: {entered_location}")
        elif location == "track":
            userlocation = user_tracked_location()
            # print(f"Your current location is: {userlocation}")
        else:
            return apology("please provide location") 

        # Scanning QR code
        '''
        NOT IMPLEMENTED DUE TO PYZBAR ".dll" DISCREPANCY
        cap = cv.VideoCapture(2)

        while True:
            _, frame = cap.read()

            barcode = pyzbar.decode(frame)
            for bdata in barcode:
                print(f"data  {bdata.data}")
                Data = barcode.data.decode("utf-8")
                Type = barcode.type
                print(f"data  {Data}")
                print(f"type  {Type}")
            break
        '''

        # Database query for best clg suggestions
        li = [ce, it, cse, ai, mech, ee, che, et, ae]
        fli = []
        ffli = []
        for item in li:
            if item != None:
                fli.append([item])

        for item in range(len(fli)):
            ffli.append(fli[item][0])

        params = []
        params.append(jee)
        for item in ffli:
            params.append(item)
        # print(f"params: {params}")
        
        # Database query for colleges in which admission is possible due to jee
        db.execute("SELECT * FROM colleges WHERE Merit_Score<=? AND Exam_JEEMHT__CET='JEE' AND Course_Name IN (%s)"%', '.join('?' for a in ffli), params)
        global clg_jee_list
        clg_jee_list = db.fetchall()
        # print(f"clg_jee_list: {clg_jee_list}")

        params[0] = cet
        #print(f"params: {params}")
        # Database query for colleges in which admission is possible due to mht-cet
        db.execute("SELECT * FROM colleges WHERE Merit_Score<=? AND Exam_JEEMHT__CET='MHT CET' AND Course_Name IN (%s)"%', '.join('?' for a in ffli), params)
        global clg_cet_list
        clg_cet_list = db.fetchall()
        # print(f"clg_cet_list: {clg_cet_list}")

        # Merging both jee and mht-cet lists
        global clg_list 
        clg_list = clg_jee_list + clg_cet_list
        # print(f"clg_list: {clg_list}")

        '''
        APLTERNATE CORRECT APPROCH BUT NOT WORKING PROPERLY DUE TO DISCREPANCY IN DATA
        skips some list items and displays it...........

        for list in clg_list:
            if (list[5] == "JEE" and list[1] > jee) or (list[5] == "MHT CET" and list[1] > cet):
                print(list)
                print()
                clg_list.remove(list)

        print(f"clg_list : {clg_list}")
        '''

        return redirect("/suggestions")
    # If user reached route via GET
    else:
        return render_template("details.html")



@app.route("/suggestions")
def suggestions():
    # Rendering suggestions along with clg list generated in runtime
    return render_template("suggestions.html", clg_list = clg_list)



@app.route("/faqs")
def faqs():
    return render_template("faqs.html")



# Error handlers
def errorhandler(e):
    # Basic error handeling
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)



# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)



if __name__ == '__main__':
    app.run(debug = True)


conn.close()
