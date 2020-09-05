import requests
import json
import copy

class pHin():

	baseUrl = "https://api.phin.co"

	def __init__(self):


	def login(self, contact, deviceUUID):

		baseHeaders = {"x-phin-concise":"true",
			"x-phin-reporting-app-id":"ios-app",
			"x-phin-reporting-device-id":deviceUUID}

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
			headers=baseHeaders).text)



		if reqJson["success"]:
			#Returns Route to verify
			return reqJson["verifyUrl"]
		else:
			raise Exception(reqJson)

	def verify(self, contact, verifyUrl, deviceUUID, verificationCode):

		baseHeaders = {"x-phin-concise":"true",
			"x-phin-reporting-app-id":"ios-app",
			"x-phin-reporting-device-id":deviceUUID}


		''' verify_route
		{
			"success": true,
			"existing": <if account exists>,
			"auth_token": <auth_token>,
			"refresh_token": <refresh_token>,
			"user": {
				"locationsUrl": "/users/3482/locations",
				"userRefreshTokenUrl": "/users/3482/refreshToken",
			}
		}
		'''
		req = requests.post(
			self.baseUrl+verifyUrl,
			json={"contact":contact,
				"deviceId":deviceUUID,
				"verificationCode":verificationCode},
			headers=baseHeaders)

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
						"route":"/users/.../locations/.../vessels"
					}
				}
			  }
		   ]
		}
		'''
		req = requests.get(
			self.baseUrl+locationUrl,
			headers=self.createHeader(authToken, deviceUUID, "2.0.1")
			)
		reqJson = json.loads(req.text)

		if not reqJson["success"]:
			raise Exception(reqJson)

		vesselUrl = reqJson["locations"][0]["resources"]["vessels"]["route"]

		auth = {"authToken":authToken,"vesselUrl":vesselUrl,"UUID":deviceUUID}
		return json.dumps(auth)

	def createHeader(self, authToken, deviceUUID, version="1.0.0"):
		tempHeader = {"x-phin-concise":"true",
			"x-phin-reporting-app-id":"ios-app",
			"x-phin-reporting-device-id":deviceUUID}
		tempHeader["Accept-Version"] = version
		tempHeader["Authorization"] = "Bearer " + authToken
		return tempHeader

	def getData(self, auth, data):

		dataCluster = json.loads(auth)

		if data.upper() == "TA" or "CYA" or "TH":
			return self.getWaterQuality(dataCluster["authToken"], dataCluster["vesselUrl"], dataCluster["UUID"], data.upper())

	def getWaterQuality(self, authToken, vesselUrl, deviceUUID, waterQualityType):


		req = requests.get(
			self.baseUrl+vesselUrl,
			headers=self.createHeader(authToken,deviceUUID, "2.0.0")
			)
		reqJson = json.loads(req.text)
		print(reqJson)


		return reqJson["vessels"][0]["waterReport"][waterQualityType]["value"]





