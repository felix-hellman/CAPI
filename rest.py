from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from time import sleep
import flask
import random
from gpiozero import LED

app = Flask(__name__)
api = Api(app)

pumps = [LED(17),LED(22),LED(27)]
status = [0,0,0] 

rate = 0.1


def enablePump(number):
    global status
    pumps[number].on()
    status[number] = 1

def disablePump(number):
    global status
    pumps[number].off()
    status[number] = 0

def isAvailable():
    global status
    for pump_status in status:
        if pump_status is 1:
	    return False
    return True

def demoRecipe():
    enablePump(1)

class Switch_On(Resource):
    def get(self):
        result = ""
        if isAvailable():
            result = {'state':'Starting'}
            enablePump(0)
            enablePump(1)
            enablePump(2)
        else:
            result = {'state':'Busy'}
        return flask.jsonify(result)

class Switch_Off(Resource):
    def get(self):
        result = {'state':'Stopping'}
        disablePump(0)
        disablePump(1)
        disablePump(2)
        return flask.jsonify(result)

class GetCurrentStatus(Resource):
   def get(self):
      result = {'Available':isAvailable()}
      return flask.jsonify(result)

class DemoRecipe(Resource):
   def get(self):
      result = ""
      if isAvailable():
         demoRecipe()
         result = {'state':'Drink is ready'}
      else:
         result = {'state':'Busy'}
      return flask.jsonify(result)
         

api.add_resource(Switch_On, '/on')
api.add_resource(Switch_Off,'/off')
api.add_resource(GetCurrentStatus,'/status')
api.add_resource(DemoRecipe,'/demo')

if __name__ == '__main__':
    app.run(port='2000', host='0.0.0.0')
