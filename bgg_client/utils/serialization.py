import pickle


SNAPSHOT_PATH = 'snapshot'


def dump_struct(obj, filename, root_dir=SNAPSHOT_PATH):
    with open(root_dir + '/' + filename, 'wb') as output_stream:
        pickle.dump(obj, output_stream)

def load_struct(filename, root_dir=SNAPSHOT_PATH):
    with open(root_dir + '/' + filename, 'rb') as input_stream:
        return pickle.load(input_stream)
