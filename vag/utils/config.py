import configparser


def read(file_path, debug=False):
    data = {}
    envs = {}
    tags = []

    config = configparser.ConfigParser()
    config.read(file_path)
    section = config.sections()[0]
    for key in config[section]:
        val = config[section][key]

        if key.startswith('env.'):
            key = key.replace('env.', '')
            envs[key.upper()] = val
            continue

        if key.startswith('tag.'):
            # tag.1 = urlprefix-www.example.com/signin  
            # tag.2 = urlprefix-www.example.com/signup
            tags.append(val) 
            continue
        
        data[key] = val

    data['envs'] = envs
    data['tags'] = tags
    if debug:
        print(data)

    return data
