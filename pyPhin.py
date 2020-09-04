import requests
import json

class pHin():

	baseUrl = "https://api.phin.co"

	urls = None
	baseHeaders = None

	authToken = None
	refreshToken = None

	#Configuable
	deviceUUID = "dbf58fc7-6501-47c7-9781-dc13aa3a5b50"

	def __init__(self,contact):
		self.contact = contact
		''' urls
		{
			"refreshToken": "/refreshtoken",
			"signin": "/signincontact",
			"success": true,
			"versionCheck": "/version"
		}
		'''
		self.urls = json.loads(requests.get(self.baseUrl + "/urls").text)

		self.baseHeaders = {"x-phin-concise":"true",
			"x-phin-reporting-app-id":"ios-app",
			"x-phin-reporting-device-id":self.deviceUUID}

	def sendAuthMessage(self):
		''' signin
		{
			"success": true,
			"verifyUrl": <verify_route>,
			"token": <token>
		}
		'''
		reqJson = json.loads(requests.post(self.baseUrl+self.urls["signin"],
			json={"contact":self.contact,"deviceType":"python"},
			headers=self.baseHeaders).text)
		if reqJson["success"]:
			#Returns Route to verify
			self.verifyRoute = reqJson["verifyUrl"]
			return
		else:
			raise Exception(reqJson)

	def authVerify(self,verificationCode):
		if self.verifyRoute == None:
			raise Exception("Call sendAuthMessage first!")

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
			self.baseUrl+self.verifyRoute,
			json={"contact":self.contact,
				"deviceId":self.deviceUUID,
				"verificationCode":verificationCode},
			headers=self.baseHeaders)

		reqJson = json.loads(req.text)

		if not reqJson["success"]:
			raise Exception(reqJson)
		if "existing" in reqJson:
			raise Exception("Contact does not exist!")

		self.authToken = reqJson["auth_token"]
		self.refreshToken = reqJson["refresh_token"]
		self.urls["locations"] = reqJson["user"]["locationsUrl"]
		self.urls["userRefresh"] = reqJson["user"]["userRefreshTokenUrl"]

