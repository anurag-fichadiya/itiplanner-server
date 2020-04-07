#imports firebase
import pyrebase
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize

config = {
    "apiKey" : "AIzaSyAa3c2pbkTRamVhqy1wkiylXsYgAM194Qg",
    "authDomain" : "iti-planner.firebaseapp.com",
    "databaseURL": "https://iti-planner.firebaseio.com",
    "projectId": "iti-planner",
    "storageBucket": "iti-planner.appspot.com",
    "messagingSenderId": "425288159072",
    "appId": "1:425288159072:web:4cd8f82ee2cd80faf55805"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
#print(db.child("Itinerary").get().val())

iti_list = db.child("Itinerary").get()

df = pd.DataFrame()

for city in iti_list.each():
    #print(city.key())
    for iti_name, iti_details in city.val().items():
        #print("iti name ",iti_name)
        #print("iti_details ", iti_details)
        #print(pd.DataFrame.from_dict(json_normalize(iti_details), orient='columns'))
        #print("Check NOW \n")
        dfd = pd.DataFrame.from_dict(json_normalize(iti_details), orient='columns')
        dfd['id'] = iti_name;
        df = df.append(dfd)
    #print("New City Now: \n")
    
# print("Itinerary List: \n")
# print(df)
#print("End")


user_list = db.child("Users").get()#.val()
#print(user_list)
dfu = pd.DataFrame()

for user in user_list.each():
    #print(user.val())
    dfu = dfu.append(pd.DataFrame.from_dict(json_normalize(user.val()), orient='columns'))
    #dfu.append(pd.read_json(user.val()))

# print("User List: \n")
# print(dfu)
#print("End")

#import unicodedata - for py 2.7

history=db.child("History").get().val()
dfh=pd.DataFrame()
for key,value in history.items():
    #uid=unicodedata.normalize('NFKD', key).encode('ascii','ignore') - for py 2.7
    for keyt,valuet in value.items():
        a=list(valuet.items())
        q=[key,keyt,a[0][1],a[1][1]]
        temp=pd.DataFrame([q])
        dfh=dfh.append(temp)
#       print(temp)
dfh.columns=["userid","Itineraryid","rating","review"]
# print("History List: \n")
# print(dfh)
#print("End")
#making a func
s = pd.Series(np.arange(len(df.index)))
df = df[['id','daysCount', 'placeModels', 'ratings']].set_index([s]) #ans ready
#print(df[['id','daysCount', 'placeModels', 'ratings']])
rowlist = [];
mainplaces = list([]);
for index, row in df.iterrows():
    #print(index)
    #print(row['placeModels'])
    t = row['placeModels']
    c = 0
    places = [];
    for i in t:
        #print(i)
        for key, val in i.items():
            #print(key)
            #print(val)
            if(key == 'price'):
                c = c + int(val)
            if(key == 'place'):
                places.append(val)
    #print(c)
    mainplaces.append(places)
    rowlist = np.append(rowlist, c)
    #print("Next iti");
#print(list(rowlist))
#print(mainplaces)
df = df.assign(totalCost = rowlist)
df = df.assign(places = mainplaces)
df = df[['id','daysCount', 'places', 'ratings', 'totalCost']];
print(df)
#------------------------------------------------------------------

# #included in model_src.py
# import pyrebase
# import pandas as pd 
# from pandas.io.json import json_normalize
# config = {
    # "apiKey" : "AIzaSyAa3c2pbkTRamVhqy1wkiylXsYgAM194Qg",
    # "authDomain" : "iti-planner.firebaseapp.com",
    # "databaseURL": "https://iti-planner.firebaseio.com",
    # "projectId": "iti-planner",
    # "storageBucket": "iti-planner.appspot.com",
    # "messagingSenderId": "425288159072",
    # "appId": "1:425288159072:web:4cd8f82ee2cd80faf55805"
# }

# firebase = pyrebase.initialize_app(config)

# db = firebase.database()

# #print(db.child("Itinerary").get().val())

# iti_list = db.child("Itinerary").get()

# df = pd.DataFrame()

# for city in iti_list.each():
    # #print(city.key())
    # for iti_name, iti_details in city.val().items():
        # #print("iti name ",iti_name)
        # #print("iti_details ", iti_details)
        # #print(pd.DataFrame.from_dict(json_normalize(iti_details), orient='columns'))
        # #print("Check NOW \n")
        # dfd = pd.DataFrame.from_dict(json_normalize(iti_details), orient='columns')
        # dfd['id'] = iti_name;
        # df = df.append(dfd)
    # #print("New City Now: \n")   

# print("Itinerary List: \n")
# print(df)
# print("End")

# #----- Making User Table DataFrame

# user_list = db.child("Users").get()#.val()
# print(user_list)
# dfu = pd.DataFrame()

# for user in user_list.each():
    # #print(user.val())
    # dfu = dfu.append(pd.DataFrame.from_dict(json_normalize(user.val()), orient='columns'))
    # #dfu.append(pd.read_json(user.val()))
    
# print(dfu);