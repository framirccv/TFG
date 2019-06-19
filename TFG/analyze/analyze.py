#!/usr/bin/python3

import sys
import threading as th
from queue import Queue
from urllib.parse import unquote

from utils import *
from data import location, domain, body

STATIC_DIR = "static/"
API_CONFIG = STATIC_DIR + "api.conf"
CATEGORY_F = STATIC_DIR + "categories"
PHONE_INFO = STATIC_DIR + "info.device"
OWNER_DATA = STATIC_DIR + "domain_owners.json"

queue = Queue(15)
print_lock = th.Lock()

def run(T, dataf, fasen):
    owner = parse_json(OWNER_DATA)

    prod = th.Thread(target=producer, args=(dataf,))
    prod.daemon = True
    prod.start()

    for _ in range(T):
        cons = th.Thread(target=consumer, args=(owner, fasen))
        cons.daemon = True
        cons.start()
    prod.join()
    queue.join()

def producer(dataf):
    for req in parse_pickle(dataf):
        queue.put(req)

def consumer(owner, fasen):
    while True:
        req = queue.get()
        analyze_request(req, owner, fasen)
        queue.task_done()

def analyze_request(req, owner, fasen):
    result = {}
    print("EL REQ [0] ES " + str(req[0]))
    if req[0]:
        content = ""
        try:
            content = req[2].content.decode("utf-8")
            req[2].path = unquote(req[2].path)
            content = unquote(content)
            print(content)
            print(req)
        except:
            pass
        result["data"] = body(content, PHONE_INFO, CATEGORY_F) + body(req[2].path, PHONE_INFO, CATEGORY_F)

        if len(result["data"]) > 0:
            result["fase"]      = fasen
            result["https"]     = req[2].url[:5] == "https"
            result["location"]  = req[2] #location(req[2].host, API_CONFIG)
            result["domain"]    = req[1] #domain(req[1], owner)
            result["port"]      = str(req[2].port)
            #print(result)
            #with print_lock:
             #   print_csv(result)
    else:
        dom, port = "", "-"
        if isinstance(req[1], tuple):
            dom = req[1][0]
            port = req[1][1]
        else:
            dom = req[1]
        result["fase"]      = fasen
        result["https"]     = True
        result["location"]  = req[2] #location(dom, API_CONFIG)
        result["domain"]    = req[1] #domain(dom, owner)
        result["port"]      = str(port)
        result["data"]      = [("Certificate Pinning", "-")]
        print(req)
        #with print_lock:
            #print_csv(result)

if __name__ == "__main__":
    dataf = sys.argv[1]
    fasen = sys.argv[2]
    with print_lock:
        print_head()
    run(10, dataf, fasen)
