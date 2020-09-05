# pyPhin

## Usage
1. Generate a UUID
```python
import uuid 
uuid = str(uuid.uuid4())
```
2. Instantiate Class and Login Using Email + UUID, storing the token returned
```python
from pyPhin import pHin
phin = pHin()
token = phin.login("test@example.com", uuid)
```
3. Verify Login with Code Recieved by Mail and store auth token
```python
auth = phin.verify("test@example.com", token, uuid, "123456")
```
4. Get Data using Authorization
```python
value = phin.getData(auth, "TH")
```

## Implemented Data Types

```python
"TH" #Total Hardness (Nominal 150-399 ppm)
"CYA" #Cyanuric Acid (Nominal 20-99 ppm)
"TA" #Total Alkalinity (Nominal 80-150 ppm)
``` 
