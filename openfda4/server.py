import http.server
import socketserver

PORT = 8010

socketserver.TCPServer.allow_reuse_address = True

# HTTPRequestHandler class
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # (new)
        with open("search.html") as file_search:
            message = file_search.read()

        #(WRITE CONTENT AS UTF-8 DATA)
        self.wfile.write(bytes(message, "utf8"))
        return


Handler = http.server.SimpleHTTPRequestHandler
Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()