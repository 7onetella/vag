

def get_service_and_group(name: str):
    tokens = name.split('-')

    service = '-'.join(tokens[:-1])
    group = tokens[-1]
    return service, group