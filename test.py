from util.gcp_utils import add_loaded_lib
from google.cloud import compute_v1
from util import gcp_utils
from util.gcp_utils import add_loaded_lib

add_loaded_lib("compute_v1")

project_id = "poc-iris3-exyon"

def list_all_vms(project_id):
    client = compute_v1.InstancesClient()

    # Use a paginação para recuperar todas as VMs
    request = compute_v1.ListInstancesRequest(project=project_id, zone="us-central1-c")
    response = client.list(request)

    # Itere sobre as VMs retornadas
    for vm in response.items:
        # GET INFO ABOUT VM
        request = compute_v1.GetInstanceRequest(
            project=project_id, zone="us-central1-c", instance=vm.name
        )
        response = client.get(request)
        
        print(f"VM: {vm.name}")

        # Verifique cada disco associado à VM
        for disk in response.disks:
            # Verifique se há informações sobre o sistema operacional
            if disk.guest_os_features:
                for feature in disk.guest_os_features:
                    if feature.type == "VIRTIO_SCSI_MULTIQUEUE":
                        # Exemplo de verificação para uma determinada feature
                        print(f"Operating System: {feature.type}")
                        break
            else:
                print("Operating System information not available")
    
        os_name = feature.type
        # lower case
        os_name = os_name.lower()

        # ADD LABELS TO VM
        labels = {"labels": {"exyon_os": os_name}}
        client.add(
            .instances()
            .addLabel(
                project=project_id,
                zone=zone,
                instance=gcp_object["name"],
                body=labels,
            )
        ), request_id=gcp_utils.generate_uuid(),


list_all_vms(project_id)
