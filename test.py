from googleapiclient import discovery
import json

from plugin import Plugin

srv = discovery.build("storage", "v1")

def label_all():
    request = srv.buckets().list(project="poc-iris3-exyon")
    # while request is not None:
    response = request.execute()
    for bucket in response["items"]:
        label_resource(bucket, "poc-iris3-exyon")
    request = srv.buckets().list_next(previous_request=request, previous_response=response)

def label_resource(gcp_object, project_id):
    print(json.dumps(gcp_object, indent=4))
    
    # NAME
    name = gcp_object["name"]

    # bucket get
    request = srv.buckets().get(bucket=name)
    response = request.execute()
    # print(json.dumps(response, indent=4))
   
    # CREATE DATE
    create_date = gcp_object["timeCreated"]
    create_date = create_date.split("T")[0]



    # LABELS
    try: 
        labels = gcp_object["labels"]
    except KeyError:
        labels = None

    if labels is None:
        labels = {}
    labels["exyon_create"] = create_date
    # labels["exyon_create_by"] = create_by

    # UPDATE
    request = srv.buckets().patch(
        bucket=gcp_object["name"],
        body={
            "labels": labels
        }
    )
    response = request.execute()
    # print(json.dumps(response, indent=4))

    # print(create_date)


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