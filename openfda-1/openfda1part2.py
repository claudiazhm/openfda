import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET", "/drug/label.json?limit=10", None, headers)
r1 = conn.getresponse()
print(r1.status, r1.reason)
repos_raw = r1.read().decode("utf-8")
conn.close()

repos = json.loads(repos_raw)

# We create a counter that will enumerate the drugs
# We check for every element in the file the id, and we print it
position = 1
for elem in repos["results"]:
        print("The id of the drug", position , "is", elem["id"])
        position += 1