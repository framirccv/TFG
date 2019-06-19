#!/usr/bin/python3

import requests
from threading import Lock

from utils import parse_data

###########################################################################################################################
#                                                                                                                         #
#                                       Location                                                                          #
#                                                                                                                         #
###########################################################################################################################

# Find location of IP from remote API.

def loc_mem(mem, lock):
    def loc(ip, api_conf):
        if ip not in mem:
            with lock:
                # This check is necesary to check posible memoization of the thread that held the lock
                if ip not in mem: 
                    params = parse_data(api_conf)
                    loc = requests.get("http://api.ipstack.com/{}".format(ip), params=params).json()
                    mem[ip] = {"country": loc["country_name"], "is_eu": loc["location"]["is_eu"]}
        return mem[ip]
    return loc
location = loc_mem({}, Lock())

###########################################################################################################################
#                                                                                                                         #
#                                       Domain                                                                            #
#                                                                                                                         #
###########################################################################################################################

# Analize a subdomain based on the information
# given by the owners list.
def domain(subdom, owners):
    dom = get_domain(subdom)
    anc = ancestry(dom, owners)
    result = {"found": len(anc) > 0, "domain": dom, "subdomain": subdom}
    if len(anc) > 0:
        result["ancestry"] = anc
    return result

# Get a list of all the names of
# the ancestry of a domain.
def ancestry(dom, owners):
    anc = []
    ids = ancestry_ids(dom, owners)
    for i in ids:
        anc.append(owners[i]["owner_name"])
    return anc

# Get a list of all the ids
# of the ancestry of a domain.
def ancestry_ids(dom, owners):
    family = []
    did = domain_id(dom, owners)
    while did:
        family.append(did)
        did = owners[did]["parent_id"]
    return family

# Get the domain from a subdomain string.
def get_domain(subdom):
    subdom = subdom.split(".")
    return "{}.{}".format(subdom[-2], subdom[-1])

# If domain is in owners data return its id
# or else return None.
def domain_id(dom, owners):
    for o in owners:
        if dom in o["domains"]:
            return o["id"]
    return None

###########################################################################################################################
#                                                                                                                         #
#                                       Body                                                                              #
#                                                                                                                         #
###########################################################################################################################

def body(data, info_file, cat_file):
    res = category(data, info_file)
    cat = [category(r, cat_file)[0] for r in res]
    return list(zip(res,cat))

def category(data, data_file):
    res  = []
    cat  = parse_data(data_file)
    for k in cat:
        tmp = [k for e in cat[k] if e in data]
        res.extend(tmp)
    return res
