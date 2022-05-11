from flask import Flask
from flask_cors import CORS
from propagator import Propagator
app = Flask(__name__)
CORS(app)

@app.route('/')
def Home():
    return 'This is the Propagators homepage'
 
@app.route('/SatList')
def satelliteList():
    prop = Propagator()
    satList = prop.getSatList()
    return satList

@app.route('/Propagate')
def propagateSatellites():
    prop = Propagator()
    path = prop.getCZMLDoc()
    return path

if __name__ == '__main__':
    app.run(debug=True)
