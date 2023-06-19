import logging
from typing import Dict, Optional

from googleapiclient import errors
import datetime
from plugin import Plugin
from util.utils import log_time, timing
# from plugins.decorator import list_audit_logs


class Cloudsql(Plugin):
    @staticmethod
    def _discovery_api():
        return "sqladmin", "v1beta4"

    @staticmethod
    def method_names():
        return ["cloudsql.instances.create"]

    @classmethod
    def _cloudclient(cls, _=None):
        logging.info("_cloudclient for %s", cls.__name__)
        raise NotImplementedError(
            "There is no Cloud Client library for " + cls.__name__
        )

    @staticmethod
    def is_labeled_on_creation() -> bool:
        """
        Labels cannot be applied to CloudSQL during its long initialization phase.

        Why:
            During initialization of CloudSQL Instance, 3 log messages arrive (within 5 sec of each other)
            At the first two, the CloudSQL Instance does not exist, and at the third, it is still PENDING.
        How:
            As an alternative, maybe use Cloud Tasks instead of Pubsub to allow delay.
        """
        return False

    def _gcp_name(self, gcp_object):
        """Method dynamically called in generating labels, so don't change name"""
        return self._name_no_separator(gcp_object)

    def _gcp_region(self, gcp_object):
        """Method dynamically called in generating labels, so don't change name"""
        try:
            return gcp_object["region"].lower()
        except KeyError:
            logging.exception("")
            return None

    def _get_resource(self, project_id, name):
        try:
            result = (
                self._google_api_client()
                .instances()
                .get(project=project_id, instance=name)
                .execute()
            )
            return result
        except errors.HttpError:
            logging.exception("")
            return None

    def get_gcp_object(self, log_data: Dict) -> Optional[Dict]:
        try:
            if "response" not in log_data["protoPayload"]:
                return None
            labels_ = log_data["resource"]["labels"]
            database_id = labels_["database_id"]
            instance = database_id[database_id.rfind(":") + 1 :]
            instance = self._get_resource(labels_["project_id"], instance)
            return instance
        except Exception:
            logging.exception("")
            return None

    def label_all(self, project_id):
        with timing(f"label_all({type(self).__name__}) in {project_id}"):
            page_token = None
            while True:
                response = (
                    self._google_api_client()
                    .instances()
                    .list(
                        project=project_id,
                        pageToken=page_token,
                        # Filter supported, but syntax not OK. We get this message: "Field not found. In
                        # expression labels.iris_name HAS *, At field labels ."
                    )
                    .execute()
                )

                if "items" not in response:
                    return
                for database_instance in response["items"]:
                    try:
                        self.label_resource(database_instance, project_id)
                    except Exception:
                        logging.exception("")
                if "nextPageToken" in response:
                    page_token = response["nextPageToken"]
                else:
                    return

    @log_time
    def label_resource(self, gcp_object, project_id):
        # Cria o objeto de serviço do Cloud SQL usando o Discovery
        from googleapiclient.discovery import build
        service = build("sqladmin", "v1beta4")

        # Lista as instancias do Cloud SQL
        request = service.instances().list(project=project_id)

        while request is not None:
            response = request.execute()

            for instance in response["items"]:
                name = instance["name"]
                location = instance["region"]
                databasev = instance["databaseInstalledVersion"]
                create = instance["createTime"]

                # Trata o valor da data de criação
                create = create.split("T")[0]
                # TRANSFORMA A DATA EM ANO-MES
                create = create.split("-")[0] + "-" + create.split("-")[1]
                

                # Converte para letras minúsculas
                name = name.lower()
                location = location.lower()
                databasev = databasev.lower()

                print("name: ", name)
                print("location: ", location)
                print("databasev: ", databasev)

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
                project_id = "poc-iris3-exyon"
                filter_key = "cloudsql.instances.create"
                client = logging.Client(project=project_id)

                # Defina a data limite para 30 dias atrás a partir da data atual
                data_limite = datetime.datetime.now() - datetime.timedelta(days=30)

                # Formate a data limite no formato adequado
                data_limite_formatada = data_limite.strftime("%Y-%m-%dT%H:%M:%SZ")

                # Use o filtro para buscar os logs de auditoria "cloudsql.instances.create" para o recurso "labpoclabel" criados nos últimos 30 dias
                filtro = f'protoPayload.methodName="{filter_key}" AND timestamp>="{data_limite_formatada}" AND protoPayload.authorizationInfo.resourceAttributes.name:"labpoclabel"'
                entries = client.list_entries(filter_=filtro)

                for entry in entries:
                    # Acesse as informações do registro de log no objeto entry
                    
                    payload_dict = dict(entry.payload)
                    
                    # Acesse as informações do registro de log no dicionário payload_dict
                    if 'authenticationInfo' in payload_dict:
                        principal_email = payload_dict['authenticationInfo'].get('principalEmail')
                        principal_email = correctLabel(principal_email)
                    print(principal_email)

                # Define as labels
                labels = {
                    "cloud-sql": name,
                    "custo-cloud-sql": name,
                    "exyon_location": location,
                    "bd": databasev,
                    "ano-mes": create,
                    "exyon_created_by": principal_email
                }

                # Obtém a versão atual das configurações da instância
                settings_version = instance["settings"]["settingsVersion"]

                # Obtém o nível (tier) atual da instância
                tier = instance["settings"]["tier"]

                # PATCH
                try:
                    # Atualiza as labels da instância
                    request = service.instances().patch(
                        project=project_id,
                        instance=name,
                        body={"settings": {"userLabels": labels}},
                    )
                    response = request.execute()
                except:
                    logging.info("A instância %s não foi atualizada, ela se encontra desligada", name)
                    pass

            # Continua para a próxima página de resultados, se houver
            request = service.instances().list_next(previous_request=request, previous_response=response)
