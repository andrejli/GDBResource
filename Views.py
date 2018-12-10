from DataStructure import GDBResource
import os


def standard_view(db=None):
    """ method finds object type and list all to screen
    :param db: source to dtabase view
    :return: list of found records in source
    """
    clear_screen()
    print("GRAPH DATABASE V1 - STANDARD VIEW ")
    source = db  # use other defined source as selection etc.
    print('\nFOUND IN OBJECT TYPES:\n')  # TODO Move to views
    print('ID CODE\t\tOBJECT TYPE\t\tTITLE\t\tDATA\t\tCONFIRMED\n')
    for i in source:  # loops records in source
        try:
            # print(len(i["data"]))
            if len(i["data"]) == 37:
                title = title_reader(i["data"])[0:-1]  # TODO
            else:
                title = i["data"]
            print(i["id"], '\t', i["object_type"], '\t', title, '\t', i["data"], '\t', i["confirmed"])  # print record to screen
        except KeyError:
            # print('Not valid keyword in', i)
            return
        finally:
            pass
    return True


def clear_screen():
    os.system(command='clear')


def title_reader(filename: str):
    with open(file=filename, mode='r', encoding='utf8') as f:
        title = f.readline()
    return title


if __name__ == '__main__':
    obj = GDBResource(filename='db.json')
    database = obj.DBTree
    standard_view(db=database)
