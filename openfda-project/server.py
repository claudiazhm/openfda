

import http.server
import json
import socketserver

socketserver.TCPServer.allow_reuse_address = True

IP = "localhost"
PORT = 8000

OPENFDA_BASIC = False

# We are going to use classes. The class is a fundamental building block used in Python, works as a library of objects.

#The first class is OpenFDAClient, which will include the logic to communicate with the OpenFDA remote API.
class OpenFDAClient():
    # We define a function called send_query which will send what we are looking for to the openFDA:
    def send_query(self, query):
        # We request an information ("query") to the openfda API, it will return the result of the query in JSON format.
        headers = {'User-Agent': 'http-client'}
        conn = http.client.HTTPSConnection("api.fda.gov")
        # Get a  drug label from the URL and extract the id, the purpose of the drug and the manufacturer_name.
        query_url = "/drug/label.json"
        if query:
            query_url += "?" + query
        print("Sending to OpenFDA the query", query_url)

        conn.request("GET", query_url, None, headers)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        res_raw = r1.read().decode("utf-8")
        conn.close()

        result = json.loads(res_raw)
        if 'results' in result:
            items = result['results']
        else:
            items = []
        return items

    def searchDrug(self, active_ingredient, limit=10):
        # We request the drugs so the client looks up for it
        query = 'search=active_ingredient:"%s"' % active_ingredient
        if limit:
            query += "&limit=" + str(limit)
        drugs = self.send_query(query)
        return drugs

    def listDrug(self, limit=10):
        query = "limit=" + str(limit)
        drugs = self.send_query(query)
        return drugs

    def searchCompany(self, company_name, limit=10):
        # We request the company name so the client looks up for it
        query = 'search=openfda.manufacturer_name:"%s"' % company_name
        if limit:
            query += "&limit=" + str(limit)
        drugs = self.send_query(query)
        return drugs

# Second class: OpenFDAParser: includes the logic to extract the data from drugs items
class parser_openfda():

    def parse_companies(self, drugs):
        # We create an empty list of the companies
        companies = []
        for drug in drugs:
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                companies.append(drug['openfda']['manufacturer_name'][0])
            else:
                companies.append("Unknown")
            companies.append(drug['id'])
        return companies

    def parse_drugs(self, drugs):
        # We create an empty list of the labels of the drugs:
        drugs_labels = []

        for drug in drugs:
            label = drug['id']
            if 'active_ingredient' in drug:
                label += " " + drug['active_ingredient'][0]
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                label += " " + drug['openfda']['manufacturer_name'][0]
            drugs_labels.append(label)
        return drugs_labels

    def parse_warnings(self, drugs):
        # We extract a warnings list:
        warnings = []
        for drug in drugs:
            if 'warnings' in drug and drug['warnings']:
                warnings.append(drug['warnings'][0])
            else:
                warnings.append("None")
        return warnings

# Third class: OpenFDAHTML: includes the logic to the HTML visualization
class OpenFDAHTML():

    def build_html_list(self, items):
        html_list = "<ul>"
        for item in items:
            html_list += "<li>" + item + "</li>"
        html_list += "</ul>"
        return html_list

    # If anything isn't found, we should receive an error, so we use a specific html file: not_found.html
    def get_not_found_page(self):
        with open("not_found.html") as html_file:
            html = html_file.read()
        return html

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        path = self.path

        client = OpenFDAClient()
        visualization = OpenFDAHTML()
        parser = parser_openfda()

        http_response_code = 200
        http_response = "<h1>Not supported</h1>"

        if path == "/":
            # Return the HTML form for searching
            with open("html_openfda.html") as file_form:
                form = file_form.read()
                http_response = form
        elif 'searchDrug' in path:
            active_ingredient = None
            limit = 10
            params = path.split("?")[1].split("&")
            for param in params:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                if param_name == 'active_ingredient':
                    active_ingredient = param_value
                elif param_name == 'limit':
                    limit = param_value
            items = client.searchDrug(active_ingredient, limit)
            http_response = visualization.build_html_list(parser.parse_drugs(items))
        elif 'listDrugs' in path:
            limit = None
            if len(path.split("?")) > 1:
                limit = path.split("?")[1].split("=")[1]
            items = client.listDrug(limit)
            http_response = visualization.build_html_list(parser.parse_drugs(items))
        elif 'searchCompany' in path:
            company_name = None
            limit = 10
            params = path.split("?")[1].split("&")
            for param in params:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                if param_name == 'company':
                    company_name = param_value
                elif param_name == 'limit':
                    limit = param_value
            items = client.searchCompany(company_name, limit)
            http_response = visualization.build_html_list(parser.parse_companies(items))
        elif 'listCompanies' in path:
            limit = None
            if len(path.split("?")) > 1:
                limit = path.split("?")[1].split("=")[1]
            items = client.listDrug(limit)
            http_response = visualization.build_html_list(parser.parse_companies(items))
        elif 'listWarnings' in path:
            limit = None
            if len(path.split("?")) > 1:
                limit = path.split("?")[1].split("=")[1]
            items = client.listDrug(limit)
            http_response = visualization.build_html_list(parser.parse_warnings(items))
        else:
            http_response_code = 404
            if not OPENFDA_BASIC:
                url_found = False
                http_response = visualization.get_not_found_page()

        self.send_response(http_response_code)

        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(bytes(http_response, "utf8"))
        return

Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()