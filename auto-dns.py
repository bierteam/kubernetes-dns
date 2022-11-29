#!/usr/bin/env python
import os
import re
import CloudFlare
import pycurl

timeout = int(os.environ.get("TIMEOUT"))
mainDomain = os.environ.get("MAIN_DOMAIN")
regexDomain = os.environ.get("REGEX_DOMAIN")
kubernetesDomain = os.environ.get("KUBERNETES_DOMAIN")
testDomain = os.environ.get("TEST_DOMAIN")

# This consumes ENV var CLOUDFLARE_API_TOKEN
# https://github.com/cloudflare/python-cloudflare
cf = CloudFlare.CloudFlare()

# Request all zones from cloudflare account
zones = cf.zones.get()

# Get the zoneId for our domain
for zone in zones:
    if zone['name'] == mainDomain:
        zoneId = zone['id']

# Get all records in zone
records = cf.zones.dns_records.get(zoneId)

nodes = [
    # debug
    # {"name": "test", "type": "AAAA", "ip": "2a02:a470:edcd:0:211:32ff:fe3a:9de5"}
]
kubernetesPool = {}
# find all regexDomain records
for record in records:
    if record['type'] == "A" or "AAAA":
        if re.search(regexDomain, record['name']):
            nodes.append({"name": record['name'], "type": record['type'], "ip": record['content']})
        if record['name'] == kubernetesDomain:
            kubernetesPool[record['content']] = {"name": record['name'], "id": record['id'], "type": record['type'], "plannedAction": "delete"}

# Try to connect to all nodes
healthyNodes = [
    # debug
    # {"name": "k8s-5.oscarr.nl", "type": "A", "ip": "1.1.1.1"},
    # {"name": "k8s-6.oscarr.nl", "type": "AAAA", "ip": "::1"}
]
for node in nodes:
    try: 
        curlConnector = pycurl.Curl()
        curlConnector.setopt(pycurl.CONNECTTIMEOUT, timeout)
        # suppress output to terminal
        curlConnector.setopt(pycurl.WRITEFUNCTION, lambda x: None)
        curlConnector.setopt(pycurl.URL, "https://"+testDomain)
        curlConnector.setopt(pycurl.RESOLVE, [testDomain+":443:" + node['ip']])
        curlConnector.perform()
        status = curlConnector.getinfo(pycurl.RESPONSE_CODE)
        if status == 200:
            print(f"Connection succeeded. Node: {node['name']} ip: {node['ip']} statuscode: {status}")
            healthyNodes.append({"name": node['name'], "type": node['type'], "ip": node['ip']})
        else:
            print(f"Status was not 200. Node: {node['name']} ip: {node['ip']} statuscode: {status}")
        curlConnector.close()
    except pycurl.error:
        print(f"Failed to connect.  Node: {node['name']} ip: {node['ip']}")
        curlConnector.close()
        continue

# find out if all healthy nodes are matched to a kubernetes pool record
for healthyNode in healthyNodes:
    if kubernetesPool.get(healthyNode['ip']):
        print(f"Node {healthyNode['name']} exists in kubernetes pool. Keeping record {healthyNode['ip']}")
        kubernetesPool[healthyNode['ip']]['plannedAction'] = 'keep'
    else:
        print(f"Node {healthyNode['name']} does not exists in kubernetes pool. Creating record {healthyNode['ip']}")
        kubernetesPool[healthyNode['ip']] = {"name": kubernetesDomain, "ip": healthyNode['ip'], "type": healthyNode['type'], "plannedAction": "create"}

# Process pool dns records
for ip in kubernetesPool:
    record = kubernetesPool[ip]
    if record['plannedAction'] == "create":
        print(f"Cloudflare: Creating new record {record['name']}: {ip}")
        cf.zones.dns_records.post(zoneId, data = {"name": record['name'], "type": record['type'], "content": ip})
    elif record['plannedAction'] == "keep":
        print(f"Cloudflare: Keeping record {record['name']}: {ip}")
    elif record['plannedAction'] == "delete":
        print(f"Cloudflare: Deleting record {record['name']}: {ip}")
        cf.zones.dns_records.delete(zoneId, record['id'])
