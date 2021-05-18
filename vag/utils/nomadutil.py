import requests
import os
import sys

def get_ip_port(job_name: str, debug: bool):
    alloc = get_allocation(job_name, debug)

    ip = alloc['Resources']['Networks'][0]['IP']
    dynamic_ports = alloc['Resources']['Networks'][0]['DynamicPorts']
    port = ''
    for p in dynamic_ports:
        if p['Label'] == 'ssh':
            port = p['Value']
            break
    
    return ip, port


def get_version(job_name: str, debug: bool):
    alloc = get_allocation(job_name, debug)

    image = alloc['Job']['TaskGroups'][0]['Tasks'][0]['Config']['image']
    if debug:
        print(image)
    version = image[image.rfind(':')+1:]
    return version


def get_allocation(job_name: str, debug: bool):
    nomad_addr = os.getenv('NOMAD_ADDR')
    if not nomad_addr:
        print('missing $NOMAD_ADDR environment variable')
        sys.exit(1)

    allocations_api_url = f'{nomad_addr}/v1/job/{job_name}/allocations'
    if debug:
        print(allocations_api_url)
        
    allocations = requests.get(allocations_api_url).json()
    if debug:
        print(allocations)

    alloc_id = ''
    for a in allocations:
        if a['TaskStates'][f'{job_name}-service']['State'] == 'running':
            alloc_id = a['ID']

    if debug:
        print(f'alloc_id = {alloc_id}')

    alloc = requests.get(f'{nomad_addr}/v1/allocation/{alloc_id}').json()
    if debug:
        print(alloc)    
    return alloc

# /Job/TaskGroups[0]/Tasks[0]/Config/image