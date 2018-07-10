ifrom flask import Flask, request
from flask_restful import Resource, Api
import json
from json import dumps
from time import sleep, time
import flask
import random
from flask_cors import CORS
from gpiozero import LED

app = Flask(__name__)
api = Api(app)
CORS(app)
cors = CORS(app, resources={r"/api/*":{"origins":"*"}})

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

def clear():
    enablePumps()
    sleep(20)
    disablePumps()

def enablePumps():
    for i, v in enumerate(pump_pins):
        v.on()
        status[i] = 1

def disablePumps():
    for i, v in enumerate(pump_pins):
        v.off()
        status[i] = 0

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

def pour(drink_name):
    if isAvailable:
        r = recipe(drink_name)
        start = time()
        total_time = secs_to_pour(reduce(max, r.values()))

        for ingredient in r:
            enablePump(ingredient)
            sleep(5)

        while (time() - start) < total_time:
            per_tube_cl_poured = cl_per_sec * (time() - start)

            for ingredient in r:
                if r[ingredient] - per_tube_cl_poured <= 0:
                    disablePump(ingredient)

           # sleep(0.2)

        for ingredient in r:
            disablePump(ingredient)

class Switch_On(Resource):
    def get(self):
        result = ""
        if isAvailable():
            result = {'state':'Starting'}
            enablePumps()
        else:
            result = {'state':'Busy'}
        return flask.jsonify(result)

class Switch_Pump(Resource):
    def get(self):
        result = ""
        if isAvailable():
            result = {'state':'Starting'}
            status[0] = 1
            pump_pins[0].on()
        else:
            result = {'state':'Busy'}
        return flask.jsonify(result)

class Switch_Off(Resource):
    def get(self):
        result = {'state':'Stopping'}
        disablePumps()
        return flask.jsonify(result)

class GetCurrentStatus(Resource):
   def get(self):
      result = {'Available':isAvailable()}
      return flask.jsonify(result)

class Clear(Resource):
    def get(self):
        clear()
        return "Clearing!"

class DemoRecipe(Resource):
   def get(self):
      result = ""
      if isAvailable():
         pour("trustly special")
         result = {'state':'Drink is ready'}
      else:
         result = {'state':'Busy'}
      return flask.jsonify(result)

class CranberryVodka(Resource):
   def get(self):
      result = ""
      if isAvailable():
         pour("cranberry vodka")
         result = {'state':'Drink is ready'}
      else:
         result = {'state':'Busy'}
      return flask.jsonify(result)

class Vodka(Resource):
   def get(self):
      result = ""
      if isAvailable():
         pour("vodka")
         result = {'state':'Drink is ready'}
      else:
         result = {'state':'Busy'}
      return flask.jsonify(result)

class Cranberry(Resource):
   def get(self):
      result = ""
      if isAvailable():
         pour("cranberry")
         result = {'state':'Drink is ready'}
      else:
         result = {'state':'Busy'}
      return flask.jsonify(result)

api.add_resource(Switch_On, '/on')
api.add_resource(Switch_Pump, '/pump')
api.add_resource(Switch_Off,'/off')
api.add_resource(GetCurrentStatus,'/status')
api.add_resource(Clear,'/clear')
api.add_resource(DemoRecipe,'/demo')
api.add_resource(CranberryVodka,'/cranberryvodka')
api.add_resource(Vodka,'/vodka')
api.add_resource(Cranberry,'/cranberry')

if __name__ == '__main__':
    app.run(port='2000', host='0.0.0.0')
