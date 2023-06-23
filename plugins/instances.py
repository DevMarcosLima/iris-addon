import logging
import threading
from functools import lru_cache
from typing import Dict, Optional, List

from googleapiclient import errors

from gce_base.gce_zonal_base import GceZonalBase
from util import gcp_utils
from util.gcp_utils import add_loaded_lib
from util.utils import log_time

import datetime

class Instances(GceZonalBase):
    __lock = threading.Lock()

    @staticmethod
    @lru_cache(maxsize=1)
    def _create_cloudclient():

        logging.info("_cloudclient for %s", "Instances")
        # Local import to avoid burdening AppEngine memory.
        # Loading all Cloud Client libraries would be 100MB  means that
        # the default AppEngine Instance crashes on out-of-memory even before actually serving a request.
        from google.cloud import compute_v1

        add_loaded_lib("compute_v1")
        return compute_v1.InstancesClient()

    @classmethod
    def _cloudclient(cls, _=None):
        with cls.__lock:
            return cls._create_cloudclient()

    @staticmethod
    def method_names():
        return ["compute.instances.insert", "compute.instances.start"]

    def _gcp_instance_type(self, gcp_object: dict):
        """Method dynamically called in generating labels, so don't change name"""
        try:
            machine_type = gcp_object["machineType"]
            ind = machine_type.rfind("/")
            machine_type = machine_type[ind + 1 :]
            return machine_type
        except KeyError:
            logging.exception("")
            return None

    def _list_all(self, project_id, zone) -> List[Dict]:
        # Local import to avoid burdening AppEngine memory.
        # Loading all Cloud Client libraries would be 100MB  means that
        # the default AppEngine Instance crashes on out-of-memory even before actually serving a request.
        from google.cloud import compute_v1

        add_loaded_lib("compute_v1")
        page_result = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
        return self._list_resources_as_dicts(page_result)

    def _get_resource(self, project_id, zone, name) -> Optional[Dict]:
        try:
            # Local import to avoid burdening AppEngine memory. Loading all
            # Client libraries would be 100MB  means that the default AppEngine
            # Instance crashes on out-of-memory even before actually serving a request.
            from google.cloud import compute_v1

            add_loaded_lib("compute_v1")
            request = compute_v1.GetInstanceRequest(
                project=project_id, zone=zone, instance=name
            )

            return self._get_resource_as_dict(request)
        except errors.HttpError:
            logging.exception("")
            return None

    @log_time
    def label_resource(self, gcp_object, project_id):
        with self._write_lock:
            labels = self._build_labels(gcp_object, project_id)
            if labels is None:
                return

            zone = self._gcp_zone(gcp_object)

            # CREATE DATE
            create = gcp_object["creationTimestamp"]
            create = create.split("T")[0]
            # TRANFORMAR EM ANO-MES
            create = create.split("-")[0] + "-" + create.split("-")[1]

            if create:
                labels["labels"]["ano-mes"] = create

            from google.cloud import compute_v1
            client = compute_v1.InstancesClient()
            disks_client = compute_v1.DisksClient()
            zoneSearch = labels["labels"]["exyon_zone"]
            logging.warning(f"zoneSearch: {zoneSearch}")
            # Use a paginação para recuperar todas as VMs
            request = compute_v1.ListInstancesRequest(project=project_id, zone=zoneSearch)
            response = client.list(request)

            # Itere sobre as VMs retornadas
            for vm in response.items:
                # GET INFO ABOUT VM
                request = compute_v1.GetInstanceRequest(
                    project=project_id, zone=zoneSearch, instance=vm.name
                )
                response = client.get(request)

                # Listar os dados dos discos da VM
                for disk in response.disks:
                    disk_request = compute_v1.GetDiskRequest(project=project_id, zone=zoneSearch, disk=disk.device_name)
                    disk_response = disks_client.get(disk_request)
                    image = disk_response.source_image.split('/')[-1]
                    print(f"Image: {image}")
                    labels["labels"]["so"] = correctLabel(image)

            
            # DELETE ["labels"]["exyon_name"] AND ADD ["labels"]["vm"]
            
            nameVM = labels["labels"].pop("exyon_name", None)
            
            # beta.compute.instances.insert
            from google.cloud import logging

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
            
            filter_key = "beta.compute.instances.insert"
            
            client = logging.Client(project=project_id)

            # Defina a data limite para 30 dias atrás a partir da data atual
            data_limite = datetime.datetime.now() - datetime.timedelta(days=30)

            # Formate a data limite no formato adequado
            data_limite_formatada = data_limite.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Use o filtro para buscar os logs de auditoria "cloudsql.instances.create" para o recurso "labpoclabel" criados nos últimos 30 dias
            filtro = f'protoPayload.methodName="{filter_key}" AND timestamp>="{data_limite_formatada}" AND protoPayload.request.name:"{nameVM}"'
            entries = client.list_entries(filter_=filtro)

            for entry in entries:
                # Acesse as informações do registro de log no objeto entry
                
                payload_dict = dict(entry.payload)
                
                # Acesse as informações do registro de log no dicionário payload_dict
                if 'authenticationInfo' in payload_dict:
                    principal_email = payload_dict['authenticationInfo'].get('principalEmail')
                    principal_email = correctLabel(principal_email)
                else:
                    principal_email = "null"
                print(principal_email)
                
            labels["labels"]["exyon_create_by"] = principal_email
            labels["labels"]["vm"] = nameVM
            labels["labels"]["custo-vm"] = nameVM


            self._batch.add(
                self._google_api_client()
                .instances()
                .setLabels(
                    project=project_id,
                    zone=zone,
                    instance=gcp_object["name"],
                    body=labels,
                ),
                request_id=gcp_utils.generate_uuid(),
            )
            # Could use the Cloud Client as follows , but that apparently that does not support batching
            #  compute_v1.SetLabelsInstanceRequest(project=project_id, zone=zone, instance=name, labels=labels)
            self.counter += 1
            if self.counter >= self._BATCH_SIZE:
                self.do_batch()


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