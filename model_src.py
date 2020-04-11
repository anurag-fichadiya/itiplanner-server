#ML model imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sympy
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import manhattan_distances
from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics import jaccard_similarity_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib
#firebase imports
import pyrebase
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
#class
class pred_model:
#constructor
    def __init__(self):
        self.set_firebase_data()
#set firebase data function
    def set_firebase_data(self):
#init firebase
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
#for iti table
        iti_list = db.child("Itinerary").get()
        df = pd.DataFrame()
        for city in iti_list.each():
            city_name = city.key()
            for iti_name, iti_details in city.val().items():
                dfd = pd.DataFrame.from_dict(json_normalize(iti_details), orient='columns')
                dfd['id'] = iti_name;
                dfd['city'] = city_name;
                df = df.append(dfd)
#for user table
        user_list = db.child("Users").get()
        dfu = pd.DataFrame()
        for key,value in user_list.val().items():
            q=[key,value['email']]
            temp=pd.DataFrame([q])
            dfu=dfu.append(temp)
        dfu.columns=["userid","email"]
#for history table
        history=db.child("History").get().val()
        dfh=pd.DataFrame()
        for key,value in history.items():
            for keyt,valuet in value.items():
                a=list(valuet.items())
                q=[key,keyt,a[0][1],a[1][1]]
                temp=pd.DataFrame([q])
                dfh=dfh.append(temp)
        dfh.columns=["userid","Itineraryid","rating","review"]
#init for reco model        
        self.U = dfu #users info
        self.I = df #iternary info
        self.H = dfh #user history info
#init tags
        tag = self.I.tags
        tag = tag.values.tolist()
        tag = pd.DataFrame(tag)
        tag.columns = ['tag0','tag1','tag2','tag3','tag4']
        self.I = self.I.drop(columns = ['tags'])
        self.I["tag0"] = tag["tag0"].values
        self.I["tag1"] = tag["tag1"].values
        self.I["tag2"] = tag["tag2"].values
        self.I["tag3"] = tag["tag3"].values
        self.I["tag4"] = tag["tag4"].values
        s = self.I.shape
        l = list()
        for i in range(s[0]):
            k = self.I["placeModels"].iloc[i]
            temp = []
            tc = 0
            plist = ""
            for j in range(len(k)):
                h = k[j]
                c = int(h["price"])
                n = int(h["noOfDays"])
                p = h["place"]
                tuple = (p,n,c)
                temp.append(tuple)
                tc = tc+c
            self.I["placeModels"].iloc[i] = temp
            l.append(tc)
        self.I["totalCost"]=l
        self.I = self.I.replace(np.nan, '', regex=True)
        self.I['bag'] = ""
        i = 0
        self.I['bag']=self.I['tag0'] +" "+self.I['tag1'] +" "+ self.I['tag2'] +" "+self.I['tag3'] +" "+ self.I['tag4']
        self.I['reviewbag']=""
        temp=list()
        for id in self.I.id:
            k=str("")
            for h in self.H[self.H['Itineraryid']==id].review:
                k=k+" "+h
            temp.append(k)
        self.I["reviewbag"]=temp
        self.I['bag']=self.I['bag']+" "+self.I['reviewbag']
        self.I=self.I.drop(columns=['reviewbag'])
        # IF YOU GET AN ERROR IN THE ABOVE LINE THEN REMOVE COMMENT FROM THE FOLLOWING LINE AND DISCARD THE ABOVE LINE. GOOGLE SAYS THEN YOU SHOULDN'T GET AN ERROR
        #self.I=self.I.drop('reviewbag', axis=1)
        
        count = CountVectorizer()
        count_matrix = count.fit_transform(self.I['bag'])
# generating the cosine similarity matrix
        self.cosine_sim = cosine_similarity(count_matrix,dense_output=1)
        np.fill_diagonal(self.cosine_sim,0)
        self.cosine_sim=pd.DataFrame(self.cosine_sim,index=self.I['id'],columns=self.I['id'])
#cosine_sim.head() # [i][j]=similarity between ith and jth Itinerary
        Umean = self.H.groupby(by="userid")['rating'].mean()
        Imean = self.H.groupby(by="Itineraryid")['rating'].mean()
        tempH = pd.merge(self.H,Umean,how='outer',on='userid')
        tempH['normalrating']=tempH['rating_x']-tempH['rating_y']
        table=pd.pivot_table(tempH,values='normalrating',index='userid',columns='Itineraryid')
        for id in self.U.userid:
            temp=table[table.index==id]
            if(temp.empty):
                table.loc[id] = Imean
        self.Utable=table.fillna(table.mean(0)) #NaN values are replaced by respective Itinerary's average normal rating
        self.Utable=self.Utable.rank(axis=1,method='dense',ascending=False) # now the table has rank 1 for highest ranking
#rec from iti function
    def rec_from_itinerary(self, Itineraryid,similarity_matrix,no_rec):
        temp=similarity_matrix[similarity_matrix.index==Itineraryid] #temp= row with index=Itineraryid
        temparray=temp.to_numpy()[0] #temparray= array form of the above
        order=temparray.argsort() #sorted(ascending) indices of the above
        order=order[::-1] #sorted(descending) indices 
        reccomandations = pd.DataFrame(columns=self.I.columns)
        for i in range(no_rec):
            a=self.I[self.I['id']==temp.columns[order[i]]]
            reccomandations=reccomandations.append(a)
        a=self.I[self.I['id']==Itineraryid]
        reccomandations=reccomandations.append(a)
        return reccomandations
#rec from user function
    def rec_from_user(self, userid):
#setting up latest firebase data
        self.set_firebase_data()
#taking user data
        temp=self.Utable[self.Utable.index==userid]  
        n=10
        i=0
        j=1         # j is rank of Iti for a user
        ans=pd.DataFrame(columns=self.I.columns)
        while(i<n):
            tt=temp.columns.where(temp.values==j)
            tt=tt[0]
            j=j+1
            tt=pd.DataFrame(tt)
            a=np.where(tt.notnull().transpose()==True)[1]
            if(len(a)==0):
                break
            if(len(a)==1):
                Is=self.rec_from_itinerary(tt[0][a[0]],self.cosine_sim,3)
                ans=ans.append(Is)
                i=i+1
            else:
                k=0
                while(k<len(a)):
                    Is=self.rec_from_itinerary(tt[0][a[k]],self.cosine_sim,3)
                    ans=ans.append(Is)
                    k=k+1
                    i=i+1      
        #z=ans.groupby('id').count()['bag']
        #z['id']=z.index
#logic of dropping duplicates
        tempo = pd.DataFrame();
        tempo['id'] = ans['id'].drop_duplicates()
        fans = pd.DataFrame();
        for i in tempo['id']:
            te = 0
            for j in ans['id']:
                if(i == j):
                    fans = fans.append(ans.iloc[te])
                    break
                te = te + 1
        #ans = pd.merge(ans, tempo, on = 'id', how='inner'); - NOT WORKING
        ans = fans
        #ans=ans.drop_duplicates() - NOT WORKING
        #ans = pd.DataFrame(np.unique(ans), columns=ans.columns) - NOT WORKING
        #ans = ans.loc[ans.astype(str).drop_duplicates().index].loc[0,'placeModels'] - NOT WORKING
        #ans = pd.merge(ans,z,on='id') # bag_x= bag of Itinerary tags and bag_y=frequency of an Itinerary
        #ans=ans.sort_values(by=['bag_y','average rating'],ascending=[False,False])
        h=self.H[self.H.userid==userid]       #Users history
        ans=ans.loc[~ans.id.isin(h.Itineraryid)]  #exclude Itineraries from history
        ans=ans.sort_values(by=['ratings'], ascending=False)
        s = pd.Series(np.arange(len(ans.index)))
        ans = ans[['city', 'id','daysCount', 'placeModels', 'ratings', 'totalCost']].set_index([s]) #ans ready
        ans = self.format_iti(ans)
#finally select the required columns to send
        print("This will be returned from model \n", ans);
        return ans 
    def format_iti(self, df):
        mainplaces = list([]);
        for index, row in df.iterrows():
            t = row['placeModels']
            places = [];
            for i in t:
                places.append(i[0])
            mainplaces.append(places)
        df = df.assign(places = mainplaces)
        df = df[['id','city','daysCount', 'places', 'ratings', 'totalCost']];
        print("Final df", df)
        return df;
    def get_iti_details(self, iti_id):
        for key, val in self.I.iterrows():
            if val['id'] == iti_id:
                ans = val
                break
        print("this is the row that will be passed \n", ans)
        return ans;
    def get_iti_all(self):
        s = pd.Series(np.arange(len(self.I.index)))
        ans = self.I.set_index([s])
        ans = self.format_iti(ans)
        print("this returned from all ", ans)
        return ans;
    def user_history(self, uid):
        print("History tabel", self.H);
        ans = [ ]
        for key, val in self.H.iterrows():
            if(val['userid'] == uid):
                ans.append(val['Itineraryid'])
        fans = pd.DataFrame()
        print("ans ", ans)
        for i in ans:
            for key, value in self.I.iterrows():
                if(value['id'] == i):
                    fans = fans.append(value)
        if len(ans) == 0:
            return fans
        print("fans", fans)
        s = pd.Series(np.arange(len(fans.index)))
        fans = fans.set_index([s])
        fans = self.format_iti(fans)
        print("This will be returned from user history table", fans)
        return fans