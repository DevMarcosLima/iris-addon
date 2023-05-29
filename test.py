from googleapiclient import discovery
import json

from plugin import Plugin

srv = discovery.build("run", "v2")

def label_all():
    project_id = "poc-iris3-exyon"
    response = srv.projects().locations().services().list(parent=f"projects/{project_id}/locations/us-central1", pageToken=None).execute()
    if "services" not in response:
        return
    for service in response["services"]:
        try:
            label_resource(service, project_id)
        except Exception:
            print("error")
    if "nextPageToken" in response:
        page_token = response["nextPageToken"]
    else:
        return
def label_resource(gcp_object, project_id):
    print(json.dumps(gcp_object, indent=4))

    creator = gcp_object["creator"]	
    creator = correctLabel(creator)
    print(creator)



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