#!/usr/bin/python3

import json
import pickle

###########################################################################################################################
#                                                                                                                         #
#                                       Parse                                                                             #
#                                                                                                                         #
###########################################################################################################################

# Read a pickled data file line by line
def parse_pickle(dataf):
    with open(dataf, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break

# Read the json data 
def parse_json(f):
    with open(f, "r") as do:
        return json.load(do)

# Read colon separated data
def parse_data(f):
    with open(f, "r") as di:
        return {x[0]: x[1].split(";") for x in (s.strip().split(": ") for s in di.readlines())}

###########################################################################################################################
#                                                                                                                         #
#                                       Print                                                                             #
#                                                                                                                         #
###########################################################################################################################

# Print dictionary in JSON format
def print_json(dic):
    print(dic)
    print()

def print_head():
    sol = ["Fase", "Dato exfiltado", "Categoria", "Dominio", "Puerto", "Cat Dominio", "País", "Transferencia Internacional", "Https"]
    print(",".join(sol))

# Print dict in csv format
def print_csv(dic):
    sol = [None] * 9
    sol[0], sol[8] = dic["fase"], dic["https"]
    sol[3], sol[4] = dic["domain"]["subdomain"], dic["port"]
    sol[6] = dic["location"]["country"]
    if sol[6] is not None:
        sol[7] =  not dic["location"]["is_eu"] and dic["location"]["country"] not in ("Norway", "Ireland", "Lietchestein")
    for d in dic["data"]:
        sol[1], sol[2] = d[0], d[1]
        sol = ["Si" if x is True else x for x in sol]
        sol = ["No" if x is False else x for x in sol]
        sol = ["-" if x is None else x for x in sol]
        print(",".join(sol))
