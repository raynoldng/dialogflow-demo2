#!/usr/bin/env python

import urllib
import urllib.request
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") == "shipping.cost":
        return shippingCost(req)
    elif req.get("result").get("action") == "bus.eta":
        return busETA(req)


def busETA(req):
    if req.get("result").get("action") != "bus.eta":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    busStopId = parameters.get("busStopId")
    busNo = parameters.get("busNo")

    print("result", result)

    APIURL = "https://arrivelah.herokuapp.com/?id="
    url = APIURL + str(busStopId)
    print("api url:", url)
    res = urllib.request.urlopen(APIURL + str(busStopId)).read()
    # res = requests.get('http://example.com').content
    print("res_read:", res)
    resJSON = json.loads(res)
    print("api response;", resJSON)
    busRowResult = [s for s in resJSON["services"] if s["no"] == str(busNo)]
    assert(len(busRowResult) == 1)
    bus = busRowResult[0]
    # now = datetime.now(timezone.utc)
    currTime = datetime.datetime.now(timezone.utc)
    nextTime = parser.parse(bus["next"]["time"])
    subTime = parser.parse(bus["subsequent"]["time"])
    # parser.parse("2017-12-11T12:07:41+08:00")
    print("times:", currTime, nextTime, subTime)
    nextDelta = nextTime - currTime
    subDelta = subTime - currTime
    print(nextDelta, subDelta)
    eta = (nextDelta.seconds // 60, subDelta.seconds // 60)
    speech = "Eta of bus " + str(busNo) + " at stop " + str(busStopId) + " is " + str(eta[0]) \
        + " and " + str(eta[1]) + " minutes"
    print("returning as speech:", speech)
    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
    }



def shippingCost(req):
    if req.get("result").get("action") != "shipping.cost":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    zone = parameters.get("shipping-zone")

    cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}

    speech = "The cost of shipping to " + zone + " is " + str(cost[zone]) + " euros."

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')