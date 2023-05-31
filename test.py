from googleapiclient.discovery import build
import json
import datetime
import time
import logging

project_id = "poc-iris3-exyon"

def list_all_datasets(project_id):
    # Cria o objeto de serviço do Cloud SQL usando o Discovery
    service = build("sqladmin", "v1beta4")

    # Lista as instancias do Cloud SQL
    request = service.instances().list(project=project_id)

    while request is not None:
        response = request.execute()

        for instance in response["items"]:
            name = instance["name"]
            location = instance["region"]
            databasev = instance["databaseInstalledVersion"]
            create = instance["createTime"]

            # Trata o valor da data de criação
            create = create.split("T")[0]

            # Converte para letras minúsculas
            name = name.lower()
            location = location.lower()
            databasev = databasev.lower()

            print("name: ", name)
            print("location: ", location)
            print("databasev: ", databasev)

            # Define as labels
            labels = {
                "exyon_name": name,
                "exyon_location": location,
                "exyon_database": databasev,
                "exyon_create": create
            }

            # Obtém a versão atual das configurações da instância
            settings_version = instance["settings"]["settingsVersion"]

            # Obtém o nível (tier) atual da instância
            tier = instance["settings"]["tier"]

           
            # PATCH
            try:
                # Atualiza as labels da instância
                request = service.instances().patch(
                    project=project_id,
                    instance=name,
                    body={"settings": {"userLabels": labels}},
                )
                response = request.execute()
            except:
                logging.info("A instância %s não foi atualizada, ela se encontra desligada", name)
                pass

        # Continua para a próxima página de resultados, se houver
        request = service.instances().list_next(previous_request=request, previous_response=response)

def label_resource(gcp_object, project_id):
    print("gcp_object: ", gcp_object)

list_all_datasets(project_id)
