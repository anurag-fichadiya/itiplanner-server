from model_src import pred_model
from sklearn.externals import joblib
a = pred_model()
joblib.dump(a, 'model.pkl')

print("Model dumped!")

a = joblib.load('model.pkl')



