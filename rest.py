from flask import Flask, request
from flask_restful import Resource, Api
import json
from json import dumps
from time import sleep, time
import flask
import random
from gpiozero import LED

app = Flask(__name__)
api = Api(app)

pump_pins = [LED(17),LED(22),LED(27)]
status = [0,0,0] 

cl_per_sec = 0.1

def secs_to_pour(cl):
    return cl / cl_per_sec

def recipe(drink_name):
    with open('drinks.json') as drinks_file:
        drinks = json.load(drinks_file)
        return drinks[drink_name]

def pump_by_liquid(liquid):
    with open('pumpsByLiquid.json') as pump_by_liquid_file:
        pump_by_liquid = json.load(pump_by_liquid_file)
        return pump_by_liquid[liquid]

def enablePump(liquid):
    global status
    pump_index = pump_by_liquid(liquid)
    pump_pins[pump_index].on()
    status[pump_index] = 1

def disablePump(liquid):
    global status
    pump_index = pump_by_liquid(liquid)
    pump_pins[pump_index].off()
    status[pump_index] = 0

def isAvailable():
    global status
    for pump_status in status:
        if pump_status is 1:
	    return False
    return True

def demoRecipe():
    r = recipe('vodka cranberry')
    start = time()

    for ingredient in r:
            enablePump(ingredient)

    for ingredient in r:
        if r[ingredient] <= 0:
            disablePump(ingredient)

        sleep(0.01)
        r[ingredient] -= cl_per_sec * (time() - start)

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
