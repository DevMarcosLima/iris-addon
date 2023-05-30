from googleapiclient import discovery
import json

from plugin import Plugin

srv = discovery.build("bigquery", "v2")

def label_all():
    project_id = "poc-iris3-exyon"
    page_token = None
    # while True:
    # response = srv.apps().services().list(appsId="poc-iris3-exyon", pageToken=None).execute()
    datasets = srv._cloudclient(project_id).list_datasets()
    for dataset in datasets:
        srv.__label_dataset_and_tables(project_id, dataset._properties)


def label_resource(gcp_object, project_id):
    print(json.dumps(gcp_object, indent=4))




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

label_all()