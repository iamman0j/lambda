import boto3
import os, os.path, sys
from datetime import datetime, timedelta 

def getCloudTrailEvents(startDateTime, rgn):
    cloudTrail = boto3.client('cloudtrail', region_name=rgn)
    attrList = [{'AttributeKey': 'ResourceType', 'AttributeValue': 'AWS::EC2::Volume'}]
    eventList = []
    response = cloudTrail.lookup_events(LookupAttributes=attrList, StartTime=startDateTime, MaxResults=50)
    eventList += response['Events']
    while('NextToken' in response):
        response = cloudTrail.lookup_events(LookupAttributes=attrList, StartTime=startDateTime, MaxResults=50, NextToken=response['NextToken'])
        eventList += response['Events']
    return eventList

def getAvailableVolumes(rgn):
    ec2 = boto3.client('ec2', region_name=rgn)
    availableVolList = []
    filterList = [{'Name': 'status', 'Values': ['available']}]
    response = ec2.describe_volumes(Filters=filterList, MaxResults=500)
    for v in response['Volumes']:
        availableVolList.append(v['VolumeId'])
    while('NextToken' in response):
        response = ec2.describe_volumes(Filters=filterList, MaxResults=500, NextToken=response['NextToken'])
        for v in response['Volumes']:
            availableVolList.append(v['VolumeId'])
    return availableVolList
    
def getRecentActiveVolumes(events):
    recentActiveVolumeList = []
    for e in events:
        for i in e['Resources']:
            if i['ResourceType'] == 'AWS::EC2::Volume':
                recentActiveVolumeList.append(i['ResourceName'])
    recentActiveVolumeSet = set(recentActiveVolumeList)
    return recentActiveVolumeSet
    
def identifyAgedVolumes(availableVolList, activeVolList):
    if len(availableVolList) == 0:
        return None
    else:
        agedVolumes = list(set(availableVolList) - set(activeVolList))
        return agedVolumes
        
def lambda_handler(event, lambda_context):
    startDateTime = datetime.today() - timedelta(days=int('2'))
    eventList = getCloudTrailEvents(startDateTime, 'eu-west-1')
    activeVols = getRecentActiveVolumes(eventList)
    availableVols = getAvailableVolumes('eu-west-1')
    if len(availableVols) == 0:
        return len(availableVols)
    else:
        flaggedVols = identifyAgedVolumes(availableVols, activeVols)
        for flaggedVol in flaggedVols:
            client = boto3.resource('ec2', region_name='eu-west-1')
            v=client.Volume(flaggedVol)
            print('Volumes to be deleted ' + str(v))
            delete = True
            if v.tags:
                for tag in v.tags:
                    if tag['Key'] == 'delete' and tag['Value'] == 'no':
                        print(str(v) + ' not to be deleted.')
                        delete = False        
                if delete:
                    response = v.delete()
                    print(response) 
            else:
                response = v.delete()
                print(response)
