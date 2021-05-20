import requests
import os
import sys

def get_ip_port(job_name: str, group: str, debug: bool):
    alloc = get_allocation(job_name, group, debug)

    ip = alloc['Resources']['Networks'][0]['IP']
    dynamic_ports = alloc['Resources']['Networks'][0]['DynamicPorts']
    port = ''
    for p in dynamic_ports:
        if p['Label'] == 'ssh':
            port = p['Value']
            break
    
    return ip, port


def get_version(job_name: str, group: str, debug: bool):
    if debug:
        print(f'job_name = {job_name}, group = {group}')
    job = get_job(job_name, debug)
    if job is None:
        return '1.0.0'

    task_groups = job['TaskGroups']
    for task_group in task_groups:
        task_group_name = task_group['Name']
        if task_group_name == group:
            image = task_group['Tasks'][0]['Config']['image']
            if debug:
                print(image)
            version = image[image.rfind(':')+1:]
            return version
    return ''


def get_job(job_name: str, debug: bool):
    nomad_addr = os.getenv('NOMAD_ADDR')
    if not nomad_addr:
        print('missing $NOMAD_ADDR environment variable')
        sys.exit(1)

    job_api_url = f'{nomad_addr}/v1/job/{job_name}'
    if debug:
        print(job_api_url)
    
    response = requests.get(job_api_url)
    if response:
        job = response.json()
        if debug:
            print(job)
        return job
    return None


def get_allocation(job_name: str, group: str, debug: bool):
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
        task_group = a['TaskGroup']
        if debug:
            print(f'task_group = {task_group}')

        if not task_group == group:
            continue

        task_states = a['TaskStates']
        if 'container' in task_states: 
            task_state = task_states['container']['State']
            if task_state == 'running':
                alloc_id = a['ID']
        else:
            # for backwards compatibility, remove this after containers are redployed
            if f'{job_name}-service' in task_states:
                task_state = task_states['{job_name}-service']['State']
                if task_state == 'running':
                    alloc_id = a['ID']

    if debug:
        print(f'alloc_id = {alloc_id}')

    alloc = requests.get(f'{nomad_addr}/v1/allocation/{alloc_id}').json()
    if debug:
        print(alloc)    
    return alloc

# /Job/TaskGroups[0]/Tasks[0]/Config/image