import datetime
from google.cloud import logging

import json

project_id = "poc-iris3-exyon"
filter_key = "cloudsql.instances.create"

def list_audit_logs(project_id, filter_key):
    client = logging.Client(project=project_id)

    # Defina a data limite para 30 dias atrás a partir da data atual
    data_limite = datetime.datetime.now() - datetime.timedelta(days=30)

    # Formate a data limite no formato adequado
    data_limite_formatada = data_limite.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Use o filtro para buscar os logs de auditoria "cloudsql.instances.create" para o recurso "labpoclabel" criados nos últimos 30 dias
    filtro = f'protoPayload.methodName="{filter_key}" AND timestamp>="{data_limite_formatada}" AND protoPayload.authorizationInfo.resourceAttributes.name:"labpoclabel"'
    entries = client.list_entries(filter_=filtro)

    for entry in entries:
        # Acesse as informações do registro de log no objeto entry
        
        payload_dict = dict(entry.payload)
        
        # Acesse as informações do registro de log no dicionário payload_dict
        if 'authenticationInfo' in payload_dict:
            principal_email = payload_dict['authenticationInfo'].get('principalEmail')
            principal_email = correctLabel(principal_email)

        return principal_email
        # JSON object
        # print(json.dumps(entry.payload, indent=4, sort_keys=True))

# list_audit_logs(project_id, filter_key)

def correctLabel(label):
    label = label.replace("-", "_")
    label = label.replace(" ", "_")
    label = label.replace(".", "_")
    label = label.replace(":", "_")
    label = label.replace(";", "_")
    label = label.replace(",", "_")
    label = label.replace("?", "_")
    label = label.replace("!", "_")
    label = label.replace("(", "_")
    label = label.replace(")", "_")
    label = label.replace("[", "_")
    label = label.replace("]", "_")
    label = label.replace("{", "_")
    label = label.replace("}", "_")
    label = label.replace("<", "_")
    label = label.replace(">", "_")
    label = label.replace("/", "_")
    label = label.replace("\\", "_")
    label = label.replace("|", "_")
    label = label.replace("=", "_")
    label = label.replace("+", "_")
    label = label.replace("'", "_")
    label = label.replace('"', "_")
    label = label.replace("@", "-")
    label = label.replace("#", "_")
    label = label.replace("$", "_")
    label = label.replace("%", "_")
    label = label.replace("^", "_")
    label = label.replace("&", "_")
    label = label.replace("*", "_")
    label = label.replace("~", "_")
    label = label.replace("`", "_")

    return label

