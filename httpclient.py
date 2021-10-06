#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Xueying Luo
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def get_host_port(self,url):
        url_parsed = urllib.parse.urlparse(url)
        
        host = url_parsed.hostname
        port = url_parsed.port
        path = url_parsed.path

        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):

        self.code = int(data.splitlines()[0].split(' ')[1])
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        self.body = data.splitlines()[-1]
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):

        # parse url
        host, port, path = self.get_host_port(url)

        # connet & send request
        self.connect(host, port)
        data = "GET "+ path + " HTTP/1.1\r\n" + "Host: "+host+"\r\n" + "Connection: close\r\n" + "Accept: application/x-www-form-urlencoded\r\n\r\n"
        self.sendall(data)

        # receive response
        buffer = self.recvall(self.socket)
        print(buffer)
        self.close()

        # parse response
        self.get_code(buffer)
        self.get_body(buffer)

        return HTTPResponse(self.code, self.body)

    def POST(self, url, args=None):
        # parse url
        host, port, path = self.get_host_port(url)

        # connet & send request
        self.connect(host, port)

        if args is not None:
            args_format = ""
            for key in args:
                args_format += key + "=" + args[key] + "&"
            args_format = args_format[0:-1]

            data = ( "POST "+ path + " HTTP/1.1\r\n" + "Host: "+host+"\r\n" + "Connection: close\r\n" + 
                "Content-type: application/x-www-form-urlencoded\r\n"+ "Content-length: "+ str(len(args_format)) +"\r\n\r\n" + args_format)
        else:
            data = ( "POST "+ path + " HTTP/1.1\r\n" + "Host: "+host+"\r\n" + "Connection: close\r\n" + 
                "Content-type: application/x-www-form-urlencoded\r\n"+ "Content-length: 0\r\n\r\n")

        
        self.sendall(data)

        # receive response
        buffer = self.recvall(self.socket)
        print(buffer)

        # parse response, get status code & body
        self.get_code(buffer)
        self.get_body(buffer)

        self.close()


        return HTTPResponse(self.code, self.body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
