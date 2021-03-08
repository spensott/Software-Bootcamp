import requests
import json
from env import config
import base64

meraki_key = config['MERAKI_KEY']
headers = {
    'X-Cisco-Meraki-API-Key': meraki_key
} 

base_url = "https://api.meraki.com/api/v0/"
endpoint = "organizations"

# Stage 0
try:
    response = requests.get(url=f'{base_url}{endpoint}', headers=headers) 
    if response.status_code == 200:
        orgs = response.json() 
        for org in orgs:
            if org['name'] == 'DevNet Sandbox':
                orgId = org['id']
            #print("ID is " + str(org['id']) + ", name is " + str(org['name']))
except Exception as ex: 
    print(ex)

# Stage 1
endpoint_network = endpoint + '/' + str(orgId) + '/networks'  
endpoint_devices = endpoint + '/' + str(orgId) + '/devices'  
try:
    response = requests.get(url=f'{base_url}{endpoint_network}', headers=headers) 
    if response.status_code == 200:
        networks = response.json() 
        for network in networks:
            if network['name'] == 'DevNet Sandbox ALWAYS ON':
                networkId = network['id']
            #print("ID is " + str(network['id']) + ", name is " + str(network['name']))
except Exception as ex: 
    print(ex)

local_inventory = []

try:
    response = requests.get(url=f'{base_url}{endpoint_devices}', headers=headers) 
    if response.status_code == 200:
        devices = response.json() 
        for device in devices:
            if device['networkId'] == networkId:
                # populate local inventory
                local_inventory.append({
                    'name' : device['name'],
                    'type' : device['model'],
                    'mac address' : device['mac'],
                    'serial' : device['serial'],
                    'category' : 'Meraki'
                    })

except Exception as ex: 
    print(ex)

# stage 2

#get token from DNAC
base_dnac_url = str(config['DNAC_BASE_URL'])
token_url = "/dna/system/api/v1/auth/token"
url_devices = "/dna/intent/api/v1/network-device"
payload = None

headers_dnac = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
response = requests.request('POST', url=f'{base_dnac_url}{token_url}', auth=(config['DNAC_USER'], config['DNAC_PASSWORD']), headers=headers_dnac, data = payload).json()
token = response["Token"]

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-auth-token" : token
}

try:
    response = requests.get(url=f'{base_dnac_url}{url_devices}', headers=headers)
    if response.status_code == 200:
        devices = response.json()['response']
        for device in devices:
            #print("************************")
            #print(device)
            # populate local inventory
            local_inventory.append({
                'name' : device['hostname'],
                'type' : device['type'],
                'mac address' : device['macAddress'],
                'serial' : device['serialNumber'],
                'category' : 'DNAC'
            })
        # convert local inventory to JSON and print
        for local_device in local_inventory:
            print(json.dumps(local_device))
except Exception as ex: 
    print(ex)
