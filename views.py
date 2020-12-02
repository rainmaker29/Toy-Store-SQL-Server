from flask import Flask,render_template,request,redirect,flash,get_flashed_messages
from wtforms import Form, StringField, SelectField
from utils import generate_otp,my_gmail_password
from CustomerDB import UserDB_Obj,SellerDB_Obj
import numpy as np
import pandas as pd
import pickle
import json
import re
import bcrypt
import smtplib
import secrets
import string
import pyodbc


class User():
   def __init__(self):
      self.email = None
      self.password = None
      self.role = None
      self.otp = None
      self.cart = None
      self.cost = 0

user = User()


app = Flask(__name__)

app.secret_key = "super secret key"
app.config["SESSION_TYPE"] = "filesystem"

# For Docker , use SA UID - this attempt is using container IPv4
# conn = pyodbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.6.so.1.1};'
#                       'Server=172.18.0.2/16,1433;'
#                       'Database=Products;'
#                       'UID=SA;'
#                       'PWD=AMAAN@123')

#This one is between containers ,using name.
conn = pyodbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.6.so.1.1};'
                      'Server=sqlserver;'
                      'Database=Products;'
                      'UID=SA;'
                      'PWD=AMAAN@123')






# This one is for container and host 
# conn = pyodbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.6.so.1.1};'
#                       'Server=localhost;'
#                       'Database=Products;'
#                       'UID=SA;'
#                       'PWD=AMAAN@123')

# conn = pyodbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.6.so.1.1};'
#                       'Server=localhost;'
#                       'Database=Products;'
#                       'UID=AMAAN;'
#                       'PWD=AMAAN@123')

cursor = conn.cursor()


class SearchForm(Form):
    search = StringField("")


with open("product_indices.pkl","rb") as f:
    product_indices = pickle.load(f)

@app.route("/",methods=["GET","POST"])
def home():
    search = SearchForm(request.form)
    products = cursor.execute("SELECT TOP 12 ids from PRODS_AMAAN;").fetchall()
    if request.method == "POST":
        return search_results(search)
    if user.email :        
        return render_template("index.html", form=search,
        products=products,user=user)

    return render_template("index.html", form=search,products=products,
    user=None)

@app.route("/results")
def search_results(search):
    results = []
    search_string = search.data["search"]
    if search.data["search"] == "":
        flash("Empty search")
        return redirect("/")
    id_names = cursor.execute("SELECT ids,names from PRODS_AMAAN;").fetchall()
    for id_name in id_names:
        if id_name[1]==search.data["search"].strip(" "):
            print("found")
            results.append(id_name[0])
            print(results)
    

    
    if not results:
        flash("No results found!")
        return redirect("/")
    else:
        return render_template("results.html",form=search, results=results,user=user)

    
@app.route("/product/<string:product_id>")
def product(product_id):
    product_info = get_all(product_id)
    name = product_info[12]
    recommendations = recommend_product(name)
    return render_template("product.html",product_info=product_info,
    recommendations=recommendations,user=user)



# User/Customer functions ------------------------

@app.route("/add_to_cart")
def add_to_cart():
    product_id = request.referrer.split("/")[-1]
    product_info = get_all(product_id)
    product_price = product_info[1]
    user.cost += product_price
    user.cart.append(product_id)
    flash(f"Added to cart. In cart : {len(user.cart)} items")
    return redirect(request.referrer)



@app.route("/view_cart")
def view_cart():
    return render_template("view_cart.html",user=user)

@app.route("/remove_from_cart",methods=["POST"])
def remove_from_cart():
    product_id=list(request.form.keys())[0]
    user.cart.remove(product_id)
    product_info = get_all(product_id)
    product_price = product_info[1]
    user.cost -= product_price
    if len(user.cart)==0:
        user.cost=0
    
    return render_template("/view_cart.html",user=user)

@app.route("/payment",methods=["POST","GET"])
def payment():
    return render_template("payment.html")

# Seller Functions ------------------------

@app.route("/error404")
def error404():
    return render_template("error404.html")

@app.route("/my_products")
def my_products():
    if user.email==None:
        return redirect("/error404")
    return render_template("my_products.html",my_prods=get_seller_products(user.email),
    user=user)

@app.route("/add_product",methods=['POST'])
def add_product():
    new_prod=[None]*14

    new_prod[0] = user.email
    new_prod[1] = request.form['new_product_price']
    new_prod[5] = request.form['new_product_rating']
    new_prod[10] = request.form['new_product_category']
    new_prod[12] = request.form['new_product_name']
    new_prod[13] = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                                                  for i in range(32)) 
    if  new_prod[0]==None or new_prod[1]==None or new_prod[12]==None:
        flash("Insuff product info ! Add again !")
        return render_template("/my_products.html",my_prods=get_seller_products(user.email),
        user=user)
    fin_ind = cursor.execute("SELECT TOP 1 ind FROM PRODS_AMAAN ORDER BY ind DESC").fetchall()[0][0]
    cursor.execute("INSERT INTO PRODS_AMAAN (manufacturer,price,number_available_in_stock,number_of_reviews,number_of_answered_questions,average_review_rating,customers_who_bought_this_item_also_bought,items_customers_buy_after_viewing_this_item,sellers,used_or_unused,category,sub_category,names,ids,ind) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    new_prod[0], new_prod[1], new_prod[2],new_prod[3],new_prod[4],new_prod[5],new_prod[6],new_prod[7],new_prod[8],new_prod[9],new_prod[10],new_prod[11],new_prod[12],new_prod[13],fin_ind+1)
    
    conn.commit()
    
    flash("Item added !")
    return render_template("/my_products.html",my_prods=get_seller_products(user.email),user=user)

@app.route("/remove_product",methods=["POST"])
def remove_product():
    product_id=list(request.form.keys())[0]
    try:
        cursor.execute("DELETE FROM PRODS_AMAAN WHERE ids=?",product_id)
        conn.commit()
        flash("Item deleted !")
        return render_template("/my_products.html",my_prods=get_seller_products(user.email),user=user)
    except :
        flash("Item not found !")
        return render_template("/my_products.html",my_prods=get_seller_products(user.email),user=user)


# Login , Signup 
# ------------------

@app.route("/login",methods=["GET","POST"])
def login():
    if request.referrer==None:
        flash("You gotta select a role")
        return redirect("/")
    if len(list(request.form.keys()))>0:
        user.role = list(request.form.keys())[0]
    return render_template("login.html",user=user)

@app.route("/authenticate",methods=["GET","POST"])
def check_login_or_signup():
   if "login" in list(request.form.keys()):
      email = request.form["email"]
      password = request.form["password"]
      if user.role=="user":
          customer_db = UserDB_Obj
    
      else:
          customer_db = SellerDB_Obj

      if (customer_db.objects()) and (customer_db.objects(email=email).first()):
         salt = bytes(customer_db.objects(email=email).first()["password"].split("\t")[1][2:-1],"utf-8")
         password = bytes(password,"utf-8")
         hashed = bcrypt.hashpw(password, salt)

         if str(hashed) == customer_db.objects(email=email).first()["password"].split("\t")[0]:
            user.email = email
            user.password = str(hashed)
            if user.role=="user":
                user.cart=list()
            flash("Login succesfful")
            return redirect("/")
         else:
            flash("Login failed,password mismatch")
            return render_template("login.html",user=user)
      else:
         flash("Login failed,email not found")
         return render_template("login.html",user=user)
   else:
      email = request.form["email"]
      password = request.form["password"]
      user.email = email
      user.password = password
      if (bool(re.match("(^[a-z])([a-z0-9]+)@gmail\.com",email))) and (bool(re.compile("[A-Z]+").search(password)) and bool(re.compile("[a-z]+").search(password)) and bool(re.compile("[0-9]+").search(password)) and bool(re.compile("[!@#$%^&*=-]+").search(password))):
         if user.role=="user":
          if UserDB_Obj.objects(email=email).first() and (email == UserDB_Obj.objects(email=email).first()["email"]):
             flash("User exists")
             return render_template("login.html",user=user)

         else:
             if (SellerDB_Obj.objects(email=email).first()) and (email == SellerDB_Obj.objects(email=email).first()["email"]):
                flash("User exists")
                return render_template("login.html",user=user)

         
         
         
         # SMTP Code here 
         user.otp = generate_otp()
         s=smtplib.SMTP("smtp.gmail.com",587)
         s.starttls()
         s.login("mksc1289@gmail.com",my_gmail_password)
         msg="OTP generated is "+str(user.otp)
         s.sendmail("mksc1289@gmail.com",email,msg)
         s.quit()

         # -------------
         
         
         return render_template("otp.html")
      else:
         flash("Invalid email or password")
         return render_template("login.html",user=user)
        


@app.route("/checkotp",methods=["GET","POST"])
def checkotp():
   entered_otp = request.form["entered_otp"]
   if user.otp==int(entered_otp):
      salt = bcrypt.gensalt()
      password = bytes(user.password,"utf-8")
      hashed = bcrypt.hashpw(password, salt)

      if user.role=="user":
          customer_doc = UserDB_Obj()
        
    
      else:
          customer_doc = SellerDB_Obj()
        
      customer_doc.email = user.email
      customer_doc.password = str(hashed)+"\t"+str(salt)
      customer_doc.save()

    
      flash("Sign up successful")
      return redirect("/login")
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
    if user.cart:
        user.cart=[]
        user.cost=0
    return redirect("/")

### Utils 


@app.context_processor
def getname():
    def get_name_by_id(idx):
        name=cursor.execute("SELECT names FROM PRODS_AMAAN where ids = ?", idx).fetchall()[0][0]

        return name
    return dict(get_name_by_id=get_name_by_id)

@app.context_processor
def trimname():
    def trim_name(name):
        if len(name)>10:
            name = name[:10]+'...'
        return name
    return dict(trim_name=trim_name)


@app.context_processor
def get_length():
    def getlen(obj):
        return len(obj)
    return dict(getlen=getlen)



def get_all(idx):
    res = cursor.execute("SELECT * FROM PRODS_AMAAN WHERE ids = ?",idx).fetchall()
    return res[0]
    


def get_idx(x):
    idx=cursor.execute("SELECT ind FROM PRODS_AMAAN WHERE names = ?", x).fetchall()[0][0]
    return idx


def recommend_product(product):
    recommendations=[]
    index = get_idx(product)
    try:
        for i in product_indices[index][1:]:
            ind = cursor.execute("SELECT ids FROM PRODS_AMAAN WHERE ind=?",int(i)).fetchall()[0][0]
            print(ind)
            recommendations.append(ind)
    except IndexError:
        recommendations=[]

    return recommendations
            
def get_seller_products(email):
    res=[]
    sellers_prods_ids = cursor.execute("SELECT ids FROM PRODS_AMAAN where manufacturer = ?", email).fetchall()
    for prod_id in sellers_prods_ids:
        res.append(prod_id[0])
    return res
