# DISCOVERY GCP API CLOUDRUN V2

import os
import json
import googleapiclient.discovery

client = googleapiclient.discovery.build('run', 'v2')

def list_services(project_id, location):
    response = client.projects().locations().services().list(parent=f"projects/{project_id}/locations/us-central1", pageToken=None).execute()
    print(response)
list_services("poc-iris3-exyon", "us-central1")


# import datetime
# from google.cloud import logging

# import json

# project_id = "poc-iris3-exyon"
# filter_key = "beta.compute.instances.insert"


# def list_audit_logs(project_id, filter_key):
#     client = logging.Client(project=project_id)

#     # Defina a data limite para 30 dias atrás a partir da data atual
#     data_limite = datetime.datetime.now() - datetime.timedelta(days=30)

#     # Formate a data limite no formato adequado
#     data_limite_formatada = data_limite.strftime("%Y-%m-%dT%H:%M:%SZ")

#     # Use o filtro para buscar os logs de auditoria "cloudsql.instances.create" para o recurso "labpoclabel" criados nos últimos 30 dias
#     filtro = f'protoPayload.methodName="{filter_key}" AND timestamp>="{data_limite_formatada}" AND protoPayload.request.name:"instance-2"'
#     # AND protoPayload.request.name:"instance-2"
#     entries = client.list_entries(filter_=filtro)
#     # AND protoPayload.authorizationInfo.request.name:"topico-audit-log-test"
#     for entry in entries:
#         # Acesse as informações do registro de log no objeto entry
        
#         payload_dict = dict(entry.payload)
        
#         # Acesse as informações do registro de log no dicionário payload_dict
#         if 'authenticationInfo' in payload_dict:
#             principal_email = payload_dict['authenticationInfo'].get('principalEmail')
#             principal_email = correctLabel(principal_email)

#         print("principal_email: ", principal_email)
#         # JSON AMB
#         print(json.dumps(payload_dict, indent=4, sort_keys=True))

       

# list_audit_logs(project_id, filter_key)

