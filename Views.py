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
    print('\nFOUND IN OBJECT TYPES:\n')
    print('ID CODE\t\tOBJECT TYPE\t\tTITLE\t\tDATA\t\tCONFIRMED\n')
    for i in source:  # loops records in source
        try:
            # print(len(i["data"]))
            if len(i["data"]) == 37:
                title = title_reader(i["data"])[0:-1]
                print(i["id"], '\t', i["object_type"], '\t', title, '\t', i["data"], '\t', i["confirmed"])
            else:
                title = i['data']
                if i['object_type'] == 'link':
                    print(i["id"], '\t', i["object_type"], '\t', i["object_id1"], '\t', i["object_id2"], '\t',
                          i["data"], '\t', i["confirmed"])
        except KeyError:
            # print('Not valid keyword in', i)
            return
        finally:
            pass
    return True


def clear_screen():
    os.system(command='clear')


def title_reader(filename: str):
    with open(file=filename, mode='r', encoding='utf8') as f:  # opens data file to read
        title = f.readline()  # reads first line in file (Header)
    return title


if __name__ == '__main__':
    obj = GDBResource(filename='db.json')
    database = obj.DBTree
    standard_view(db=database)
