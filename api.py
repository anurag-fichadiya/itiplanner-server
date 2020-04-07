# from flask import Flask
# app = Flask(__name__) # create a Flask app

# @app.route("/")
# def hello():
    # return "Hello World!"
    
# if __name__=='__main__':
    # app.run(port=3000, debug=True)

# from flask import Flask, request, jsonify, render_template # loading in Flask
# import pandas as pd                                        # loading pandas for reading csv
# from sklearn.externals import joblib                       # creating a Flask application

# app = Flask(__name__, template_folder = 'template')

# Load the model


# creating predict url and only allowing post requests.
# @app.route('/', methods=['GET','POST'])
# def home():
    # if request.method == 'POST':
        # data = request.form.get('text')
        # # Make prediction
        # print('This is data printed', data)
        # pred = model.rec_from_user(data)
        # print('This is pred output', pred) #OF type dataframe
        # return render_template('index.html', sentiment=pred.to_html)
    # return render_template('index.html', sentiment='')
#WITHOUT WEBSITE
# def predict():
    # # Get data from Post request
    # data = request.get_json()
    # # Make prediction
    # df = pd.DataFrame([str(data['text'])], columns=['content'])
    # print(df.head())
    # # making predictions
    # pred = model.rec_from_user(df)
    # print(pred)
    # # returning the predictions as json
    # return jsonify(pred)

# if __name__ == '__main__':
    # app.run(port=3000, debug=True)
    
from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
from sklearn.externals import joblib

app = Flask(__name__)
api = Api(app)

CORS(app)

model = joblib.load('model.pkl')

@app.route("/")
def hello():
    return jsonify({'text':'Hello World!'})

class iti_list(Resource):
    def get(self, uid):
        #print(uid)
        df = model.rec_from_user(uid)
        print("This is printed dataframe got from the model and converted to dict - now return to angular \n",df.to_dict('index'))
        return df.to_dict('index')#.to_json(orient='records')

class iti_details(Resource):
    def get(self, iti_id):
        print('ITI id:' + iti_id)
        df = model.get_iti_details(iti_id)
        print("this is df from api.py", df);
        return df.to_dict()

class iti_all(Resource):
    def get(self):
        df = model.get_iti_all()
        print("this is df from api.py for all", df);
        return df.to_dict('index') #IMP to write this index

api.add_resource(iti_all, '/itinerary') # Route_1
api.add_resource(iti_list, '/user/<uid>') # Route_1
api.add_resource(iti_details , '/itinerary/<iti_id>') # Route_3


if __name__ == '__main__':
     app.run(port=5002)