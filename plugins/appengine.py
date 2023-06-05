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
                response = self._google_api_client().apps().services().list(appsId="poc-iris3-exyon", pageToken=None).execute()
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
        # GET ID
        try:
            print(gcp_object)
            service_name = gcp_object["id"]

            # LAST VERSION
            response = self._google_api_client().apps().services().versions().list(appsId=project_id, servicesId=service_name, pageToken=None).execute()
            
            # print(json.dumps(response, indent=4))
            # CREATOR LAST VERION
            creator = response["versions"][0]["createdBy"]
            # CREATE TIME LAST VERSION
            create_time = response["versions"][0]["createTime"]
            # CREATE TIME LAST VERSION
            create_time = create_time.split("T")[0]
            # aaaa-mm
            create_time = create_time.split("-")[0] + "-" + create_time.split("-")[1]
            

            # add labels
            gcp_object['labels'] = {}
            prefix = "exyon_"
            # REMOVE lowercase letters, numeric characters, underscores, and dashes
            service_name = correctLabel(service_name)
            creator = correctLabel(creator)
            # create_time = correctLabel(create_time)
            # ADD LABELS
            gcp_object['labels'][f'app-engine'] = service_name
            gcp_object['labels'][f'custo-app-engine'] = service_name
            gcp_object['labels'][f'{prefix}create_by'] = creator
            gcp_object['labels'][f'ano-mes'] = create_time
            
            # print(json.dumps(gcp_object, indent=4))
            self._google_api_client().apps().services().patch(    
                appsId=project_id,
                servicesId=service_name,
                body=gcp_object,
                updateMask="labels"
            ).execute()

        except errors.HttpError as e:
            if "SERVING_STATUS_UNSPECIFIED" in gcp_object.get("servingStatus", {}):
                logging.exception("App Engine service is not fully deployed yet, which is why we do not label it on-demand in the usual way")
            raise e

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