import urllib3
import json
import csv
import os
from datetime import datetime
import dateutil.tz

def lambda_handler(event, context):
    scheduleFilaname = os.environ['ScheduleFilename']
    sensiboKey = os.environ['SensiboAPIKey']
    webhooksKey = os.environ['WebhooksAPIKey']
    temperatureAge = int(os.environ['TempAgeSeconds'])
    timeNow = int((datetime.now(tz=dateutil.tz.gettz(os.environ['Timezone']))).strftime("%H%M"))
    
    # Parse the schedule file
    crSchedule = []
    fetchSensiboData = False
    schedFile = csv.reader(open(scheduleFilaname))
    for row in schedFile:
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

    # Exit if there are no schedules to process at this specific time
    if fetchSensiboData is False:
        print("No active schedules to process")
        return {
            'statusCode': 200,
            'body': json.dumps('No active schedules')
        }

    print("Active Schedules:", crSchedule)
    
    # Retrieve device data from the Sensibo API
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
    
    # Check the schedule against devices and see if conditions are met
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
    
    # Call IFTTT Webhooks triggers
    for trigger in iftttTriggers:
        req = http.request('POST', 'https://maker.ifttt.com/trigger/' + trigger + '/with/key/'+webhooksKey)

    print('Triggered '+str(len(iftttTriggers))+' Webhooks')
    return {
        'statusCode': 200,
        'body': json.dumps('Triggered '+str(len(iftttTriggers))+' Webhooks')
    }
