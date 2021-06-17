import sys
from functools import wraps
import traceback
import json
from django.http import QueryDict
from json.decoder import JSONDecodeError
from io import BytesIO
from django.http.request import HttpRequest
from django.http.request import QueryDict
from django.core.handlers.wsgi import WSGIRequest


def handle(template=None, error_occurred_move=None):
    def decorator(f):
        @wraps(f)
        def wrapper(arg, *args, **kwargs):
            try:
                if template:
                    if type(arg) == WSGIRequest:
                        request = arg
                    else:
                        request = args[0]
                    request.DATA = parse(request.DATA, template)
                return f(arg, *args, **kwargs)
            except Exception as e:
                exc_type, exc_instance, exc_traceback = sys.exc_info()
                formatted_traceback = ''.join(traceback.format_tb(exc_traceback))
                message = str('\n{0}\n{1}:\n{2}\n{3}'.format(
                    e,
                    formatted_traceback,
                    exc_type.__name__,
                    exc_instance
                ))
                print(message)
                return error_occurred_move
        return wrapper
    return decorator


http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

default = {
    str: '',
    int: 0,
    float: 0.0,
    list: [],
    dict: {},
    bool: False,
}

type_allowed = default.keys()


def corr(data, template):
    msg = 'correspond success'
    for key in data.keys():
        if key not in template:
            msg = f"data don't has key:[{key}]"
            return False, msg
        elif type(data[key]) == dict:
            correspond, msg = corr(data[key], template[key])
            if not correspond:
                return False, msg
        elif type(data[key]) == list:
            pass
        elif type(data[key]) != template[key]:
            msg = f"data's key:[{key}] with type:({type(data[key])}) don't match the type:({template[key]})"
            return False, msg
    return True, msg


def check(request, template):
    data_dict = QueryDict(request.body)
    if type(template) != dict:
        raise TypeError(f"Template with error type:[{type(template)}] (must be a [dict])")
    for key in template.keys():
        temp = template[key]
        if key not in http_method_names or key.lower() not in http_method_names:
            raise KeyError(f"Template key:[{key}] does not in http method name")
        if type(temp) != dict:
            raise TypeError(f"SubTemplate with error type:[{type(temp)}] (must be a [dict])")
        if request.method == key.upper():
            correspond, msg = corr(data_dict, temp)
            if not correspond:
                raise AttributeError("Template match error:"+msg)
    return True


def type_check(temp):
    if temp in default:
        return default[temp]
    else:
        raise TypeError(f"Template type error: type[{temp}] not allowed")


def copy(temp):
    if type(temp) == type:
        return type_check(temp)

    elif type(temp) == dict:
        for key in temp.keys():
            return copy(temp[key])

    elif type(temp) == list:
        return copy(temp[0])


def parse(data_raw, template, strict=True, depth=0):
    if type(template) != dict:
        raise TypeError(f"Template with error type:[{type(template)}] (must be a [dict])")
    json_type = type(data_raw) == dict
    data_dict = dict(data_raw)
    data_parse = {}
    for key in template.keys():
        data_key = None
        temp = template[key]
        if type(temp) == type and temp not in type_allowed:
            raise TypeError(f"Template type error: type[{temp}] not allowed")
            # api template contains a type that don't allowed
        if key not in data_dict:
            if strict:
                raise KeyError(f"Template key:[{key}] does not in request data's keys")
            else:
                data_parse[key] = copy(temp)
                continue

        if json_type or depth: # QueryDict set multipart only work for layer 0
            data_key = type_transform(data_dict[key], temp)
        elif type(temp) == type and temp != list or type(temp) != list:
            data_key = type_transform(data_dict[key][0], temp)

        if type(temp) != type:
            if type(temp) == list:
                data_list = []
                if type(temp[0]) == type:
                    for d in data_dict[key]:
                        if d != '':
                            data_list.append(type_transform(d, temp[0]))
                    data_key = data_list
                elif type(temp[0]) == dict:
                    for d in data_dict[key]:
                        d = json.loads(d)
                        data_list.append(parse(d, temp[0], strict, depth+1))
                    data_key = data_list
                else:
                    raise TypeError(f"Template key:[{key}] list does not allow for type[{type(temp[0])}]")
            elif type(temp) == dict:
                data_key = parse(data_dict[key], temp, strict, depth+1)
            else:
                raise TypeError(f"Template key:[{key}] does not allow for type[{type(temp)}]")

        data_parse[key] = data_key
    return data_parse


def type_transform(data, t):
    if type(data) != t:
        try:
            if t == dict:
                return json.loads(data)
            elif t == list:
                if type(data) == str and data[0] == '[' and data[-1] == ']':
                    return data[1:-1].split(',')
                return [data] if data else []
            elif t == bool:
                false_list = ['', '0', 0, 'false', 'False', 'null']
                if data in false_list:
                    return False
                return True
            return t(data)
        except:
            raise TypeError(f"Data don't have the correct type[{t}]")
    return data



