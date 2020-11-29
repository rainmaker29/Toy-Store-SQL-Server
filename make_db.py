import pyodbc
import pandas as pd
conn = pyodbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.6.so.1.1};'
                      'Server=localhost;'
                      'Database=Products;'
                      'UID=AMAAN;'
                      'PWD=AMAAN@123')

cursor = conn.cursor()


df = pd.read_csv("products.csv")

cursor.execute("CREATE TABLE PRODS_AMAAN (manufacturer VARCHAR(100),price FLOAT,number_available_in_stock FLOAT, number_of_reviews FLOAT, number_of_answered_questions FLOAT,average_review_rating FLOAT,customers_who_bought_this_item_also_bought VARCHAR(100),items_customers_buy_after_viewing_this_item VARCHAR(100),sellers VARCHAR(500),used_or_unused VARCHAR(100),category VARCHAR(100),sub_category VARCHAR(100),names VARCHAR(1000),ids VARCHAR(100),ind INT)")



# conn.commit()

for index in range(len(df)):
    row = df.iloc[index]
    cursor.execute("INSERT INTO PRODS_AMAAN (manufacturer,price,number_available_in_stock,number_of_reviews,number_of_answered_questions,average_review_rating,customers_who_bought_this_item_also_bought,items_customers_buy_after_viewing_this_item,sellers,used_or_unused,category,sub_category,names,ids,ind) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
     row.manufacturer, row.price, row.number_available_in_stock,row.number_of_reviews,row.number_of_answered_questions,row.average_review_rating,row.customers_who_bought_this_item_also_bought,row.items_customers_buy_after_viewing_this_item,row.sellers,row.used_or_unused,row.category,row.sub_category,row.names,row.ids,index)

conn.commit()
cursor.close()

print("SUCESS !!!!!!!!-----------------------------")



# df.to_sql("PRODS",conn,if_exists="replace",index=False)
# sql_query = pd.read_sql_query('SELECT * FROM TestDB.dbo.Inventory',conn)
