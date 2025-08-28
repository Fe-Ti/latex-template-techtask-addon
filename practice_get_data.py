# Copyright 2023-2025 Fe-Ti aka T.Kravchenko

import sys
import time
import json

print("Welcome :)\nDescr.: Скрипт для получения данных из задачи Redmine и формирования tex команд\nВерсия: v1\nCodename: RedDust\n\n")

if len(sys.argv) < 4:
    print("""Мне нужено 3 аргумента --- сначала домен сервера, номер задачи, а затем твой ключ API. Например:
    
    python3 practice_get_data.py дело.бмсту.ру 12345 123456fda12345adf90fada56fad0dfa4adf8900
""")
    exit(1)

srvdomain = sys.argv[1]
issuenum = sys.argv[2]
myKey = sys.argv[3]

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
    # ~ print( f"{scheme}://{server_root / resource_path}{api_format}?{parameters_string}")
    return f"{scheme}://{server_root / resource_path}{api_format}?{parameters_string}"

def make_json_url(srvdomain, resource, apikey):
    return make_url("https", Path(srvdomain), resource,{"key":apikey})

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

# ~ reqURLfmt="{myURL}.json?key={myKey}"
reqURL = make_url("https", Path(srvdomain), f"issues/{issuenum}",{"key":myKey})

print(f"Получаю данные из {reqURL}...")
resp = GET(reqURL)
code_OK = 200
time.sleep(1) # imitate hard work even if response is fast
if resp["code"] == code_OK:
    print("[ Успех XD  ]")
else:
    print("[ Ошибка :D ]")
    exit(1)

ID = 'id'
VALUE = 'value'
issue_datadict = json.loads(resp["data"])["issue"]
custom_fields = issue_datadict["custom_fields"] # custom fields is place where all the juice is :)

# ~ print(json.dumps(issue_datadict, indent=4, ensure_ascii=False))

cfields_by_name = dict()

for field in custom_fields:
    fid = field["id"]
    fname = field["name"]
    fval = field["value"]
    cfields_by_name[fname] = fval
    # uncomment below to get keywords
    #print(f"\"{fname}\"")

# Print if needed
# ~ print(json.dumps(cfields_by_name, indent=4, ensure_ascii=False))

kwd_student = "Студент-исполнитель"
kwd_mgtu_sup = "Руководитель от МГТУ"
kwd_comp_sup = "Руководитель от Предприятия"
kwd_group = "Группа"
kwd_profile = "Номер личного дела"
kwd_kind = "Вид практики"
kwd_type = "Тип практики"
kwd_length = "Длительность практики"
kwd_start = "Дата начала практики"
kwd_due = "Дата окончания практики"
kwd_base = "База практики"
kwd_task = "Задание на практику"

kwd_quality = "Должность"

student = cfields_by_name[kwd_student] # student id
mgtu_sup = cfields_by_name[kwd_mgtu_sup] # supervisor id
comp_sup = cfields_by_name[kwd_comp_sup]
group = cfields_by_name[kwd_group] # group with year like dep-num-year
profile = cfields_by_name[kwd_profile]
kind = cfields_by_name[kwd_kind]
ptype = cfields_by_name[kwd_type]
length = cfields_by_name[kwd_length]
date_start = cfields_by_name[kwd_start] # 2025-12-20
date_due = cfields_by_name[kwd_due]
base = cfields_by_name[kwd_base]
task = cfields_by_name[kwd_task]

# Get full names of guys involved
def get_dict_json(url):
    print(f"Получаю данные из {url}...")
    resp = GET(url)
    code_OK = 200
    if resp["code"] == code_OK:
        print("[ Успех XD  ]")
    else:
        print("[ Ошибка :D ]")
        exit(1)
    time.sleep(0.3) # imitate hard work even if response is fast
    return json.loads(resp["data"])

def get_username(userdict):
    return userdict["user"]["lastname"] + " " + userdict["user"]["firstname"]

def get_userquality(userdict):
    for field in userdict["user"]["custom_fields"]  :
        fid = field["id"]
        fname = field["name"]
        fval = field["value"]
        if fname == kwd_quality:
            return fval
    print(f"No custom fields in user {userdict['user']['id']} profile.")
    exit(1)

student_fullname = get_username(get_dict_json(make_json_url(srvdomain, f"users/{student}", myKey)))
# ~ student = sum([f"{i[0]}. " for i in student_fullname.split()[1:]])+f" {student_fullname.split()[0]}"
print(f"{student_fullname} проходит {kind.upper().split()[0][:-2]}УЮ практику в {base}.")

mgtu_sup = get_dict_json(make_json_url(srvdomain, f"users/{mgtu_sup}", myKey))
# ~ print(json.dumps(mgtu_sup, indent=4, ensure_ascii=False))
mgtu_sup = get_userquality(mgtu_sup) + " " + get_username(mgtu_sup)
print(f"Руководителем от МГТУ является {mgtu_sup}.")

comp_sup = comp_sup
print(f"Руководителем от Предприятия является {comp_sup}.")

# Format dates
date_start = "{}.{}.{}".format(*(date_start.split('-')[::-1]))
date_due = "{}.{}.{}".format(*(date_due.split('-')[::-1]))
print(f"Практика начинается {date_start} и заканчивается {date_due}.")

# ~ print(task.replace('•', '').split('\n'))
tasklist = ''
for i in task.replace('•', '').split('\n'):
    # ~ print(i)
    tasklist+=f"\\item {i}\n"

tasklist = "\\begin{itemize}\n" + tasklist + r"\end{itemize}"

# ~ print("Короче. Вот, что нужно вставить в преамбулу:")


preamble_part = fr"""
\overrideTitlePage

\practiceType{{{ptype}}}
\practiceKind{{{kind.upper().split()[0][:-2]}ОЙ}}
\practiceBase{{{base}}}

\studentFullName{{{student_fullname}}}
\group{{{group}}}

\profile{{{profile}}}
\supervisor{{{comp_sup}}}
\departmentSupervisor{{{mgtu_sup}}}
\datestart{{{date_start}}}
\datedue{{{date_due}}}

% Если в JSON API у СУК СРС добавят поля, специальности и специализации
%      то можно будет заполнять в автоматическом режиме 
\speciality{{\error Заполни меня из PDF, в системе delo параметра "Специальность / направление" нигде нет ;( }}
\specialization{{\error Заполни меня из PDF, в системе delo параметра "Специализация / профиль" нигде нет ;( }}

\practicetasks{{
{tasklist}
}}
"""
print(preamble_part)
