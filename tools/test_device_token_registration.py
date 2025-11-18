import requests

base='http://127.0.0.1:8000/api'
# Obtener token
resp = requests.post(f'{base}/token/', json={'username':'apitest','password':'apitestpassword'})
print('TOKEN STATUS', resp.status_code)
print('BODY', resp.text)

if resp.status_code==200:
    token = resp.json()['access']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    # POST a device-tokens
    body = {'token': 'TEST_FCM_123', 'platform': 'android'}
    r2 = requests.post(f'{base}/device-tokens/', headers=headers, json=body)
    print('REGISTER STATUS', r2.status_code)
    print('REGISTER BODY', r2.text)
    # Probar desregistro
    r3 = requests.post(f'{base}/device-tokens/unregister/', headers=headers, json={'token': body['token']})
    print('UNREGISTER STATUS', r3.status_code)
    print('UNREGISTER BODY', r3.text)
else:
    print('Error al obtener token')
