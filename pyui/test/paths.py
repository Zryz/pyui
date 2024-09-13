import os, json

HOME_DIR = os.path.join(os.path.expanduser('~'), ".pyui")
TEST_FILE = os.path.join(HOME_DIR, 'test.json')

def gen_test_file():
    if not os.path.exists(HOME_DIR):
        os.makedirs(HOME_DIR)
    if not os.path.exists(TEST_FILE):
        with open(TEST_FILE, 'w') as file:
            file.write('')

def gen_files(locs:dict):
    for directory, file in locs.items():
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(file):
            with open(file, 'w') as file:
                file.write('')

def check_for_file(file)->bool:
    if os.path.isfile(file) and os.path.getsize(file) > 0:
        return True
    else:
        return False
    
def dump_object(object):
    if check_for_file(TEST_FILE):
        z = json.loads(TEST_FILE)
        q = json.dumps(object)
        z.update(q)
    else:
        iz = object
    dump_data(TEST_FILE, z)
    
def join_paths(*paths):
    return os.path.join(HOME_DIR, *paths)

    #Load data from a file
def load_data(file)->json:
    if os.path.getsize(file) == 0: return
    with open(file, 'r') as local:
        return json.load(local)

def dump_data(file, data=None):
    with open(file, 'w') as file:
        json.dump(data, file)
