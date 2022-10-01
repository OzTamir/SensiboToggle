import requests
import json

_SERVER = 'https://home.sensibo.com/api/v2'

# Client code taken from https://github.com/Sensibo/sensibo-python-sdk/blob/master/sensibo_client.py
class SensiboClientAPI(object):
    def __init__(self, api_key):
        self._api_key = api_key

    def _get(self, path, ** params):
        params['apiKey'] = self._api_key
        response = requests.get(_SERVER + path, params = params)
        response.raise_for_status()
        return response.json()

    def _patch(self, path, data, ** params):
        params['apiKey'] = self._api_key
        response = requests.patch(_SERVER + path, params = params, data = data)
        response.raise_for_status()
        return response.json()

    def devices(self):
        result = self._get("/users/me/pods", fields="id,room")
        return {x['room']['name']: x['id'] for x in result['result']}

    def pod_ac_state(self, podUid):
        result = self._get("/pods/%s/acStates" % podUid, limit = 2, fields="acState")
        return result['result'][0]['acState']

    def pod_change_ac_state(self, podUid, currentAcState, propertyToChange, newValue):
        self._patch("/pods/%s/acStates/%s" % (podUid, propertyToChange),
                json.dumps({'currentAcState': currentAcState, 'newValue': newValue}))


def toggle_ac(sensibo_client, device_name):
    device_uid = sensibo_client.devices()[device_name]
    ac_state = sensibo_client.pod_ac_state(device_uid)
    sensibo_client.pod_change_ac_state(device_uid, ac_state, "on", not ac_state['on'])

def lambda_handler(event, context):
    try:
        event_data = event['queryStringParameters']
        client = SensiboClientAPI(event_data['api_key'])
        toggle_ac(client, event_data['device_name'])
        return {'statusCode': 200, 'body': 'OK'}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(str(e))}

