from util.gcp_utils import add_loaded_lib
from google.cloud import compute_v1

add_loaded_lib("compute_v1")

project_id = "poc-iris3-exyon"

def list_all_vms(project_id):
    client = compute_v1.InstancesClient()
    disks_client = compute_v1.DisksClient()

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

        # Listar os dados dos discos da VM
        for disk in response.disks:
            disk_request = compute_v1.GetDiskRequest(project=project_id, zone="us-central1-c", disk=disk.device_name)
            disk_response = disks_client.get(disk_request)
            image = disk_response.source_image.split('/')[-1]
            print(f"Image: {image}")
            

list_all_vms(project_id)
