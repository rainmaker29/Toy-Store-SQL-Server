#!/usr/bin/env python
import views
from  CustomerDB import mongo_global_init

app = views.app

if __name__=="__main__":
    mongo_global_init()
    app.run(host="0.0.0.0",debug=True)
