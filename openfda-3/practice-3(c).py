
import http.server
import socketserver
import http.client
import json

PORT = 8029
MAX_OPEN_REQUESTS = 5

def process_client(clientsocket):

    headers = {'User-Agent': 'http-client'}

    conn = http.client.HTTPSConnection("api.fda.gov")
    conn.request("GET", "/drug/label.json?limit=10", None, headers)
    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    repos_raw = r1.read().decode("utf-8")
    conn.close()

    repos = json.loads(repos_raw)

    #We create an empty list, called drug_list, and we will later add elements to the list:
    drug_list = []
    #We create a counter, and we will use it to add the elements to our drug_list:
    counter = 0
    #We create a head list so it prints the title and enumerates the list of drugs:
    head_list = "<head>" + "THIS IS THE LIST OF THE DRUGS' ID" + "</head>" "<ol>" + "\n"

    while counter < 10:
        if 'active_ingredient' in repos['results'][counter]:
            counter += 1
            drug_list.append(repos['results'][counter]['id'])
        else:
            counter += 1
            drug_list.append("This index does't correspond to any drug")

    with open("htmlfile.html", "w") as f:
        f.write(head_list)
        for element in drug_list:
            elementslist = "<t>" + "<li>" + element
            f.write(elementslist)

    with open("drugs.html", "r") as f:
        drugfile = f.read()

    web_contents = drugfile
    web_headers = "HTTP/1.1 200"
    web_headers += "\n" + "Content-Type: text/html"
    web_headers += "\n" + "Content-Length: %i" % len(str.encode(web_contents))
    clientsocket.send(str.encode(web_headers + "\n\n" + web_contents))
    clientsocket.close()

    print(clientsocket)
    print(clientsocket.recv(1024))

# Create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
hostname = socket.gethostname()
# Let's use better the local interface name
hostname = "localhost"
try:
    serversocket.bind((hostname, PORT))
    # become a server socket
    # MAX_OPEN_REQUESTS connect requests before refusing outside connections
    serversocket.listen(MAX_OPEN_REQUESTS)

    while True:
        # accept connections from outside
        print("Waiting for connections at %s %i" % (hostname, PORT))
        (clientsocket, address) = serversocket.accept()
        # now do something with the clientsocket
        # in this case, we'll pretend this is a non threaded server
        process_client(clientsocket)
except socket.error:
    print("Problemas using port %i. Do you have permission?" % PORT)