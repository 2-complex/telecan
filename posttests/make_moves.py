
import requests
import json
import random

URL = "http://localhost:5000"

r = requests.post(
    URL + "/new-move",
    data = {
        "round_id": 2,
        "user_id": 6,
        "content": "move: " + str(random.randrange(100,1000))
    })

print(r.json())
