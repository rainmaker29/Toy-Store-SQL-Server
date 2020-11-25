from flask import Flask,render_template,request,redirect,flash
from wtforms import Form, StringField, SelectField
import numpy as np
import pandas as pd


app = Flask(__name__)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

class SearchForm(Form):
    search = StringField('')

df = pd.read_csv('products.csv')

@app.route('/',methods=['GET','POST'])
def home():
    search = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', form=search,products=df['ids'].to_list()[:12])

@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
    if search.data['search'] == '':
        flash("Empty search")
        return redirect('/')
    
    for i in range(len(df)):
        if df.iloc[i]['name']==search.data['search']:
            print("found")
            results.append(df.iloc[i]['ids'])
            print(results)
    


    # for prod_name in df['name'].to_list():
    #     if prod_name==search.data['search']:
    #         print("found")
    #         results.append(prod_name)
    #         print(results)
    
    
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        return render_template('results.html',form=search, results=results)

    
@app.route('/product/<string:product_id>')
def product(product_id):
    return render_template('product.html',product_id=product_id)

@app.context_processor
def getname():
    def get_name_by_id(id):
        return df.loc[df['ids']==id,'name'].to_list()[0]
    return dict(get_name_by_id=get_name_by_id)


@app.context_processor
def get_length():
    def getlen(obj):
        return len(obj)
    return dict(getlen=getlen)

@app.context_processor
def getall():
    def get_all(id):
        return df.loc[df['ids']==id,:]
    return dict(get_all=get_all)