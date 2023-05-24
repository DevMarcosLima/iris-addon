from googleapiclient import discovery

srv = discovery.build("run", "v2")
def label_all():
    response = srv.projects().locations().services().list(parent=f"projects/poc-iris3-exyon/locations/us-central1", pageToken=None).execute()

    project_id = "poc-iris3-exyon"

    if "services" not in response:
        print("no services")
    for service in response["services"]:
        # try:
        print("labeling")
        label_resource(service, project_id)
        # except Exception:
        #     print("error labeling")
    if "nextPageToken" in response:
        page_token = response["nextPageToken"]
    else:
        print("no more pages")

def label_resource(gcp_object, project_id):

    print("labeling")
    print(gcp_object)
    labels = gcp_object.get("labels", {})
    if labels is None:
        print("skipping")
    # try:
    service_name = gcp_object["name"]
    is_name = service_name.split("/")[-1]
    is_create = gcp_object["createTime"]
    is_create = is_create.split("T")[0]
    is_location = service_name.split("/")[3]

    # LOG Warning gcp
    service_body = {'name': 'projects/poc-iris3-exyon/locations/us-central1/services/hello', 'uid': '5990611e-0f9c-4e8b-a8a1-94e8ac414b5b', 'generation': '2', 'labels': {'exyon_create':'2023-05-16', 'exyon_location': 'us-east1', 'exyon_name': 'hello'}, 'createTime': '2023-05-16T19:03:06.150793Z', 'updateTime': '2023-05-23T20:59:00.124692Z', 'creator': 'italo.teixeira@ipnet.cloud', 'lastModifier': 'marcos.lima.t@ipnet.cloud', 
'client': 'cloud-console', 'ingress': 'INGRESS_TRAFFIC_ALL', 'launchStage': 'GA', 'template': {'scaling': {'maxInstanceCount': 10}, 'timeout': '300s', 'serviceAccount': 'poc-iris3-exyon@appspot.gserviceaccount.com', 'containers': [{'image': 'us-docker.pkg.dev/cloudrun/container/hello', 'resources': {'limits': {'cpu': '1000m', 'memory': '512Mi'}, 'cpuIdle': True}, 'ports': [{'name': 'http1', 'containerPort': 8080}], 'startupProbe': {'timeoutSeconds': 240, 'periodSeconds': 240, 'failureThreshold': 1, 'tcpSocket': {'port': 8080}}}], 'maxInstanceRequestConcurrency': 80}, 'traffic': [{'type': 'TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST', 'percent': 100}], 'observedGeneration': '2', 'terminalCondition': {'type': 'Ready', 'state': 'CONDITION_SUCCEEDED', 'lastTransitionTime': '2023-05-23T20:59:15.302196Z'}, 'conditions': [{'type': 'RoutesReady', 'state': 'CONDITION_SUCCEEDED', 'lastTransitionTime': '2023-05-23T20:59:15.493440Z'}, {'type': 'ConfigurationsReady', 'state': 'CONDITION_SUCCEEDED', 'lastTransitionTime': '2023-05-23T20:59:09.603445Z'}], 'latestReadyRevision': 'projects/poc-iris3-exyon/locations/us-central1/services/hello/revisions/hello-00002-4wm', 'latestCreatedRevision': 'projects/poc-iris3-exyon/locations/us-central1/services/hello/revisions/hello-00002-4wm', 'trafficStatuses': [{'type': 'TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST', 'percent': 100}], 'uri': 'https://hello-zjb2v377mq-uc.a.run.app', 'etag': '"CJTStKMGEKDMujs/cHJvamVjdHMvcG9jLWlyaXMzLWV4eW9uL2xvY2F0aW9ucy91cy1jZW50cmFsMS9zZXJ2aWNlcy9oZWxsbw"'}
    
    service_body["labels"]['exyon_name'] = is_name
    service_body["labels"]['exyon_create'] = is_create
    service_body["labels"]['exyon_location'] = is_location

    print("patching")
    print(gcp_object)
    srv.projects().locations().services().patch(
        name=f"projects/poc-iris3-exyon/locations/us-central1/services/hello",
        body=service_body,
    ).execute()

    # except:
    #     print("error")

label_all()

# items = l["services"]
# print(items)
# print(l)

