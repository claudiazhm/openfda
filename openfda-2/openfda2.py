# The purpose of this practice is to find out the names of the manufacturer which produce aspirin
# From the API basics we know that to search we need to use: search=field:term
# For example: https://api.fda.gov/drug/event.json?search=patient.reaction.reactionmeddrapt:"fatigue"&limit=1

import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
# We modify the request, so it looks up for the active ingredient of the aspirin, which is acetylsalicylic acid:
conn.request("GET", "/drug/label.json?search=active_ingredient:acetylsalicylic&limit=4", None, headers)
r1 = conn.getresponse()
print(r1.status, r1.reason)
repos_raw = r1.read().decode("utf-8")
conn.close()

repos = json.loads(repos_raw)

# We print the names of the manufacturers repositories, and we look the name inside the lists:
print("The manufacturer repository which produce aspirin is", repos["results"][2]["openfda"]["manufacturer_name"])
print("The manufacturer repository which produce aspirin is", repos["results"][0]["openfda"]["manufacturer_name"])