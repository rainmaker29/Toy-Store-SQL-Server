from flask import Flask,render_template,request,redirect,flash,get_flashed_messages
from wtforms import Form, StringField, SelectField
from utils import generate_otp,my_gmail_password
import numpy as np
import pandas as pd
import pickle
import json
import re
import bcrypt
import smtplib


class User():
   def __init__(self):
      self.email = None
      self.password = None
      self.role = None
      self.otp = None

user = User()


app = Flask(__name__)

app.secret_key = "super secret key"
app.config["SESSION_TYPE"] = "filesystem"

class SearchForm(Form):
    search = StringField("")

df = pd.read_csv("products.csv")

with open("product_indices.pkl","rb") as f:
    product_indices = pickle.load(f)

@app.route("/",methods=["GET","POST"])
def home():
    search = SearchForm(request.form)
    if request.method == "POST":
        return search_results(search)
    if user.email :
        return render_template("index.html", form=search,
        products=df["ids"].to_list()[:12],user=user)

    return render_template("index.html", form=search,products=df["ids"].to_list()[:12],
    user=None)

@app.route("/results")
def search_results(search):
    results = []
    search_string = search.data["search"]
    if search.data["search"] == "":
        flash("Empty search")
        return redirect("/")
    
    for i in range(len(df)):
        if df.iloc[i]["name"]==search.data["search"].strip(" "):
            print("found")
            results.append(df.iloc[i]["ids"])
            print(results)
    

    
    if not results:
        flash("No results found!")
        return redirect("/")
    else:
        return render_template("results.html",form=search, results=results)

    
@app.route("/product/<string:product_id>")
def product(product_id):
    product_info = get_all(product_id)
    key = list(product_info["name"].keys())[0]
    name = product_info["name"][key]
    recommendations = recommend_product(name)
    
    return render_template("product.html",product_info=product_info,
    recommendations=recommendations,key=key)

@app.context_processor
def getname():
    def get_name_by_id(id):
        return df.loc[df["ids"]==id,"name"].to_list()[0]
    return dict(get_name_by_id=get_name_by_id)


@app.context_processor
def get_length():
    def getlen(obj):
        return len(obj)
    return dict(getlen=getlen)

# Login , Signup 
# ------------------
@app.route("/login",methods=["GET","POST"])
def login():
    user.role = list(request.form.keys())[0]
    return render_template("login.html")

@app.route("/authenticate",methods=["GET","POST"])
def check_login_or_signup():
   if "login" in list(request.form.keys()):
      email = request.form["email"]
      password = request.form["password"]
      if user.role=="user":
          filename = "users.json"
    
      else:
          filename="sellers.json"
      with open(filename,"r") as f:
         users = json.load(f)
         
      
      if email in users.keys():

         salt = bytes(users[email].split("\t")[1][2:-1],"utf-8")
         password = bytes(password,"utf-8")
         hashed = bcrypt.hashpw(password, salt)

         
         

         if str(hashed) == users[email].split("\t")[0]:
            user.email = email
            user.password = str(hashed)
            flash("Login succesfful")
            return redirect("/")
         else:
            flash("Login failed,password mismatch")
            return render_template("login.html")
      else:
         flash("Login failed,email not found")
         return render_template("login.html")
   else:
      email = request.form["email"]
      password = request.form["password"]
      user.email = email
      user.password = password
      if (bool(re.match("(^[a-z])([a-z0-9]+)@gmail\.com",email))) and (bool(re.compile("[A-Z]+").search(password)) and bool(re.compile("[a-z]+").search(password)) and bool(re.compile("[0-9]+").search(password)) and bool(re.compile("[!@#$%^&*=-]+").search(password))):
         # SMTP Code here 
         user.otp = generate_otp()
         s=smtplib.SMTP("smtp.gmail.com",587)
         s.starttls()
         s.login("amaanrahil29@gmail.com",my_gmail_password)
         msg="OTP generated is "+str(user.otp)
         s.sendmail("amaanrahil29@gmail.com","amaanrahil29@gmail.com",msg)
         s.quit()

         # -------------
         
         
         return render_template("otp.html")
      else:
         flash("Invalid email or password")
         return render_template("login.html")
        


@app.route("/checkotp",methods=["GET","POST"])
def checkotp():
   entered_otp = request.form["entered_otp"]
   if user.otp==int(entered_otp):
      salt = bcrypt.gensalt()
      password = bytes(user.password,"utf-8")
      hashed = bcrypt.hashpw(password, salt)

      if user.role=="user":
          filename = "users.json"
    
      else:
          filename="sellers.json"

      with open(filename,"r") as f:
         users = json.load(f)

      users[user.email] = str(hashed)+"\t"+str(salt)

      with open(filename,"w+") as f:
         json.dump(users,f)

      flash("Sign up successful")
      return redirect("login.html")
   else:
      flash("otp failed")
      return render_template("login.html")
#---------------------------------------
@app.route("/logout")
def logout():
    user.email=None
    user.password=None
    user.role=None
    user.otp=None
    return redirect("/")

### Utils 

def get_all(id):
    res = df.loc[df["ids"]==id,:].to_dict()
    return res
    


def get_idx(x):
    return df[df["name"]==x].index.tolist()[0]

def recommend_product(product):
    recommendations=[]
    index = get_idx(product)
    for i in product_indices[index][1:]:
            recommendations.append(df.iloc[i]["ids"])

    return recommendations
            

