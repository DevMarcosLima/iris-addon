import logging
from typing import Dict, Optional

from googleapiclient import errors

from plugin import Plugin
from util.utils import log_time, timing


class Appengine(Plugin):
    @staticmethod
    def _discovery_api():
        return "appengine", "v1"

    @staticmethod
    def method_names():
        return ["appengine.services.create"]

    @classmethod
    def _cloudclient(cls, _=None):
        logging.info("_cloudclient for %s", cls.__name__)
        raise NotImplementedError("There is no Cloud Client library for " + cls.__name__)

    @staticmethod
    def is_labeled_on_creation() -> bool:
        # No App Engine, os rótulos podem ser aplicados durante a criação do serviço.
        return True

    def _gcp_name(self, gcp_object):
        return self._name_no_separator(gcp_object)

    def _gcp_region(self, gcp_object):
        try:
            return gcp_object["locationId"]
        except KeyError:
            logging.exception(f"Error getting region for {gcp_object['name']}")
            return None

    def _get_resource(self, project_id, name):
        try:
            logging.warning(f"Getting resource {name} in project {project_id}")
            result = (
                self._google_api_client()
                .apps()
                .services()
                .get(appsId=project_id, servicesId=name)
                .execute()
            )
            logging.warning(f"Successfully retrieved resource {name} in project {project_id}")
            logging.info(f"Successfully retrieved resource {name} in project {project_id}")
            return result
        except errors.HttpError:
            logging.exception(f"Error getting resource {name} in project {project_id}")
            return None

    def get_gcp_object(self, log_data: Dict) -> Optional[Dict]:
        try:
            if "protoPayload" not in log_data or "response" not in log_data["protoPayload"]:
                return None
            labels_ = log_data["resource"]["labels"]
            service = labels_["service_id"]
            service = self._get_resource(log_data["resource"]["projectId"], service)
            return service
        except Exception:
            logging.exception(f"Error getting resource {log_data['resource']['name']}")
            return None

    def label_all(self, project_id):
        logging.warning(f"Labeling all {type(self).__name__} in {project_id}")
        logging.info(f"Labeling all {type(self).__name__} in {project_id}")
        page_token = None
        try:
            while True:
                response = self._google_api_client().apps().services().list(appsId=project_id, pageToken=page_token).execute()
                if "services" not in response:
                    return
                for service in response["services"]:
                    try:
                        self.label_resource(service, project_id)
                    except Exception:
                        logging.exception("Error labeling resource")
                if "nextPageToken" in response:
                    page_token = response["nextPageToken"]
                else:
                    return
        except Exception:
            logging.exception("Error while labeling all resources")

    @log_time
    def label_resource(self, gcp_object, project_id):
        labels = gcp_object.get("labels", {})
        if labels is None:
            logging.warning(f"Skipping {gcp_object['name']} because it is not labeled")
            return
        try:
            service_name = gcp_object["name"]

            # json body
            service_body = gcp_object
            # ADD LABELS in json body
            # GET createTime
            service_name = gcp_object["name"]
            is_name = service_name.split("/")[-1]
            is_create = gcp_object["createTime"]
            is_create = is_create.split("T")[0]
            is_location = gcp_object["locationId"]

            # IF DONT HAVE LABELS
            if not service_body.get("labels"):
                service_body["labels"] = {}
            prefix = "exyon_"
            # ADD LABELS
            service_body["labels"][f'{prefix}name'] = is_name
            service_body["labels"][f'{prefix}create'] = is_create
            service_body["labels"][f'{prefix}location'] = is_location

            self._google_api_client().apps().services().patch(
                appsId=project_id,
                servicesId=is_name,
                body=service_body,
            ).execute()

        except errors.HttpError as e:
            if "SERVING_STATUS_UNSPECIFIED" in gcp_object.get("servingStatus", {}):
                logging.exception("App Engine service is not fully deployed yet, which is why we do not label it on-demand in the usual way")
            raise e
