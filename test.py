from googleapiclient import discovery
import json

srv = discovery.build("appengine", "v1")

def label_all():
    response = srv.apps().services().list(appsId="poc-iris3-exyon", pageToken=None).execute()
    project_id = "poc-iris3-exyon"
    
    for service in response["services"]:
        # try:
        label_resource(service, project_id)
        # except Exception:
        #     print("a")
    # print(response)

def label_resource(gcp_object, project_id):
    # GET ID
    print(gcp_object)
    service_name = gcp_object["id"]

    # LAST VERSION
    response = srv.apps().services().versions().list(appsId=project_id, servicesId=service_name, pageToken=None).execute()
    
    print(json.dumps(response, indent=4))
    # CREATOR LAST VERION
    creator = response["versions"][0]["createdBy"]
    # CREATE TIME LAST VERSION
    create_time = response["versions"][0]["createTime"]
    # CREATE TIME LAST VERSION
    create_time = create_time.split("T")[0]
    

    # add labels
    gcp_object['labels'] = {}
    prefix = "exyon_"
    # REMOVE lowercase letters, numeric characters, underscores, and dashes
    service_name = correctLabel(service_name)
    creator = correctLabel(creator)
    # create_time = correctLabel(create_time)
    # ADD LABELS
    gcp_object['labels'][f'{prefix}name'] = service_name
    gcp_object['labels'][f'{prefix}create_by'] = creator
    gcp_object['labels'][f'{prefix}create_time'] = create_time
    
    print(json.dumps(gcp_object, indent=4))
    srv.apps().services().patch(    
        appsId=project_id,
        servicesId=service_name,
        body=gcp_object,
        updateMask="labels"
    ).execute()

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