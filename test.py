from util.gcp_utils import add_loaded_lib
from google.cloud import compute_v1

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

        # Obtenha o tipo de máquina da VM
        machine_type = response.machine_type.split('/')[-1]
        print(f"Machine Type: {machine_type}")

        # Obtenha informações sobre o sistema operacional da VM
        image = response.disks[0].initialize_params.source_image.split('/')[-1]
        os_info = "Linux" if "debian" in image.lower() else "Windows" if "windows" in image.lower() else "N/A"
        print(f"Operating System: {os_info}")

list_all_vms(project_id)
