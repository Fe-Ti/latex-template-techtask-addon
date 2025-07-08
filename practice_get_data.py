# Copyright 2023-2025 Fe-Ti aka T.Kravchenko

import sys
import time

print("Welcome :)\nDescr.: Скрипт для получения данных из задачи Redmine и формирования tex команд\nВерсия: v1\nCodename: Oh, sysempai\n\n")

if len(sys.argv) < 2:
    print("""Мне нужно два аргумента --- сначала URL задачи, а затем ключ API. Например:
    
    python3 practice_get_data.py https://дело.бмсту.ру/issues/12345 123456fda12345adf90fada56fad0dfa4adf8900
""")
    exit(1)
if len(sys.argv) < 3:
    print("""Мне нужен второй аргумент --- твой ключ API. Например:
    
    python3 practice_get_data.py https://дело.бмсту.ру/issues/12345 123456fda12345adf90fada56fad0dfa4adf8900
""")
    exit(1)

myURL = sys.argv[1]
myKey = sys.argv[2]

# HTTP request library (cut down part of Redmine-Bot-Library request sublibrary)
import urllib.request as u_request # TODO: make async http

from typing import Union
from pathlib import Path

def make_url(
                scheme : str,
                server_root : Path,
                resource_path,
                parameters : dict | str,
                api_format='.json'
            ):
    """!
    This function assembles a URL from given parameters.
    """
    # Let's check types
    # ~ if type(server_root) is Path:
        # ~ raise TypeError("Server root should be a Path object like 'host/path/to/redmine'")
    if type(parameters) is dict:
        # if parameters are present as dict, then make a string out of them
        parameters_string = ""
        for k in parameters.keys():
            parameters_string += f"{k}={parameters[k]}&"
        parameters_string = parameters_string[:-1]
    elif type(parameters) is str:
        parameters_string = parameters
    else:
        raise TypeError("Parameters should be either in dict or URL parameters string form")
    print( f"{scheme}://{server_root / resource_path}{api_format}?{parameters_string}")
    return f"{scheme}://{server_root / resource_path}{api_format}?{parameters_string}"

# HTTP Requests -- all of them return response string

def  _sync_get_response(req, encoding):
    try:
        with u_request.urlopen(req) as f:
            return {"data":f.read().decode(encoding), "code":f.code}
    except u_request.HTTPError as error:
        with error as f:
            return {"data":f.read().decode(encoding), "code":f.code}

def GET(url : str, encoding : str ='utf-8'):
    """!
    GET is used for getting info. Returns string.
    """
    req = u_request.Request(url=url, data=None, method="GET")
    return _sync_get_response(req, encoding)


# Now goes One Script for getting all of 'em

reqURL=f"{myURL}.json?key={myKey}"
print(f"Получаю данные из {reqURL}...")
resp = GET(reqURL)
code_OK = 200
time.sleep(1) # imitate hard work even if response is fast
if resp["code"] == code_OK:
    print("[ Успех XD  ]")
else:
    print("[ Ошибка :D ]")
    exit(1)



