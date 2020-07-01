import urllib3
import json
import csv
import os
from datetime import datetime
import dateutil.tz

def lambda_handler(event, context):
    sensiboKey = os.environ['SensiboAPIKey']
    webhooksKey = os.environ['WebhooksAPIKey']
    temperatureAge = int(os.environ['TempAgeSeconds'])
    
    now = datetime.now(tz=dateutil.tz.gettz(os.environ['Timezone']))
    timeNow = int(now.strftime("%H%M"))
    
    reader = csv.reader(open('crschedule'))
    crSchedule = []
    fetchSensiboData = False
    for row in reader:
        if len(row) == 7:
            startTime = int(row[5].replace(":",""))
            endTime = int(row[6].replace(":",""))
            crPeriods = []
            if startTime <= endTime:
                crPeriods.append([startTime,endTime])
            else:
                crPeriods.append([startTime,2400])
                crPeriods.append([0,endTime])
            for period in crPeriods:
                if timeNow >= period[0] and timeNow <= period[1]:
                    fetchSensiboData = True
                    crSchedule.append({"acOn":True if row[0].lower()=="on" else False,"acName":row[1],"compOper":row[2],
                        "trigTemp":float(row[3]),"iftttTrig":row[4]})
                    break

    if fetchSensiboData is False:
        return {
            'statusCode': 200,
            'body': json.dumps('No active schedules')
        }

    print("Active Schedules:", crSchedule)
    
    http = urllib3.PoolManager()
    req = http.request('GET', 'https://home.sensibo.com/api/v2/users/me/pods?fields=*&apiKey='+sensiboKey)
    payload = json.loads(req.data.decode('utf-8'))
    
    devices = {}
    for device in payload["result"]:
        deviceName = device["room"]["name"]
        if device["measurements"]["time"]["secondsAgo"] < temperatureAge:
            devices[deviceName] = {
                "acOn":device["acState"]["on"],
                "temperature":device["measurements"]["temperature"],
                "humidity":device["measurements"]["humidity"]
            }
    print("Available Devices:",devices)
    
    iftttTriggers = []
    for schedule in crSchedule:
        if schedule["acName"] in devices:
            if schedule["compOper"] == "gt":
                if devices[schedule["acName"]]["temperature"] > schedule["trigTemp"]:
                    if devices[schedule["acName"]]["acOn"] is not schedule["acOn"] and schedule["iftttTrig"] not in iftttTriggers:
                        iftttTriggers.append(schedule["iftttTrig"])
            elif schedule["compOper"] == "lt":
                if devices[schedule["acName"]]["temperature"] < schedule["trigTemp"]:
                    if devices[schedule["acName"]]["acOn"] is not schedule["acOn"] and schedule["iftttTrig"] not in iftttTriggers:
                        iftttTriggers.append(schedule["iftttTrig"])
    print("IFTTT Triggers:", iftttTriggers)
    
    for trigger in iftttTriggers:
        req = http.request('POST', 'https://maker.ifttt.com/trigger/' + trigger + '/with/key/'+webhooksKey)

    return {
        'statusCode': 200,
        'body': json.dumps('Triggered '+str(len(iftttTriggers))+' Webhooks')
    }
