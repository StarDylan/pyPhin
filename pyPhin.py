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
import re
import logging


class pHin():

	baseUrl = "https://api.phin.co"

	'''init()
	Initializes the Library with Specified parameters

	logger - Used to pass in a logger for module to use

	All remaining parameters used to specify the amount
	of data points to be used in average calculation.
	A data point is roughly taken every hour.

	'''
	def __init__(self, logger=None,
		phDataPointAvgLen=5,
		orpMvDataPointAvgLen=5,
		batteryDataPointAvgLen=5,
		rssiDataPointAvgLen=1):
		if logger != None:
			self.logger = logger
		else:
			self.logger = logging.getLogger("nullLogger").addHandler(logging.NullHandler())

		try:
			self.phDataPointAvgLen = int(phDataPointAvgLen)
			self.orpMvDataPointAvgLen = int(orpMvDataPointAvgLen)
			self.batteryDataPointAvgLen = int(batteryDataPointAvgLen)
			self.rssiDataPointAvgLen = int(rssiDataPointAvgLen)
		except Exception as e:
			self.logger.critcal("ph, orp, or battery Data Point Avg Len is not an Integer! Exception: %s",e)

	'''login()
	Used to start verificaiton process by sending a verificaton
	email request.

	contact - email used to login to account
	deviceUUID - Any UUID

	Returns verificationUrl needed to call verify()
	'''
	def login(self, contact, deviceUUID):

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
		req = requests.post(self.baseUrl+urls["signin"],
			json={"contact":contact,"deviceType":"python"},
			headers=self.createHeader(deviceUUID))


		self.checkRequest(req)
		reqJson = json.loads(req.text)



		#Returns Route needed to verify
		return reqJson["verifyUrl"]

	'''verify()
	Used to get authorization to the pHin service.

	contact - email used to login to account
	deviceUUID - Any UUID
	verifyUrl - Url obtained from login()
	verficationCode - Numeric code obtained from contact email

	Returns authToken and vesselUrl in a python dictionary object
	'''
	def verify(self, contact, deviceUUID, verifyUrl, verificationCode):

		self.checkVerificationCode(verificationCode)
		self.checkUrlRoute(verifyUrl)
		self.checkEmail(contact)

		''' verify_route
		{
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
			headers=self.createHeader(deviceUUID))


		self.checkRequest(req)
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

		self.checkRequest(req)
		reqJson = json.loads(req.text)


		vesselUrl = reqJson["locations"][0]["resources"]["vessels"]["route"]

		#Auth Dictionary Structure needed to access data.
		authData = {"authToken":authToken,"vesselUrl":vesselUrl}

		return authData


	'''getData()
	Used to get the data from authorized account.

	authToken - Token recieved from login()
	deviceUUID - Any UUID
	vesselUrl - vesselUrl from login()

	Returns data in a python dictionary object:

	'''
	def getData(self, authToken, deviceUUID, vesselUrl):
		def merge(dict_list):
		    merged = {}
		    for item in dict_list:
		        for key in item.keys():
		            try:
		                merged[key].update(item[key])
		            except KeyError:
		                merged[key] = {}
		                merged[key].update(item[key])
		    return merged
		self.checkUrlRoute(vesselUrl)

		data = {}

		dataList = self.getWaterData(
			authToken,
			deviceUUID,
			vesselUrl)

		data = merge(dataList)


		return data

	def getWaterData(self, authToken, deviceUUID, vesselUrl):


		req = requests.get(
			self.baseUrl+vesselUrl,
			headers=self.createHeader(deviceUUID, authToken, "2.0.0")
			)


		self.checkRequest(req)
		reqJson = json.loads(req.text)

		data = {"waterData":{},"pool":{}}

		for dataType in ["TA","CYA","TH"]:
			try:
				data["waterData"][dataType.lower()] = reqJson["vessels"][0]["waterReport"][dataType]["value"]
			except:
				self.logger.error("Not able to access %s with %s",dataType,req.text)

		try:
			data["waterData"]["temperature"] = reqJson["vessels"][0]["disc"]["temperatureF"]
		except:
			self.logger.error("Not able to access temperature with %s",req.text)
		try:
			data["pool"]["status_title"] = reqJson["vessels"][0]["disc"]["name"]
		except:
			self.logger.error("Not able to access temperature with %s",req.text)
		try:
			data["pool"]["status_id"] = reqJson["vessels"][0]["disc"]["waterStatus"]["value"]
		except:
			self.logger.error("Not able to access status id with %s",req.text)

		chartData = self.getChartData(
			authToken,
			deviceUUID,
			reqJson["vessels"][0]["widgets"][0]["resources"]["appChartsWeek"]["route"])

		returnData = [data,chartData]


		'''Sample Return data
		[
			{
				"waterData":{
					"ta":100,
					"cya": 40,
					"th": 170,
					"temperature":70.9
				}
				"pool":{
					"status": "balanced",
					"index": 1
					}
			},
			{
				"waterData":{
					"ph":{"value":8.2, "status":1},
					"orp":{"value":800,"status":2}
				}
				"vesselData":{
					"battery":{"value":2000, "status":3},
					"rssi":{"value":-91,"status":3}
				}
			}
		]
		'''
		return returnData

	def getChartData(self, authToken, deviceUUID, chartUrl):
		req = requests.get(
			self.baseUrl + chartUrl,
			headers=self.createHeader(deviceUUID, authToken, "1.0.0")
			)
		self.checkRequest(req)
		reqJson = json.loads(req.text)

		chartData = {"waterData":{},"vesselData":{}}

		'''Status Codes
		1 - Needs Immediate Attention Low
		2 - Needs Attention Low
		3 - Ok
		4 - Needs Attention High
		5 - Needs Immediate Attention High
		'''

		#PH
		try:
			phAvg = sum(reqJson["ph"][-self.phDataPointAvgLen:])/self.phDataPointAvgLen

			phStatus = -1
			if phAvg < 6.8:
				phStatus = 1
			elif phAvg < 7:
				phStatus = 2
			elif phAvg >= 7 and phAvg <= 7.5:
				phStatus = 3
			elif phAvg > 7.5:
				phStatus = 4
			elif phAvg > 7.8:
				phStatus = 5
			else:
				self.logger.error("PH Status not Classified: PH_AVG=%s",phAvg)
			chartData["waterData"]["ph"] = {"value":phAvg,"status":phStatus}

		except Exception as e:
			self.logger.error("Can not Access PH: Exception=%s",e)
		#ORP
		try:
			orpAvg = sum(reqJson["orpMv"][-self.orpMvDataPointAvgLen:])/self.orpMvDataPointAvgLen

			orpStatus = -1
			if orpAvg < 300:
				orpStatus = 1
			elif orpAvg < 600:
				orpStatus = 2
			elif orpAvg >= 600 and orpAvg <= 875:
				orpStatus = 3
			elif orpAvg > 875:
				orpStatus = 5
			else:
				self.logger.error("ORP Status not Classified: ORP_AVG=%s",orpAvg)
			chartData["waterData"]["orp"] = {"value":orpAvg,"status":orpStatus}

		except Exception as e:
			self.logger.error("Can not Access ORP: Exception=%s",e)
		#BatteryMv
		try:
			batteryAvg = sum(reqJson["batteryMv"][-self.batteryDataPointAvgLen:])/self.batteryDataPointAvgLen

			batteryStatus = -1
			if batteryAvg < 1500:
				batteryStatus = 1
			elif batteryAvg > 3500:
				batteryStatus = 5
			else:
				batteryStatus = 3
			chartData["vesselData"]["battery"] = {"value":batteryAvg,"status":batteryStatus}

		except Exception as e:
			self.logger.error("Can not Access Battery: Exception=%s",e)

		#RSSI
		try:
			rssiAvg = sum(reqJson["rssi"][-self.rssiDataPointAvgLen:])/self.rssiDataPointAvgLen

			rssiStatus = -1
			if rssiAvg < -110:
				rssiStatus = 1
			elif rssiAvg > -20:
				rssiStatus = 5
			else:
				rssiStatus = 3
			chartData["vesselData"]["rssi"] = {"value":rssiAvg,"status":rssiStatus}

		except Exception as e:
			self.logger.error("Can not Access RSSI: Exception=%s",e)

		'''Sample ChartData Return
		{
			"waterData":{
				"ph":{"value":8.2, "status":1},
				"orp":{"value":800,"status":2}
			}
			"vesselData":{
				"battery":{"value":2000, "status":2},
				"rssi":{"value":-91,"status":1}
			}
		}
		'''
		return chartData

	def createHeader(self, deviceUUID, authToken=None, version=None):
		headers = {"x-phin-concise":"true",
			"x-phin-reporting-app-id":"ios-app",
			"x-phin-reporting-device-id":deviceUUID}
		if version != None:
			headers["Accept-Version"] = version
		if authToken != None:
			headers["Authorization"] = "Bearer " + authToken
		return headers

	def checkRequest(self, request):
		if request == None:
			raise Exception("Request is None!")
		try:
			reqJson = json.loads(request.text)
		except:
			raise Exception("Request is not Returning Json!")

		if not reqJson["success"]:
			raise Exception(json)

	def checkUrlRoute(self, urlRoute):
		if type(urlRoute) != str:
			logigng.critical("Url %s not a String!",urlRoute)
			raise Exception("Url not a String!")
		if re.match("^\/",urlRoute) == None:
			self.logger.critical("URL %s not Valid!", urlRoute)
			raise Exception("Not a Valid URL Route!")

	def checkEmail(self, email):
		if type(email) != str:
			self.logger.critical("Email %s not a String!", email)
			raise Exception("Email not a String!")

		if re.match("^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w+$",email) == None:
			self.logger.critical("Email %s not Valid!",email)
			raise Exception("Not a Valid Email!")

	def checkVerificationCode(self, verificationCode):
		if type(verificationCode) != str:
			self.logger.critical("Verification Code %s not a String!",verificationCode)
			raise Exception("Verification is not String!")

		if not verificationCode.isnumeric():
			self.logger.critical("Verification Code %s not Numeric")
			raise Exception("Verification Code is not Numeric!")
