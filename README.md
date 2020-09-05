# pyPhin

## Simple Usage
1. Generate a UUID
```python
import uuid 
uuid = str(uuid.uuid4())
```
2. Instantiate Class and Login Using Email + UUID, storing the token returned
```python
from pyPhin import pHin
phin = pHin()
login_token = phin.login("test@example.com", uuid)
```
3. Verify Login with Code Recieved by Mail and store auth token
```python
authData = phin.verify("test@example.com", uuid, login_token,"123456")
```

```python
#Python Dictionary Returned from verify()
{
	"authToken": <authToken>, 
	"vesselUrl": <Url Route to Vessel>
}
```

4. Unpack authData Dictionary and Get Data using Authorization
```python
value = phin.getData(
	authData["authToken"],
	uuid,
	authData["vesselUrl"])
```
```python
#Sample value from getData()
{
	"waterData":
		{"TA":80,"CYA":60,"TH":450, "temperature": 80.2,
		"status":"balanced"}
}
```


## Implemented Data Types

```python
"TH" #Total Hardness (Nominal 150-399 ppm)
"CYA" #Cyanuric Acid (Nominal 20-99 ppm)
"TA" #Total Alkalinity (Nominal 80-150 ppm)

"temperature" #Temperature in Fahrenheit
"status" #Overall Status of Water
``` 
