"""
Basic skeleton of a mitmproxy addon.

Run as follows: mitmproxy -s addon.py
"""
import logging
import json
import time
import random

from mitmproxy import http
from datetime import datetime

resources = {}
project_iam_policies = {}
compute_operations = {}

class TerraFaker:
  def __init__(self) -> None:
    self.num_count = 0

  def request(self, flow: http.HTTPFlow) -> None:
    fr = flow.request
    frh = flow.request.headers
    if 'user-agent' in frh and 'erraform' in frh['user-agent']:
      if "googleapis.com" in fr.host:
        resp = GoogleFaker().parse_terraform_google(flow)
        if resp:
         self.respond_to_terraform(flow, resp)
      else:
        logging.info("Skipping processing for: "+ fr.url)


  def respond_to_terraform(self, flow: http.HTTPFlow, body: dict) -> None:
      payload_bytes = json.dumps(body).encode('utf-8')
      flow.response = http.Response.make(
        200,
        payload_bytes,
        {"Content-Type": "application/json"},
      )
      logging.info(flow.response.content)
      logging.info("")

  # Called when the addon shuts down
  def done(self):
    # Collect all resources to assets list
    assets = []
    for k, v in resources.items():
        asset = {}
        asset["name"] = v.get("name")
        asset["type"] = k.split(":")[0]
        asset["action"] = "UPSERT"
        asset["update_time"] = datetime.now().isoformat()
        asset["data"] = v
        assets.append(asset)
    
    # Write out json assets created to a file
    logging.info("writing assets to file...")
    print(json.dumps(assets, indent=2))
    with open('changeset.json', 'w') as outfile:
      changeset_data = {
        "type": "changeset",
        "date": datetime.now().isoformat(),
        "assets": assets
      }
      json.dump(changeset_data, outfile)

    logging.info("Done")

class GoogleFaker:
  def __init__(self) -> None:
    self.num_count = 0

  def parse_terraform_google(self, flow: http.HTTPFlow) -> str:
    fr = flow.request
    if not self.is_supported_service(fr.host):
      return None

    if fr.host == "iam.googleapis.com":
      return GoogleIamFaker().parse(flow)
    
    if fr.host == "cloudresourcemanager.googleapis.com":
      return GoogleCrmFaker().parse(flow)

    if fr.host == "compute.googleapis.com":
      return GoogleComputeFaker().parse(flow)


  def is_supported_service(self, host: str) -> bool:
    supported_services = ['iam', 'compute', 'cloudresourcemanager']
    # Parse host into subdomain and domain
    subdomain = host.split(".")[0]
    if subdomain in supported_services:
      return True

    return False

class GoogleCrmFaker:
  def __init__(self) -> None:
    self.num_count = 0

  def parse(self, flow: http.HTTPFlow) -> dict:
    fr = flow.request
    pcs = flow.request.path_components

    # Get the IAM policy for a project
    if fr.method == "POST" and pcs[0] == "v1" and pcs[1] == "projects" and ":getIamPolicy" in pcs[2]:
      # parse the project-id from the path componet
      project_id = pcs[2].split(":")[0]
      # if we've already created an IAM policy for this project, return it
      if project_id in project_iam_policies:
        logging.info("Fetching IAM policy for project: "+ project_id)
        return project_iam_policies[project_id]
      # else allow the request to go through
      else:
        logging.info("Storing IAM policy for project: "+ project_id)
        return None
    elif fr.method == "POST" and pcs[0] == "v1" and pcs[1] == "projects" and ":setIamPolicy" in pcs[2]:
      # parse the project-id from the path componet
      project_id = pcs[2].split(":")[0]
      # parse the iam policy from the request body
      policy = fr.json()
      policy['version'] = 1
      policy['etag'] = "BwYR2wZdArY="
      project_iam_policies[project_id] = policy.get('policy')

      resources["gcp_cloudresourcemanager_iam_policy:"+ project_id] = policy.get('policy')
      resources["gcp_cloudresourcemanager_iam_policy:"+ project_id]["name"] = "projects/"+ project_id
      # if we've already created an IAM policy for this project, return it
      if project_id in project_iam_policies:
        logging.info("Returning IAM policy for project: "+ project_id)
        return project_iam_policies[project_id]
      # else return an error
      else:
        return {}
    else:
      return {}

class GoogleIamFaker:

  def __init__(self) -> None:
    self.num_count = 0

  def parse(self, flow: http.HTTPFlow) -> dict:
    fr = flow.request

    pcs = flow.request.path_components
    # Create a GCP Service Account
    if fr.method == "POST" and pcs[0] == "v1" and pcs[1] == "projects" and pcs[3] == "serviceAccounts":
      resource = self.parse_post_service_account(flow)
      return self.create_service_account(resource)
    # Get a GCP Service Account
    elif fr.method == "GET" and pcs[0] == "v1" and "iam.gserviceaccount.com" in pcs[4]:
      resource = self.parse_get_service_account(flow)
      return self.get_service_account(resource)
    else:
      return {}

  def parse_post_service_account(self, flow: http.HTTPFlow) -> dict:
    pcs = flow.request.path_components
    data = {}
    if flow.request.method == "POST":
      data = flow.request.json()

    uniqueId = str(random.randint(100000000000000000000, 999999999999999999999))
    project_id = "no-project-id"
    displayName = ""
    description = ""
    email = ""

    if "projects" in pcs and "serviceAccounts" in pcs:
      project_id = pcs[2]

    if data.get("accountId"):
      email = data.get("accountId") +"@"+ project_id + ".iam.gserviceaccount.com"

    if data.get("serviceAccount").get("displayName"):
      displayName = data.get("serviceAccount").get("displayName")

    if data.get("serviceAccount").get("description"):
      description = data.get("serviceAccount").get("description")

    resource_name = "projects/" + project_id + "/serviceAccounts/" + email

    resource = {
      "name": resource_name,
      "email": email,
      "projectId": project_id,
      "displayName": displayName,
      "description": description,
      "etag": "MDEwMjE5MjA=",
      "disabled": False,
      "oauth2ClientId": uniqueId,
      "uniqueId": uniqueId
    }

    return resource
  
  def parse_get_service_account(self, flow: http.HTTPFlow) -> dict:
    pcs = flow.request.path_components
    return {
      "name": "projects/" + pcs[2] + "/serviceAccounts/" + pcs[4]
    }

  def create_service_account(self, resource: dict) -> dict:
    resources["gcp_iam_serviceaccount:"+ resource.get("name")] = resource
    return resource

  def get_service_account(self, resource: dict) -> dict:
    resource = resources.get("gcp_iam_serviceaccount:"+ resource.get("name"))
    return resource

class GoogleComputeFaker:
  def __init__(self) -> None:
    self.num_count = 0

  def parse(self, flow: http.HTTPFlow) -> dict:
    fr = flow.request
    pcs = flow.request.path_components

    # Create a GCP Compute Instance
    if fr.method == "POST" and pcs[0] == "compute" and pcs[1] == "v1" \
      and pcs[2] == "projects" and pcs[4] == "zones" and pcs[6] == "instances":

      logging.info("Creating a GCP Compute Instance")
      # parse and store the compute instance, return the operation id
      instance_operation_id = self.parse_post_compute_instance(flow)

      # return the create instance operation
      return self.get_instance_operation(instance_operation_id)

    # Get a GCP Compute Instance Operation
    elif fr.method == "GET" and pcs[0] == "compute" and pcs[1] == "v1" \
      and pcs[2] == "projects" and pcs[4] == "zones":
      if len(pcs) > 6 and pcs[6] == "operations":
        instance_operation_id = self.parse_compute_instance_operation_for_id(flow)
        return self.get_instance_operation(instance_operation_id)

      if len(pcs) > 6 and pcs[6] == "instances":
        logging.info("Get for GCP Compute Instance Detail")
        instance = self.get_instance_detail(flow)
        return instance

      if len(pcs) > 6 and pcs[6] == "disks":
        logging.info("Get for GCP Compute Instance Disk")
        return {}


    return None

  def get_instance_detail(self, flow: http.HTTPFlow) -> dict:
    fr = flow.request
    pcs = flow.request.path_components
    api_version = pcs[1]
    project_id = pcs[3]
    zone = pcs[5]
    vm_name = pcs[7]
    vm_url = "https://www.googleapis.com/compute/"+ api_version +"/projects/"+ project_id +"/zones/"+ zone +"/instances/"+ vm_name
    instance_detail = resources.get("gcp_compute_instance:"+ vm_url)

    return instance_detail

  def get_instance_operation(self, operation_id: str) -> dict:
    # return the operation by operation_id, advancing the state of the operation each time
    logging.info("Getting a GCP Compute Instance Operation: "+ operation_id)
    operation = compute_operations.get(operation_id)

    # if pending, change to done
    if operation.get("status") != "RUNNING" and operation.get("status") != "DONE":
      logging.info("Setting operation to DONE: "+ operation_id)
      operation["status"] = "DONE"
      operation["progress"] = 100
      operation["endTime"] = datetime.now().isoformat()

    return operation

  def parse_post_compute_instance(self, flow: http.HTTPFlow) -> dict:
    fr = flow.request
    pcs = flow.request.path_components
    api_version = pcs[1]
    project_id = pcs[3]
    zone = pcs[5]
    region = "-".join(zone.split("-")[0:2])
    vm_name = fr.json().get('name') or "no-vm-name"
    # parse the compute instance body from the request
    zone_url = "https://www.googleapis.com/compute/"+ api_version +"/projects/"+ project_id +"/zones/"+ zone
    vm_url = zone_url +"/instances/"+ vm_name

    vm_id = random.randint(1000000000000000000, 9999999999999999999)
    disk_size_gb = fr.json().get('disks')[0].get('initializeParams').get('diskSizeGb') or 10
    tags = fr.json().get('tags').get('items')
    can_ip_forward = fr.json().get('canIpForward')
    service_account_email = fr.json().get('serviceAccounts')[0].get('email')
    scopes = fr.json().get('serviceAccounts')[0].get('scopes')
    metadata_items = fr.json().get('metadata').get('items')
    machine_type = fr.json().get('machineType')
    machine_type_url = "https://www.googleapis.com/compute/v1/" + machine_type
    guest_os_features = [
      { "type": "UEFI_COMPATIBLE" },
      { "type": "VIRTIO_SCSI_MULTIQUEUE" },
      { "type": "GVNIC" },
      { "type": "SEV_CAPABLE" }
    ]
    architecture = fr.json().get('disks')[0].get('architecture')
    cpu_platform = "Intel Broadwell"

    instance_detail = {
     "kind": "compute#instance",
     "id": str(vm_id),
     "creationTimestamp": datetime.now().isoformat(),
     "name": vm_name,
     "tags": {
      "items": tags or [],
      "fingerprint": "pOiUF0UJfOw="
     },
     "machineType": machine_type_url,
     "status": "RUNNING",
     "zone": zone_url,
     "canIpForward": can_ip_forward or False,
     "networkInterfaces": [],
     "disks": [
      {
       "kind": "compute#attachedDisk",
       "type": "PERSISTENT",
       "mode": "READ_WRITE",
       "source": zone_url +"/disks/"+ vm_name,
       "deviceName": "persistent-disk-0",
       "index": 0,
       "boot": True,
       "autoDelete": True,
       "licenses": [
        "https://www.googleapis.com/compute/v1/projects/debian-cloud/global/licenses/debian-12-bookworm"
       ],
       "interface": "SCSI",
       "guestOsFeatures": guest_os_features or [],
       "diskSizeGb": disk_size_gb,
       "architecture": architecture
      }
     ],
     "metadata": {
      "kind": "compute#metadata",
      "fingerprint": "BFuQ-sDJdpk=",
      "items": metadata_items or []
     },
     "serviceAccounts": [
      {
       "email": service_account_email,
       "scopes": scopes or ["https://www.googleapis.com/auth/cloud-platform"]
      }
     ],
     "selfLink": vm_url,
     "scheduling": {
      "onHostMaintenance": "MIGRATE",
      "automaticRestart": True,
      "preemptible": False,
      "provisioningModel": "STANDARD"
     },
     "cpuPlatform": cpu_platform,
     "labelFingerprint": "42WmSpB8rSM=",
     "startRestricted": False,
     "deletionProtection": False,
     "shieldedInstanceConfig": {
      "enableSecureBoot": True,
      "enableVtpm": True,
      "enableIntegrityMonitoring": True
     },
     "shieldedInstanceIntegrityPolicy": {
      "updateAutoLearnPolicy": True
     },
     "fingerprint": "w465_wnrOho=",
     "lastStartTimestamp": datetime.now().isoformat()
    }

    network_interfaces = []
    interface_count = 0
    for req_interface in fr.json().get('networkInterfaces'):
      network = req_interface.get('network')
      network_name = network.split("/")[-1]
      interface = {
        "kind": "compute#networkInterface",
        "network": "https://www.googleapis.com/compute/v1/projects/"+ project_id +"/global/networks/"+ network_name,
        "subnetwork": "https://www.googleapis.com/compute/v1/projects/"+ project_id +"/regions/"+ region +"/subnetworks/"+ network_name,
        "networkIP": "10.0.0.0",
        "name": "nic"+ str(interface_count),
        "fingerprint": "o9wnSWdXEW4=",
        "stackType": "IPV4_ONLY",
        "nicType": "gVNIC"
      }
      access_configs = []
      if req_interface.get('accessConfigs')[interface_count].get('type') == "ONE_TO_ONE_NAT":
        access_config = {
          "kind": "compute#accessConfig",
          "type": "ONE_TO_ONE_NAT",
          "name": "external-nat",
          "natIP": "1.1.1.1",
          "networkTier": "PREMIUM"
        }
        access_configs.append(access_config)

      interface["accessConfigs"] = access_configs
      network_interfaces.append(interface)
      interface_count += 1

    instance_detail["networkInterfaces"] = network_interfaces

    # Store the compute instance as a resource
    resources["gcp_compute_instance:"+ vm_url] = instance_detail

    # parse the project-id and zone from the path componet
    operation_id = random.randint(1000000000000000000, 9999999999999999999)
    target_id = random.randint(1000000000000000000, 9999999999999999999)
    operation_name = "operation-compute-create-"+ project_id +"-"+ zone +"-"+ vm_name

    # Create a new compute operation in the state of pending
    zone_url = "https://www.googleapis.com/compute/"+ api_version +"/projects/"+ project_id +"/zones/"+ zone
    operation = {
     "kind": "compute#operation",
     "id": str(operation_id),
     "name": str(operation_name),
     "zone": str(zone_url),
     "operationType": "insert",
     "targetLink": vm_url,
     "targetId": str(target_id),
     "status": "PENDING",
     "user": "psychiac@psychiac.com",
     "progress": 0,
     "insertTime": datetime.now().isoformat(),
     "startTime": datetime.now().isoformat(),
     "endTime": datetime.now().isoformat(),
     "selfLink": zone_url +"/operations/"+ operation_name
    }
    logging.info("Storing operation in PENDING: "+ operation_name)
    compute_operations[operation_name] = operation

    # return the operation id
    return operation_name

  def parse_compute_instance_operation_for_id(self, flow: http.HTTPFlow) -> None:
    fr = flow.request
    pcs = flow.request.path_components

    project_id = pcs[3]
    zone = pcs[5]
    vm_name = fr.json().get('name') or "no-vm-name"

    operation_name = "operation-compute-create-"+ project_id +"-"+ zone +"-"+ vm_name

    return operation_name


addons = [TerraFaker()]