#!/usr/bin/python
import shutil
import re
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import os
import boto3

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
def put_file_s3(bucketName, fileName, key):
    s3 = boto3.resource('s3')
    s3.Object(bucketName, fileName).put(Body=open(fileName, 'rb'))

def put_message_sqs(queue, message):
    sqs = boto3.resource("sqs", region_name='us-west-2')
    queue = sqs.get_queue_by_name(QueueName=queue)
    response = queue.send_message(MessageBody=message)
    print(response.get('MessageId'))
    print(response.get('MD5OfMessageBody'))

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
        put_file_s3('web-module-files', name, name)
        put_message_sqs('web-module', name)
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


