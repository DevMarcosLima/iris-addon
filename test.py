import datetime
from google.cloud import logging

import json

project_id = "poc-iris3-exyon"
filter_key = "google.pubsub.v1.Publisher.CreateTopic"

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


def list_audit_logs(project_id, filter_key):
    client = logging.Client(project=project_id)

    # Defina a data limite para 30 dias atrás a partir da data atual
    data_limite = datetime.datetime.now() - datetime.timedelta(days=30)

    # Formate a data limite no formato adequado
    data_limite_formatada = data_limite.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Use o filtro para buscar os logs de auditoria "cloudsql.instances.create" para o recurso "labpoclabel" criados nos últimos 30 dias
    filtro = f'protoPayload.methodName="{filter_key}" AND timestamp>="{data_limite_formatada}" AND protoPayload.request.name:"topico-audit-log-test"'
    entries = client.list_entries(filter_=filtro)
    # AND protoPayload.authorizationInfo.request.name:"topico-audit-log-test"
    for entry in entries:
        # Acesse as informações do registro de log no objeto entry
        
        payload_dict = dict(entry.payload)
        
        # Acesse as informações do registro de log no dicionário payload_dict
        if 'authenticationInfo' in payload_dict:
            principal_email = payload_dict['authenticationInfo'].get('principalEmail')
            principal_email = correctLabel(principal_email)

        if 'requestMetadata' in payload_dict:
            date_create = payload_dict['requestMetadata'].get('requestAttributes').get('time')
            date_create = date_create.split("T")[0]

        print(date_create)
        print(principal_email)
        # JSON object
        print(json.dumps(entry.payload, indent=4, sort_keys=True))

list_audit_logs(project_id, filter_key)








# # VM
# from googleapiclient.discovery import build
# import json
# import datetime
# import time
# import logging

# project_id = "poc-iris3-exyon"
# service = build("compute", "v1")
# def list_all_instance(project_id):
#     # Cria o objeto de serviço do Cloud SQL usando o Discovery
#     service = build("compute", "v1")

#     # Lista as instancias do Cloud SQL
#     request = service.instances().list(project=project_id, zone="us-central1-a")

#     response = request.execute()
#     print(response)
#     # while request is not None:
        
# # from googleapiclient.discovery import build
# # import json
# # import datetime
# # import time
# # import logging

# # project_id = "poc-iris3-exyon"

# # def list_all_datasets(project_id):
# #     # Cria o objeto de serviço do Cloud SQL usando o Discovery
# #     service = build("sqladmin", "v1beta4")

# #     # Lista as instancias do Cloud SQL
# #     request = service.instances().list(project=project_id)

# #     while request is not None:
# #         response = request.execute()

# #         for instance in response["items"]:
# #             name = instance["name"]
# #             location = instance["region"]
# #             databasev = instance["databaseInstalledVersion"]
# #             create = instance["createTime"]

# #             # Trata o valor da data de criação
# #             create = create.split("T")[0]

# #             # Converte para letras minúsculas
# #             name = name.lower()
# #             location = location.lower()
# #             databasev = databasev.lower()

# #             print("name: ", name)
# #             print("location: ", location)
# #             print("databasev: ", databasev)

# #             # Define as labels
# #             labels = {
# #                 "exyon_name": name,
# #                 "exyon_location": location,
# #                 "exyon_database": databasev,
# #                 "exyon_create": create
# #             }

# #             # Obtém a versão atual das configurações da instância
# #             settings_version = instance["settings"]["settingsVersion"]

# #             # Obtém o nível (tier) atual da instância
# #             tier = instance["settings"]["tier"]

           
# #             # PATCH
# #             try:
# #                 # Atualiza as labels da instância
# #                 request = service.instances().patch(
# #                     project=project_id,
# #                     instance=name,
# #                     body={"settings": {"userLabels": labels}},
# #                 )
# #                 response = request.execute()
# #             except:
# #                 logging.info("A instância %s não foi atualizada, ela se encontra desligada", name)
# #                 pass

# #         # Continua para a próxima página de resultados, se houver
# #         request = service.instances().list_next(previous_request=request, previous_response=response)

# # def label_resource(gcp_object, project_id):
# #     print("gcp_object: ", gcp_object)

# # list_all_datasets(project_id)
