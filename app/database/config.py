from configparser import ConfigParser

import os


def config(filename=str(os.path.abspath('app/database/database.ini')), section='postgresql'):
    """Read database.ini file and return a dictionary"""

    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql from file
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
