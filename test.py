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

from googleapiclient.discovery import build
import json
import datetime
import time
project_id = "poc-iris3-exyon"

def list_all_datasets(project_id):
    # Cria o objeto de serviço do BigQuery usando o Discovery
    service = build("bigquery", "v2")

    # Faz a chamada à API para listar os conjuntos de dados
    datasets = service.datasets().list(projectId=project_id).execute()

    # Itera sobre os conjuntos de dados retornados
    if "datasets" in datasets:
        for dataset in datasets["datasets"]:
            name = dataset['datasetReference']['datasetId']
            label_resource(name, project_id)

def label_resource(dataset, project_id):
    # Cria o objeto de serviço do BigQuery usando o Discovery
    service = build("bigquery", "v2")

    # Faz a chamada à API para obter os metadados do conjunto de dados
    dataset_metadata = service.datasets().get(projectId=project_id, datasetId=dataset).execute()
    
    # GET access role owner userByEmail
    creater = dataset_metadata['access'][2]['userByEmail']

    create_time = dataset_metadata['creationTime']

    # CONVERTE CREATE
    create_time = datetime.datetime.fromtimestamp(int(create_time)/1000).strftime('%Y-%m-%d')
    
    creater = correctLabel(creater)
    print(creater)
    # INSERT LABEL

    if 'labels' not in dataset_metadata:
        dataset_metadata['labels'] = {}

    dataset_metadata['labels']['exyon_create_by'] = creater
    dataset_metadata['labels']['exyon_create'] = create_time

    # UPDATE LABEL
    print(dataset, dataset_metadata)
    service.datasets().patch(projectId=project_id, datasetId=dataset, body=dataset_metadata).execute()

    

    # Acessa os metadados do conjunto de dados
    # print(json.dumps(dataset_metadata, indent=4))

list_all_datasets(project_id)

