#!/usr/bin/python
import shutil
import re
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import os

PORT_NUMBER = 8080
form_header_length = 141


def get_name(fileName):
    f = open(fileName, "r")
    lines = f.readlines()
    name = re.search('filename="(.+)"',lines[1]).group(1)
    f.close()
    return name

def remove_pd_hed(fileName):
    f = open(fileName, "r")
    lines = f.readlines()
    f.close()
    del lines[:4]
    del lines[-2:]
    f = open(fileName,"w")
    for var in lines:
        f.write(var)
    f.close()

class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/index":
            self.path="/index.html"
                try:
                    sendReply = False
                    if self.path.endswith(".html"):
                        mimetype='text/html'
                        sendReply = True
                    if sendReply == True:
                        #Open the static file requested and send it
                        f = open(curdir + sep + self.path)
                        self.send_response(200)
                        self.send_header('Content-type', mimetype)
                        self.end_headers()
                        self.wfile.write(f.read())
                        f.close()
                        return
                except IOError:
                    self.send_error(404,'File Not Found: %s' % self.path)
    def do_POST(self):
        # print self.path
        length = int(self.headers['content-length'])
        content = self.rfile.read(length)
        fo = open("temp.txt", "w")
        fo.write(content)
        fo.close()
        name = get_name("temp.txt")
        remove_pd_hed("temp.txt")
        shutil.copy("temp.txt", name)
        os.remove("temp.txt")

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ' , PORT_NUMBER

    #Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()


