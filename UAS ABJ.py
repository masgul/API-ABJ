import requests
from time import *
import realhttp
import json

base_url = "http://192.168.10.181/api/v1"
user = "warnet"
password = "masuk"

bot_token = "5488164199:AAE3-qK-G9gQPeMco7lHYH7wARpViyZawd4"
bot_chatID = "-657138368"


def get_ticket():
    headers = {"content-type": "application/json"}
    data = {"username": user, "password": password}

    response = requests.post(base_url+"/ticket", headers=headers, json=data)
    ticket = response.json()
    service_ticket = ticket["response"]["serviceTicket"]
    print("token : " + service_ticket)
    return service_ticket
    
def get_network_device_count():
    ticket = get_ticket()
    headers = {"X-Auth-Token": ticket}
    response = requests.get(base_url+"/network-device/count", headers=headers)
    managed_device_count = response.json()
    print("Total Managed Device :", managed_device_count["response"])
    
def get_network_device():
    ticket = get_ticket()
    headers = {"X-Auth-Token": ticket}
    response = requests.get(base_url+"/network-device", headers=headers)
    print("===Daftar Managed Device===")
    print("Status Code : ",response.status_code)
    managed_device = response.json()
    networkDevices = managed_device["response"]

    for networkDevice in networkDevices:
        print(networkDevice["hostname"], "\t\t", networkDevice["platformId"], "\t", networkDevice["managementIpAddress"])
        
def get_connected_hosts():
    ticket = get_ticket()
    headers = {"X-Auth-Token": ticket}
    response = requests.get(base_url+"/host", headers=headers, verify=False)
    print("===Daftar Host===")
    print("Status Code : ",response.status_code)
    connectedDevices = response.json()
    devices = connectedDevices["response"]
    print("Device Name \t IP Address \t MAC Address \t Connected Port")
    for device in devices:
        print(device["hostName"], "\t", device["hostIp"], "\t", device["hostMac"], "\t\t", device["connectedInterfaceName"])
        
def get_network_health():
    ticket = get_ticket()
    headers = {"X-Auth-Token": ticket}
    response = requests.get(base_url+"/assurance/health", headers=headers)
    health = response.json()
    network_health = health['response'][0]['networkDevices']['totalPercentage']
    return network_health

def get_network_issues():
    ticket = get_ticket()
    headers = {'Accept': 'application/yang-data+json', 'X-Auth-Token': ticket}
    issues = requests.get(url = base_url + "/assurance/health-issues", headers=headers)
    issue_details = issues.json()
    devices = len(issue_details['response'])
    output = "Peringatan! Terjadi gangguan akses ke "+ str(devices) +" perangkat berikut:\n"
    output += "-"*60 +"\n"
    output += "NO. | PERANGKAT | WAKTU | DESKRIPSI\n"
    output +="-"*60 +"\n"
    number=1
    for device in issue_details['response']:
        output += ""+ str(number) +". | "+ device['issueSource'] +" | "+ device['issueTimestamp'] +" | "+ device['issueDescription'] +"\n"
        number +=1
    return output
    
def onHTTPDone(status, data, replyHeader): 
    if status == 200:
        print("Pesan Network Issues sukses dikirim!")
    else:
        print("Pesan Network Issues gagal dikirim!")
        
def escape_underscore(txt):
    return txt.replace ("_", "-")


if __name__ == "__main__":
    print("===================================================================================")
    print("==============MONITORING & MANAJERIAL JARINGAN MENGGUNAKAN SDN CONTROLLER REST API==============")
    print("===================================================================================")
    print("Kode REST API : " + get_ticket())
    get_network_device_count()
    get_network_device()
    get_connected_hosts()
    network_health = get_network_health()
    if int(network_health) < 100:
        issues = get_network_issues()
        print(issues)
        http = realhttp.RealHTTPClient()
        issues = escape_underscore(issues)
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + issues
        http.get(send_text)
        http.onDone(onHTTPDone)
        while True:
            sleep(5)
    else:
        print("Persentase Network Health: "+ network_health +"%")