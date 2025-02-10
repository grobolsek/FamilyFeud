import pickle


def pickle_data(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)


def unpickle_data(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)