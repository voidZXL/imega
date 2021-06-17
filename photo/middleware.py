import json
from json.decoder import JSONDecodeError
from django.http import QueryDict
from django.http import HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin
import time
from django.conf import settings
from django.utils.log import log_response
from django.http import HttpResponse

def is_float(s):
    s = str(s)
    if s.count('.') == 1:  # 判断小数点个数
        sl = s.split('.')  # 按照小数点进行分割
        left = sl[0]  # 小数点前面的
        right = sl[1]  # 小数点后面的
        if left.startswith('-') and left.count('-') == 1 and right.isdigit():
            lleft = left.split('-')[1]  # 按照-分割，然后取负号后面的数字
            if lleft.isdigit():
                return True
        elif left.isdigit() and right.isdigit():
            # 判断是否为正小数
            return True
    return False


"""
+---------------+-------------------+
| JSON | Python |
+= == == == == == == == += == == == +
| object | dict |
+---------------+-------------------+
| array | list |
+---------------+-------------------+
| string | str |
+---------------+-------------------+
| number(int) | int |
+---------------+-------------------+
| number(real) | float |
+---------------+-------------------+
| true | True |
+---------------+-------------------+
| false | False |
+---------------+-------------------+
| null | None |
+---------------+-------------------+
"""


def type_decode(data):
    if type(data) == str:
        if data.isdigit() or (data.split('-')[-1]).isdigit():
            return int(data)
        elif is_float(data):
            return float(data)
        elif data == "true":
            return True
        elif data == "false":
            return False
        elif data == "null":
            return None
        else:
            try:
                d = json.loads(data)
                # print(d)
                return d
            except JSONDecodeError:
                return data
    else:
        return data


def dict_parser(data):
    data = dict(data)
    for key in data.keys():
        try:
            if type(data[key]) == list:
                if len(data[key]) == 1:
                    data[key] = type_decode(data[key][0])
                else:
                    data_list = []
                    for d in data[key]:
                        data_list.append(type_decode(d))
                    data[key] = data_list
            else:
                data[key] = type_decode(data[key])

        except (ValueError, TypeError) as e:
            pass
    return data

class DataParsingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.content_type != "application/json":
            if request.method == "PUT" or request.method == "DELETE":
                if hasattr(request, '_post'):
                    del request._post
                    del request._files
                try:
                    m = request.method
                    request.method = "POST"
                    request._load_post_and_files()
                    request.method = m
                except AttributeError as e:
                    request.META['REQUEST_METHOD'] = 'POST'
                    request._load_post_and_files()
                    request.META['REQUEST_METHOD'] = request.method

            if request.method == 'GET':
                request.DATA = request.GET
            else:
                request.DATA = request.POST# dict_parser(request.POST)
            # request.DATA_TYPE = 'multipart'
        else:
            # request.DATA_TYPE = 'json'
            try:
                request.DATA = json.loads(request.body)
            except ValueError as ve:
                return HttpResponseBadRequest("unable to parse JSON data. Error : {0}".format(ve))

class RESTParsingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (request.method == "PUT" or request.method == "DELETE") and request.content_type != "application/json":
            if hasattr(request, '_post'):
                del request._post
                del request._files
            try:
                m = request.method
                request.method = "POST"
                request._load_post_and_files()
                request.method = m
            except AttributeError as e:
                request.META['REQUEST_METHOD'] = 'POST'
                request._load_post_and_files()
                request.META['REQUEST_METHOD'] = request.method

            exec(f"request.{request.method} = request.POST")


class JSONParsingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (request.method == "PUT" or request.method == "POST" or request.method == "DELETE") \
                and request.content_type == "application/json":
            try:
                request.JSON = json.loads(request.body)
            except ValueError as ve:
                return HttpResponseBadRequest("unable to parse JSON data. Error : {0}".format(ve))


class LogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        start = int(round(time.time() * 1000))
        path = request.get_full_path()
        address = request.META.get("HTTP_X_FORWARDED_FOR", "") or request.META.get('REMOTE_ADDR', "")
        now = time.strftime('%Y.%m.%d %H:%M:%S ', time.localtime(time.time()))
        method = request.method
        # _______________________________
        response = self.get_response(request)
        # -------------------------------
        end = int(round(time.time() * 1000))
        dual = end - start
        # if hasattr(response, 'content'):
        #     size = len(response.content)
        # elif hasattr(response, 'streaming_content'):
        #     size = response['Content-Length']
        #     # length = 0  # len(list(response.streaming_content))*4096
        # else:
        #     size = 0
        size = response['Content-Length'] or 0
        status = response.status_code
        log = f"[{now}] {method} {path} from [{address}] -- response[{status}] with [{size}] Bytes in [{dual}]ms\n"
        if hasattr(settings, 'LOG'):
            if settings.LOG['type'] == 'file':
                d = settings.LOG['dir']
                with open(d, 'a') as f:
                    f.write(log)
            elif settings.LOG['type'] == 'db':
                print(log)
        else:
            print(log, "(LOG in settings.py not set!!)")
        return response

