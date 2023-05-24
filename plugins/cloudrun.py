import logging
from typing import Dict, Optional

from googleapiclient import errors

from plugin import Plugin
from util.utils import log_time, timing


class Cloudrun(Plugin):
    @staticmethod
    def _discovery_api():
        return "run", "v2"

    @staticmethod
    def method_names():
        return ["cloudrun.services.create"]

    @classmethod
    def _cloudclient(cls, _=None):
        logging.info("_cloudclient for %s", cls.__name__)
        raise NotImplementedError("There is no Cloud Client library for " + cls.__name__)

    @staticmethod
    def is_labeled_on_creation() -> bool:
        # As Labels não podem ser aplicados aos serviços do Cloud Run durante a criação.
        # Por que:
        #     O serviço Cloud Run é criado de forma assíncrona e pode não estar imediatamente disponível para atualizações de labels.
        # Como:
        #     Use uma solução alternativa para rotular o serviço depois que ele estiver totalmente implantado e disponível.
        return False

    def _gcp_name(self, gcp_object):
        return self._name_no_separator(gcp_object)

    def _gcp_region(self, gcp_object):
        try:
            return gcp_object["metadata"]["labels"]["region"].lower()
        except KeyError:
            logging.exception(f"Error getting region for {gcp_object['metadata']['name']} MARCOSx003")
            return None

    def _get_resource(self, project_id, name):
        try:
            logging.warning(f"MARCOS Getting resource {name} in project {project_id}")
            result = (
                self._google_api_client()
                .projects()
                .locations()
                .services()
                .get(name=name)
                .execute()
            )
            logging.warning(f"MARCOS Getting resource {name} in project {project_id}")
            logging.info(f"MARCOS Getting resource {name} in project {project_id}")
            return result
        except errors.HttpError:
            logging.exception(f"Error getting resource {name} in project {project_id} MARCOSx001")
            return None

    def get_gcp_object(self, log_data: Dict) -> Optional[Dict]:
        try:
            if "response" not in log_data["protoPayload"]:
                return None
            labels_ = log_data["resource"]["labels"]
            service = labels_["service_name"]
            service = self._get_resource("poc-iris3-exyon", service)
            return service
        except Exception:
            logging.exception(f"Error getting resource {log_data['resource']['name']} MARCOSx002")
            return None

    def label_all(self, project_id):
        # LIST ALL CLOUD RUN SERVICES
        with timing(f"label_all({type(self).__name__}) in {project_id}"):
            logging.warning(f"0x1 MARCOS Labeling all {type(self).__name__} in {project_id}")
            logging.info(f"0x1 MARCOS Labeling all {type(self).__name__} in {project_id}")
            page_token = None
            try:
                while True:
                    response = self.projects().locations().services().list(parent=f"projects/{project_id}/locations/us-central1", pageToken=None).execute()
                    if "services" not in response:
                        return
                    for service in response["services"]:
                        try:
                            self.label_resource(service, project_id)
                        except Exception:
                            logging.exception("a")
                    if "nextPageToken" in response:
                        page_token = response["nextPageToken"]
                    else:
                        return
            except Exception:
                logging.exception("")

    @log_time
    def label_resource(self, gcp_object, project_id):
        labels = gcp_object.get("labels", {})
        if labels is None:
            logging.warning(f"1x2 MARCOS Skipping {gcp_object['name']} because it is not labeled")
            return
        try:
            service_name = gcp_object["name"]
            # {
            #     'name': 'projects/poc-iris3-exyon/locations/us-central1/services/hello',
            #     'uid': '5990611e-0f9c-4e8b-a8a1-94e8ac414b5b',
            #     'generation': '2',
            #     'labels': {
            #         'exyon_create': '2023-05-16',
            #         'exyon_location': 'us-east1',
            #         'exyon_name': 'hello'
            #     },
            #     'createTime': '2023-05-16T19:03:06.150793Z',
            #     'updateTime': '2023-05-23T20:59:00.124692Z',
            #     'creator': 'italo.teixeira@ipnet.cloud',
            #     'lastModifier': 'marcos.lima.t@ipnet.cloud',
            #     'client': 'cloud-console',
            #     'ingress': 'INGRESS_TRAFFIC_ALL',
            #     'launchStage': 'GA',
            #     'template': {
            #         'scaling': {'maxInstanceCount': 10},
            #         'timeout': '300s',
            #         'serviceAccount': 'poc-iris3-exyon@appspot.gserviceaccount.com',
            #         'containers': [
            #             {
            #                 'image': 'us-docker.pkg.dev/cloudrun/container/hello',
            #                 'resources': {'limits': {'cpu': '1000m', 'memory': '512Mi'}, 'cpuIdle': True},
            #                 'ports': [{'name': 'http1', 'containerPort': 8080}],
            #                 'startupProbe': {'timeoutSeconds': 240, 'periodSeconds': 240, 'failureThreshold': 1, 'tcpSocket': {'port': 8080}}
            #             }
            #         ],
            #         'maxInstanceRequestConcurrency': 80
            #     },
            #     'traffic': [
            #         {'type': 'TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST', 'percent': 100}
            #     ],
            #     'observedGeneration': '2',
            #     'terminalCondition': {
            #         'type': 'Ready',
            #         'state': 'CONDITION_SUCCEEDED',
            #         'lastTransitionTime': '2023-05-23T20:59:15.302196Z'
            #     },
            #     'conditions': [
            #         {'type': 'RoutesReady', 'state': 'CONDITION_SUCCEEDED', 'lastTransitionTime': '2023-05-23T20:59:15.493440Z'},
            #         {'type': 'ConfigurationsReady', 'state': 'CONDITION_SUCCEEDED', 'lastTransitionTime': '2023-05-23T20:59:09.603445Z'}
            #     ],
            #     'latestReadyRevision': 'projects/poc-iris3-exyon/locations/us-central1/services/hello/revisions/hello-00002-4wm',
            #     'latestCreatedRevision': 'projects/poc-iris3-exyon/locations/us-central1/services/hello/revisions/hello-00002-4wm',
            #     'trafficStatuses': [
            #         {'type': 'TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST', 'percent': 100}
            #     ],
            #     'uri': 'https://hello-zjb2v377mq-uc.a.run.app',
            #     'etag': '"CJTStKMGEKDMujs/cHJvamVjdHMvcG9jLWlyaXMzLWV4eW9uL2xvY2F0aW9ucy91cy1jZW50cmFsMS9zZXJ2aWNlcy9oZWxsbw"'
            # }

            # json body
            service_body = gcp_object
            # ADD LABELS in json body
            # GET createTime
            service_name = gcp_object["name"]
            is_name = service_name.split("/")[-1]
            is_create = gcp_object["createTime"]
            is_create = is_create.split("T")[0]
            is_location = service_name.split("/")[3]

            service_body = {'name': 'projects/poc-iris3-exyon/locations/us-central1/services/hello', 'uid': '5990611e-0f9c-4e8b-a8a1-94e8ac414b5b', 'generation': '2', 'labels': {'exyon_create':'-', 'exyon_location': '-', 'exyon_name': '-'}, 'createTime': '2023-05-16T19:03:06.150793Z', 'updateTime': '2023-05-23T20:59:00.124692Z', 'creator': 'italo.teixeira@ipnet.cloud', 'lastModifier': 'marcos.lima.t@ipnet.cloud', 
'client': 'cloud-console', 'ingress': 'INGRESS_TRAFFIC_ALL', 'launchStage': 'GA', 'template': {'scaling': {'maxInstanceCount': 10}, 'timeout': '300s', 'serviceAccount': 'poc-iris3-exyon@appspot.gserviceaccount.com', 'containers': [{'image': 'us-docker.pkg.dev/cloudrun/container/hello', 'resources': {'limits': {'cpu': '1000m', 'memory': '512Mi'}, 'cpuIdle': True}, 'ports': [{'name': 'http1', 'containerPort': 8080}], 'startupProbe': {'timeoutSeconds': 240, 'periodSeconds': 240, 'failureThreshold': 1, 'tcpSocket': {'port': 8080}}}], 'maxInstanceRequestConcurrency': 80}, 'traffic': [{'type': 'TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST', 'percent': 100}], 'observedGeneration': '2', 'terminalCondition': {'type': 'Ready', 'state': 'CONDITION_SUCCEEDED', 'lastTransitionTime': '2023-05-23T20:59:15.302196Z'}, 'conditions': [{'type': 'RoutesReady', 'state': 'CONDITION_SUCCEEDED', 'lastTransitionTime': '2023-05-23T20:59:15.493440Z'}, {'type': 'ConfigurationsReady', 'state': 'CONDITION_SUCCEEDED', 'lastTransitionTime': '2023-05-23T20:59:09.603445Z'}], 'latestReadyRevision': 'projects/poc-iris3-exyon/locations/us-central1/services/hello/revisions/hello-00002-4wm', 'latestCreatedRevision': 'projects/poc-iris3-exyon/locations/us-central1/services/hello/revisions/hello-00002-4wm', 'trafficStatuses': [{'type': 'TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST', 'percent': 100}], 'uri': 'https://hello-zjb2v377mq-uc.a.run.app', 'etag': '"CJTStKMGEKDMujs/cHJvamVjdHMvcG9jLWlyaXMzLWV4eW9uL2xvY2F0aW9ucy91cy1jZW50cmFsMS9zZXJ2aWNlcy9oZWxsbw"'}
            
            service_body["labels"]['exyon_name'] = is_name
            service_body["labels"]['exyon_create'] = is_create
            service_body["labels"]['exyon_location'] = is_location

            self.projects().locations().services().patch(
                name=f"projects/poc-iris3-exyon/locations/us-central1/services/{is_label_name}",
                body=service_body,
            ).execute()

        except errors.HttpError as e:
            if "SERVICE_STATUS_UNSPECIFIED" in gcp_object.get("status", {}):
                logging.exception("Cloud Run service is not fully deployed yet, which is why we do not label it on-demand in the usual way")
            raise e
