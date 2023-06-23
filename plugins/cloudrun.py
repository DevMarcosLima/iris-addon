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
            return None

    def _get_resource(self, project_id, name):
        try:
            result = (
                self._google_api_client()
                .projects()
                .locations()
                .services()
                .get(name=name)
                .execute()
            )
            return result
        except errors.HttpError:
            return None

    def get_gcp_object(self, log_data: Dict) -> Optional[Dict]:
        try:
            if "response" not in log_data["protoPayload"]:
                return None
            labels_ = log_data["resource"]["labels"]
            service = labels_["service_name"]
            service = self._get_resource(log_data["resource"]["projectId"], service)
            return service
        except Exception:
            return None

    def label_all(self, project_id):
        # LIST ALL CLOUD RUN SERVICES
        # with timing(f"label_all({type(self).__name__}) in {project_id}"):
        page_token = None
        try:
            while True:
                response = self._google_api_client().projects().locations().services().list(parent=f"projects/{project_id}/locations/us-central1", pageToken=None).execute()
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
            # aaaa-mm
            is_create = is_create.split("-")[0] + "-" + is_create.split("-")[1]
            is_location = service_name.split("/")[3]
            creator = gcp_object["creator"]	
            creator = correctLabel(creator)

            # ADICIONAR CRIADOR ENTRE OUTROS LABELS
            

            # IF DONT HAVE LABELS
            if not service_body.get("labels"):
                service_body["labels"] = {}
            prefix = "exyon_"
            # ADD LABELS
            service_body["labels"][f'cloud-run'] = is_name
            service_body["labels"][f'ano-mes'] = is_create
            service_body["labels"][f'{prefix}location'] = is_location
            service_body["labels"][f'{prefix}create_by'] = creator
            
            self._google_api_client().projects().locations().services().patch(
                name=f"projects/{project_id}/locations/{is_location}/services/{is_name}",
                body=service_body,
            ).execute()

        except errors.HttpError as e:
            if "SERVICE_STATUS_UNSPECIFIED" in gcp_object.get("status", {}):
                logging.exception("Cloud Run service is not fully deployed yet, which is why we do not label it on-demand in the usual way")
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