#!/usr/bin/env python3
"""
pyPhin by Dylan Starink - An Unoffical pHin Python API
Copyright (C) 2020 StarDylan
https://github.com/StarDylan/pyPhin

"pHin" is a trademark owned by ConnectedYard, Inc., see www.phin.co for more information.
I am in no way affiliated with the ConnectedYard, Inc. organization.

"""

import requests
import json
import copy
import re

class pHin():

	baseUrl = "https://api.phin.co"

	def __init__(self):
		pass

	def login(self, contact, deviceUUID):

		self.checkRequest(reqJson)
		self.checkEmail(contact)


		''' urls
		{
			"refreshToken": "/refreshtoken",
			"signin": "/signincontact",
			"success": true,
			"versionCheck": "/version"
		}
		'''
		urls = json.loads(requests.get(self.baseUrl + "/urls").text)

		''' signin
		{
			"success": true,
			"verifyUrl": <verify_route>,
			"token": <token>
		}
		'''
		reqJson = json.loads(requests.post(self.baseUrl+urls["signin"],
			json={"contact":contact,"deviceType":"python"},
			headers=createHeader(deviceUUID)).text)




		#Returns Route needed to verify
		return reqJson["verifyUrl"]

	def verify(self, contact, deviceUUID, verifyUrl, verificationCode):

		if not verificationCode.isnumeric():
			raise Exception("Verification Code is not Numeric!")
		self.checkUrlRoute(verifyUrl)
		self.checkEmail(contact)

		''' verify_route
		{n
			"success": true,
			"existing": <if account exists>,
			"auth_token": <auth_token>,
			"refresh_token": <refresh_token>,
			"user": {
				"locationsUrl": "/users/1234/locations",
				"userRefreshTokenUrl": "/users/1234/refreshToken",
			}
		}
		'''
		req = requests.post(
			self.baseUrl+verifyUrl,
			json={"contact":contact,
				"deviceId":deviceUUID,
				"verificationCode":verificationCode},
			headers=createHeader(deviceUUID))

		reqJson = json.loads(req.text)

		if not reqJson["success"]:
			raise Exception(reqJson)
		if "existing" in reqJson:
			raise Exception("Contact does not exist!")

		authToken = reqJson["auth_token"]
		refreshToken = reqJson["refresh_token"]
		locationUrl = reqJson["user"]["locationsUrl"]
		userRefreshUrl = reqJson["user"]["userRefreshTokenUrl"]


		''' locations
		{
		   "success":true,
		   "locations":[
			  {
				 "vesselSummaries":[
					{
					   "disc":{
							"temperature":{
								"celsius":21.25,
								"fahrenheit":70.3
						  }
					   }
					}
				 ]
				"resources":{
					"vessels": {
						"route":"/users/1234/locations/1234/vessels"
					}
				}
			  }
		   ]
		}
		'''
		req = requests.get(
			self.baseUrl+locationUrl,
			headers=self.createHeader(deviceUUID, authToken, "2.0.1")
			)
		reqJson = json.loads(req.text)

		self.checkRequest(reqJson)

		vesselUrl = reqJson["locations"][0]["resources"]["vessels"]["route"]

		#Auth Dictionary Structure needed to access data.
		authData = {"authToken":authToken,"vesselUrl":vesselUrl}

		return authData

	def getData(self, authToken, deviceUUID, vesselUrl):

		self.checkUrlRoute(vesselUrl)

		data = {}

		data["waterData"] = self.getWaterData(
			authToken,
			deviceUUID,
			vesselUrl)

		return data

	def getWaterData(self, authToken, deviceUUID, vesselUrl):


		req = requests.get(
			self.baseUrl+vesselUrl,
			headers=self.createHeader(deviceUUID, authToken, "2.0.0")
			)

		reqJson = json.loads(req.text)
		self.checkRequest(reqJson)

		data = {}

		for dataType in ["TA","CYA","TH"]:
			data[dataType] = reqJson["vessels"][0]["waterReport"][dataType]["value"]
		data["temperature"] = reqJson["vessels"][0]["disc"]["temperatureF"]
		data["status"] = reqJson["vessels"][0]["disc"]["title"]

		'''Sample Return data
		{
			"TA":100,
			"CYA": 40,
			"TH": 170
			"temperature":70.9
			"status":"balanced"
		}
		'''
		return data

	def createHeader(self, deviceUUID, authToken=None, version="1.0.0"):
		headers = {"x-phin-concise":"true",
			"x-phin-reporting-app-id":"ios-app",
			"x-phin-reporting-device-id":deviceUUID}
		headers["Accept-Version"] = version
		if authToken != None:
			headers["Authorization"] = "Bearer " + authToken
		return headers

	def checkRequest(self, json):
		if not json["success"]:
			raise Exception(json)
	def checkUrlRoute(self, urlRoute):
		if re.match("^\/",urlRoute) == None:
			raise Exception("Not a Valid URL Route!")
	def checkEmail(self, email):
		if re.match("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$",email) == None:
			raise Exception("Not a Valid Email!")
