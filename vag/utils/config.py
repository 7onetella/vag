import configparser


def read(file_path, debug=False):
    data = {}
    envs = {}

    config = configparser.ConfigParser()
    config.read(file_path)
    section = config.sections()[0]
    for key in config[section]:
        val = config[section][key]
        if key.startswith('env.'):
            key = key.replace('env.', '')
            envs[key.upper()] = val
        else:
            data[key] = val

    data['envs'] = envs
    if debug:
        print(data)

    return data
