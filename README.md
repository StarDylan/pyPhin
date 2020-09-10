

# pyPhin

## Simple Usage
1. Generate a UUID
```python
import uuid
deviceUUID = str(uuid.uuid4())
```
2. Instantiate Class and Login Using Email + UUID, storing the token returned
```python
from pyPhin import pHin
phin = pHin()
login_token = phin.login("test@example.com", deviceUUID)
```
3. Verify Login with Code Recieved by Mail and store auth token
```python
authData = phin.verify("test@example.com", deviceUUID, login_token,"123456")
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
	deviceUUID,
	authData["vesselUrl"])
```
```python
#Sample value from getData()
{
  'pool': {
    'status_title': 'needs-attention',
    'status_id': 2
  },
  'waterData': {
    'ta': 80,
    'cya': 60,
    'th': 450,
    'temperature': 75.0,
    'ph': {
      'value': 7.2,
      'status': 3
    },
    'orp': {
      'value': 550.2,
      'status': 2
    }
  },
  'vesselData': {
    'battery': {
      'value': 3000.2,
      'percentage': 0.90
    },
    'rssi': {
      'value': -92,
      'status': 3
    }
  }
}
```


## Implemented Data Types

```python
pool:
"status_title" #String of Overall Status of Pool
"status_id" #Indexed status value (See Key Below)

waterData:
"th" #Total Hardness (Nominal 150-399 ppm)
"cya" #Cyanuric Acid (Nominal 20-99 ppm)
"ta" #Total Alkalinity (Nominal 80-150 ppm)
"temperature" #Temperature in Fahrenheit
"ph":
	"value" #Value of pH
	"status" #Status of pH (Integer 1-5)

"orp": #Oxidation-Reduction Potential (Sanitization)
	"value" #Value of ORP in mV
	"status" #Status of ORP (1,3 or 5)

vesselData:
"rssi" #Received Signal Strength Indicator
	"value" #Value of RSSI in dB
	"status" #Status of RSSI (1,3 or 5)
"battery":
	"value" #Value of battery in mV
	"percentage" #Percent of Battery Remaining (0.01-1.00)
```
Status of data in `waterData` and `vesselData`:
1 - Needs Immediate Attention (Low)
2 - Needs Attention (Low)
3 - Ok
4 - Needs Attention (High)
5 - Needs Immediate Attention (High)

`status_id` of `pool`:
1 - Balanced
2 - Needs Attention
3 - Needs Immediate Attention
