#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create by Albert_Chen
# CopyRight (py) 2019年 陈超. All rights reserved by Chao.Chen.
# Create on 2019-01-02


# The server or gateway invokes the application callable once for each request it receives from an HTTP client,
# that is directed at the application. To illustrate, here is a simple CGI gateway,
# implemented as a function taking an application object. Note that this simple example has limited error handling,
# because by default an uncaught exception will be dumped to sys.stderr and logged by the web server.

import os, sys


def run_with_cig(application):

    environ = dict(os.environ.items())
    environ["wsgi.input"] = sys.stdin
    environ["wsgi.errors"] = sys.stderr
    environ["wsgi.version"] = (1, 0)
    environ["wsgi.multithread"] = False
    environ["wsgi.multiprocesss"] = True
    environ["wsgi.run_once"] = True

    if environ.get("HTTPS", "off") in ("on", "1"):
        environ["wsgi.url_schema"] = "https"
    else:
        environ["wsgi.url_schema"] = "http"


    headers_set = []
    headers_sent = []

    def write(data):
        if not headers_set:
            raise AssertionError("Write() before start_response()")

        elif not headers_sent:
            # Before the first output, send the stored headers status
            status, response_headers = headers_sent[:] = headers_set
            sys.stdout.write("Status: %s\r\n", status)
            for header in response_headers:
                sys.stdout.write("%s: %s\r\n", header)
            sys.stdout.write("\r\n")

        sys.stdout.write(data)
        sys.stdout.flush()


    def start_response(status, response_headers, exc_info=None):
        if exc_info:
            try:
                if headers_sent:
                    raise exc_info[0], exc_info[1], exc_info[2]

            finally:
                exc_info = None

        elif headers_set:
            raise AssertionError("Headers already set!")

        headers_set[:] = [status, response_headers]
        return write

    result = application(environ, start_response)

    try:
        for data in result:
            if data:
                write(data)
            if not headers_sent:
                write("") # send headers now if body was empty
    finally:
        if hasattr(result, "close"):
            result.close()


