import json

settings_file = 'settings.json'

# protocol specific ending
MESSAGE_ENDING = '\x00'


def read_json(path):
    """
    Returns the dictionary contained in the given .json file
    :param path: String specifying the path
    :return: Dictionary representing the .json's content
    """
    with open(path, 'r') as json_file_handle:
        return dict(json.load(json_file_handle))


def get_settings_dict(key=None):
    """
    Returns the dictionary's value for a specific key contained in the settings file if a key is provided
    else the whole settings dictionary
    :param key: String specifying a key in the settings file
    :return: Content of settings file or value of a key in the settings file
    """
    return read_json(settings_file).get(key) if key else read_json(settings_file)


def get_server_settings(key=None):
    """
    Returns the dictionary's value for a specific key contained in the server dictionary if a key is provided
    else the whole server dictionary
    :param key: String specifying a key in the server dictionary
    :return: Content of server dictionary or value of a key in the server file
    """
    return get_settings_dict('server').get(key) if key else get_settings_dict('server')


def get_client_settings(key=None):
    """
    Returns the dictionary's value for a specific key contained in the client dictionary if a key is provided
    else the whole client dictionary
    :param key: String specifying a key in the client dictionary
    :return: Content of server dictionary or value of a key in the client dictionary
    """
    return get_settings_dict('client').get(key) if key else get_settings_dict('client')


def get_common_settings(key=None):
    """
    Returns the dictionary's value for a specific key contained in the common dictionary if a key is provided
    else the whole common dictionary
    :param key: String specifying a key in the common dictionary
    :return: Content of common dictionary or value of a key in the common dictionary
    """
    return get_settings_dict('common').get(key) if key else get_settings_dict('common')


def reformat_json():
    """
    Reads the settings file and saves it with a better readable format
    """
    json_content = read_json(settings_file)
    with open(settings_file, 'w') as write_handle:
        json.dump(json_content, write_handle, indent=4)


if __name__ == "__main__":
    reformat_json()
