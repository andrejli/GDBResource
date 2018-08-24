import random
import os
import json
import re
import cmd
from CONFIG import AUTOSAVE


class GDBResource(object):
    """ Link based graph database to store data in memory and then commit to JSON file.
        Database has objects:
            :: db_root_record - master base key for blockchain encryption mechanism
            :: db_object_record - with parameters :: object_type =(Person, Asset, Phone, Car, etc.)
                                                :: data is bytearray containing data about object OR
                                                :: objects two ids of objects link is connecting OR
                                                :: multiple ids as a collection
                                                :: id identification number of object if None db generates new id
            :: DBObject link  - with parameters :: object_type: link
                                                          enc.link - encrypted link
                                                          collection
                                                          report
                                                          file

                                                :: id identification number of object if None db generates new id
    """
    def __init__(self, filename):
        """ Initialize method of GDBResource class
        :param filename: local file to store data
        """
        self.filename = filename  # define main file of database
        self.SALT = 'KNOWN SECRET'# is used with db_root_record to obtain BASE KEY
        self.KEY = [10, 234, 56, 67, 34, 67, 99]  # TODO Write Method to obtain KEY from ... server ???
        self.DBTree = list()  # defines empty DBTree list
        self.SELECTION = None  # selection of records is initiated as None
        self.load_all_from_json()
        # TODO write method to check integrity of database -
        print('DATABASE LOADED AND READY TO USE')

    # D A T A B A S E   O B J E C T S

    def db_root_record(self):
        """
         Defines data structure of root record and stores it to DBTree
        :return:
        """
        db_record = dict()  # defines as an empty dictionary
        id_code = 111111111  # id code of root record is always nine ones
        db_record['id'] = id_code  # writes id to dictionary
        db_record['object_type'] = 'root'
        db_record['relationships'] = self.analyze_database_structure()  # writes relationships to dictionary
        db_record['data'] = self.KEY  # TODO Generate or obtain 1800bytes key for encryption
        self.DBTree.append(db_record)  # append dict to DBTree
        return

    def db_object_record(self, object_type: str, data: str, id_code=None, confirmed=False):
        """
        Method defines data structure of record, adds record to DBTree
        and update root object
        :param object_type: person, asset, report, # TODO Add collections
        :param data: text string describe object
        :param id_code: unique random value integer stored between 100000000 and 999999999
        :param confirmed: Boolean value of confirmation
        :return:
        """
        db_record = dict()  # defines DBrecord as dict
        if id_code is not None:  # if id_code is not given
            db_record['id'] = id_code  # overrides generation of new id in loads and in specific cases
        else:  # if id_code is None DO:
            id_code = self.calculate_id()  # generate new id_code
            db_record['id'] = id_code  # store id in dict
        db_record['object_type'] = object_type  # store object_type in dict
        db_record['data'] = data  # store data in dict
        db_record['confirmed'] = confirmed
        self.DBTree.append(db_record)  # append dict to DBTree
        # REMOVE OLD root and generate NEW with added record
        for i in self.DBTree:  # loops thru DBTree
            if i['id'] == 111111111:  # if root is found DO:
                self.DBTree.remove(i)  # remove old root record
                self.db_root_record()  # add new root record to database with actualized data
        # INCREMENTAL SAVE WITH NEW OBJECT ADDED
        self.save_all_to_json()
        return

    def db_link_record(self, object1_id: int, object2_id: int, reverse=False, data=None, id_code=None, confirmed=False):
        """
        Method defines data structure of links between two objects, adds link to
        DBTree and update root object
        :param object1_id: integer number of first related object
        :param object2_id: integer number of second related object
        :param reverse: Boolean value of vector of relationship - if True arrow will be on both sides
        :param data: text string describe link
        :param id_code: unique random value integer stored between 100000000 and 999999999
        :param confirmed: Boolean value of confirmation
        :return:
        """
        db_record = dict()  # defines DBrecord as dict
        if id_code is not None:  # if id_code is not given
            db_record['id'] = id_code  # overrides generation of new id in loads and in specific cases
        else:  # if id_code is None DO:
            id_code = self.calculate_id()  # generate new id_code
            db_record['id'] = id_code  # store id in dict
        db_record['object_type'] = 'link'
        db_record['object_id1'] = object1_id  # store in dict
        db_record['object_id2'] = object2_id  #
        db_record['reverse'] = reverse
        db_record['data'] = data  # store data in dict
        db_record['confirmed'] = confirmed
        self.DBTree.append(db_record)  # append dict to DBTree

        # REMOVE OLD root and generate NEW with added record
        for i in self.DBTree:  # loops thru DBTree
            if i['id'] == 111111111:  # if root is found DO:
                self.DBTree.remove(i)  # remove old root record
                self.db_root_record()  # add new root record to database with actualized data
        # INCREMENTAL SAVE WITH NEW OBJECT ADDED
        self.save_all_to_json()
        return

    # S I M P L E   F I N D   M E T H O D S

    def full_match_id_find(self, id_code, db=None):
        """
        Finds fullmatch object with id for perimeter calculations and database internal needs
        :param id_code: id of object in integer form
        :param db: can override database to SELECTION or another source
        :return: list of ID ( database doesn't accept duplicity of ids!!!)
        """
        result = list()
        if db is None:  # if db is not defined DO:
            source = self.DBTree  # switch to default
        else:
            source = db  # else db is selection or other given source in memory
        for i in source:  # loops thru database to check all records
            # check records stored in [id]:
            if i['id'] == id_code:  # if id is found
                if id_code != 111111111:
                    print(i["id"], '\t', i["object_type"], '\t', i["data"], '\t', i["confirmed"])  # print record to screen
                result.append(i)  # append record to result dict
                return result

    def find_id(self, id_code: int, db=None):
        """
        Method to find id code value in objects, links and ids in fulltext
        :param id_code: integer value of id to search for
        :param db: defines value - default value will be in method set to DBTree
        :return: dict with OBJECTS, LINKS and OTHER findings
        """
        result = dict()  # define result as an empty dict
        result['OBJECTS'] = list()  # define result as an empty list
        result['LINKS'] = list()  # define result as an empty list
        result['OTHER'] = list()  # define result as an empty list
        source = self.DBTree  # setting default value of source
        if db is None:  # if db is not defined DO:
            source = self.DBTree  # switch to default
        else:
            source = db  # else db is selection or other given source in memory
        # SEARCHING ALL OBJECTS IN [ID] PART OF DICTIONARY
        print('\nFOUND IN OBJECTS:\n')  # find in objects:
        for i in source:  # loops thru database to check all records
            # check records stored in [id]:
            if i['id'] == id_code:  # if id is found
                print(i["id"], '\t', i["object_type"], '\t', i["data"], '\t', i["confirmed"])  # print record to screen
                result['OBJECTS'].append(i)  # append record to result dict

        # SEARCHING IN LINKS [OBJECT_ID1] AND [OBJECT_ID2] PART OF DICTIONARY
        print('\nFOUND IN LINKS:\n')  # find in objects:
        for i in source:  # loops thru database to check all records
            # check records stored in [id]:
            if i['object_type'] == 'link':
                if i['object_id1'] == id_code or i['object_id2'] == id_code:  # if id is found
                    print(i["id"], '\t', i["object_id1"], '\t', i["object_id2"], i["data"], '\t', i["confirmed"])
                    result['LINKS'].append(i)  # append record to result dict

        # SEARCHING IN ALL [DATA]
        print('\nFOUND FULLTEXT LINKS:\n')  # fulltext regex search in [data] part of dictionary
        for i in source:  # loops thru database to check all records
            # check links and collections stored in [data]:
            search = re.match(str(id_code), i['data'])  # regex match search in data string
            if search:  # if success DO
                print(i)  # print record to screen
                result['OTHER'].append(i)  # append record to result list
        if len(result['OBJECTS']) == 0 and len(result['LINKS']) == 0 and len(result['OTHER']) == 0:
            print('NOT FOUND')
        return result  # returns result dict


    def find_object_type(self, object_type: str, db=None):
        """ method finds object type and list all to screen
        :param object_type: object type(person, link, collection, report)
        :param db: source to search if None - default DBTree
        :return: list of found records in source
        """
        result = list()  # define result as an empty list
        if db is None:  # if db is not defined
            source = self.DBTree  # use default database
        else:
            source = db  # use other defined source as selection etc.
        print('\nFOUND IN OBJECT TYPES:\n')  #
        for i in source:  # loops records in source
            search = re.match(object_type, i['object_type'])  # regex match in [object_type] part of dictionary
            if search:  # if result
                print(i["id"], '\t', i["object_type"], '\t', i["data"], '\t', i["confirmed"])  # print record to screen
                result.append(i)  # append record to result dict
        if len(result) == 0:
            print('NOT FOUND')
        return result  # return result list

    def find_text(self, text: str, db=None):
        """
        Method searches text in string format in data values of all objects and links
        :param text: string value to search for
        :param db: source to search if None - default DBTree
        :return: list of finded records
        """
        result = list()  # define result as an empty list
        if db is None:  # if db is not given as parameter DO
            source = self.DBTree  # default defined database
        else:
            source = db  # if parameter db is given use it instead default
        print('\nFOUND IN OBJECTS AND LINKS:\n')  #
        for i in source:  # loops in db
            search = re.search(text, i['data'])  # search for fulltext
            if search:  # if result exists
                print(i)  # prints out to console
                result.append(i)  # append to result list
        if len(result) == 0:  # if result length is 0
            print('NOT FOUND')  # text was not found in database
        return result  # return list of records

    # S E L E C T  R E C O R D S

    def select_all(self):
        """ Method to select all values from DBTree and insert it into SELECTION"""
        self.SELECTION = self.DBTree  # defines SELECTION as copy of db
        print('\nSELECTION FROM DATABASE :\n')  # prints to console
        [print(i) for i in self.SELECTION]  # list all SELECTION to console
        return self.SELECTION  # return SELECTION database

    def add_id_to_selection(self, id_code: int):
        """
        Method to select all values from DBTree and insert it into SELECTION
        :param id_code: (9digit integer)
        :return:
        """
        if self.SELECTION is None:  # if SELECTION is default None DO
            self.SELECTION = list()  # define SELECTION as an empty list
        for i in self.DBTree:  # loops tru db
            if i['id'] == id_code:  # if id is equal DO
                self.SELECTION.append(i)  # append id to SELECTION
        print('\nSELECTION FROM DATABASE :\n')  # print to console
        [print(i) for i in self.SELECTION]  # list all objects and links in selection
        return

    def remove_id_from_selection(self, id_code: int):
        """
        Method removes id from SELECTION
        :param id_code: 9digit integer
        :return:
        """
        if self.SELECTION is not None:  # if SELECTION exists
            for i in self.SELECTION:  # loops SELECTION
                if i['id'] == id_code:  # if equal id is found DO
                    self.SELECTION.remove(i)  # remove id from SELECTION
            print('\nSELECTION FROM DATABASE :\n')  # prints to console
            [print(i) for i in self.SELECTION]  # list all records and links from SELECTION


    def drop_selection(self):
        """ Method to drop selection of records
        :return:
        """
        self.SELECTION = None  # defines SELECTION as None (default value)
        return


    # A D M I N  P R O C E D U R E S

    def init_new_database(self):
        """ Method to initialize new database.
        :return:
        """
        self.DBTree = list()  # drop old and make empty function
        # make new empty root record
        self.db_root_record()
        self.save_all_to_json()  # save it to instance db file
        return  #

    def drop_database(self):
        """ Method to drop all database
        :return:
        """
        [self.DBTree.remove(i) for i in self.DBTree] # remove all records
        self.save_all_to_json()  # save empty file
        cmd = 'rm ' + self.filename  # remove file from file system
        os.system(command=cmd)  # execute via os.system command  # TODO Use shutil module
        return

    def remove_id(self, id_code: int):
        result = self.full_match_id_find(id_code)
        if result is not False:
            print('RECORD FOUND')
            for i in self.DBTree:
                if i['id'] == id_code:
                    self.DBTree.remove(i)
                    print(f'OBJECT {id_code} REMOVED FROM DATABASE')

    def save_all_to_json(self):
        """ Export all records in DBTree to specified file
                :return: True if success
                """
        file = self.filename
        try:
            cmd = 'rm ' + file  # try to remove old saved file  # TODO Get Currently Working Directory
            os.system(command=cmd)  # execute system command via os.system
        except FileNotFoundError:  # exception handle
            print('FILE DOESNT EXIST YET  !!!')  # print msg
        finally:
            with open(file=file, mode='w') as f:  # open file as f
                # CONVERT DBtree to serializable data
                converted_dbtree = self.DBTree  # makes copy of DBTree function
                for i in converted_dbtree:  # loops thru dicts
                    i['data'] = str(i['data'])  # changes bytearrays to strings
                json.dump({'DBTree': converted_dbtree}, f, ensure_ascii=False, indent=4, sort_keys=True)  # dumps converted list to file
                print(f'SAVE RECORD TO JSON: {file}')  # print message
                return True  # return

    def load_all_from_json(self):
        """ Method to import all records from specified file to DBTree instance
                        :return: True if success
                                 False if rejected
                        """
        file = self.filename
        try:
            with open(file=file, mode='r') as f:  # open file as f
                converted_dbtree = json.load(f)  # TODO Move JSON data to DBTree
                [print(converted_dbtree['DBTree'][i]) for i in range(0, len(converted_dbtree['DBTree']))]
                self.DBTree = list()  # removes all data and import new from json
                for i in range(0, len(converted_dbtree['DBTree'])):
                    self.DBTree.append(converted_dbtree['DBTree'][i])
        except FileNotFoundError:
            self.init_new_database()
            print('NEW DATABASE WAS INITIALIZED')
        finally:
            print('DONE')
            return True  # return
#
#     # E X P O R T   I M P O R T   C O M M A N D S
#
#     def export_to_json(self, file: str):
#         """ Export all records in DBTree to specified file
#                 :return: True if success
#                 """
#         try:
#             cmd = 'rm ' + file  # try to remove old saved file
#             os.system(command=cmd)  # execute system command via os.system
#         except FileNotFoundError:  # exception handle
#             print('FILE DOESNT EXIST YET  !!!')  # print msg
#         finally:
#             with open(file=file, mode='w') as f:  # open file as f
#                 # CONVERT DBtree to serializable data
#                 converted_dbtree = self.DBTree  # makes copy of DBTree function
#                 for i in converted_dbtree:  # loops thru dicts
#                     i['data'] = str(i['data'])  # changes bytearrays to strings
#                 json.dump({'DBTree': converted_dbtree}, f)  # dumps converted list to file
#                 print(f'EXPORTED TO JSON: {file}')  # print message
#                 return True  # return
#
#     def import_from_json(self, file: str):
#         """ Method to import all records from specified file to DBTree instance
#                         :return: True if success
#                                  False if rejected
#                         """
#         with open(file=file, mode='r') as f:  # open file as f
#             converted_dbtree = json.load(f)  # loads json from file
#             [print(converted_dbtree['DBTree'][i]) for i in range(0, len(converted_dbtree['DBTree']))]
#             key = input(f'IMPORTED FROM JSON: {file} (y/n')  # TODO Make method to yes/no
#             if key == 'y':
#                 for i in range(0, len(converted_dbtree['DBTree'])):
#                     # TODO check duplicity of records
#                     self.DBTree.append(converted_dbtree['DBTree'][i])
#                     return True  # return
#             if key == 'n':
#                 return False

    # A N A L Y Z E R S  A N D  D A T A B A S E   S T A T I S T I C S

    def analyze_database_structure(self):
        """ Method to analyze structure of database
        :return: dict with all values of routes(root to object links), vectors (links) and objects.
        """
        result = dict()  # define variable as an empty dictionary
        objects = list()  # define variable as an empty list
        vectors = list()  # define variable as an empty list
        # collections = list()  # define variable as an empty list  # TODO Add collection
        record_result = list()  # define variable as an empty list
        # LOOP TO FIND ALL IDS IN DATA PART OF RECORD
        for i in self.DBTree:  # loops all values in DBTree
            collect_ids = re.findall(r'\d+\d+\d+\d+\d+\d+\d+\d+\d', str(i['data']))  # regex findall of 9digits numbers
            # collect_ids = list(filter(self.check_id_len, collect_ids))  # obsolete due regex refactoring TODO Test and remove
            collect_ids.append(i['id'])  # append id integer of record  # TODO check if not usefull in start of current loop
            if collect_ids:  # if exists DO
                record_result.append(collect_ids)  # append to record_result list
        # CHECK OBJECTS AND LINKS IN DBTREE
        for i in self.DBTree:
            if i['object_type'] == 'link':
                print('VALID LINK FOUND')
                vectors.append(i['id'])
            if i['object_type'] == 'root':
                print('VALID ROOT OBJECT FOUND')
            if i['object_type'] != 'link' and i['object_type'] != 'root':
                print('VALID OBJECT FOUND')
                objects.append(i['id'])

        result['vectors'] = vectors  # defines part of result dict
        result['objects'] = objects  # defines part of result dict
        # result['collections'] = collections  # defines part of result dict
        [print(result[i]) for i in ['vectors', 'objects']]
        return result

    def print_basic_statistics(self):
        """ Method prints out to screen basic statistics of database"""
        input_data = self.analyze_database_structure()  # use analyze method to obtain data
        print('\nVECTORS :\n', len(input_data['vectors']))  # print number of vectors
        print('\nOBJECTS :\n', len(input_data['objects']))  # print number of objects
        # print('\nCOLLECTIONS OR REPORTS:\n', len(input_data['collections']))  # print number of objects
        return
#
    # C A L C U L A T I O N S  A N D  V E C T O R S

    def calculate_id(self):
        """ Generates id code and checks duplicity in all objects in database"""
        while True:  # infinite loop
            random_id = random.randint(100000000, 999999999)  # generate random integer number
            # CHECKS IF NOT ID DUPLICITY
            for i in self.DBTree:  # loops thru main database function
                if i['id'] == random_id:  # if id is found DO:
                    random_id = random.randint(100000000, 999999999)  # generate new number
            return int(random_id)  # return valid id number

    @staticmethod
    def calculate_hash(self):  # TODO calculate MD5 hash with HMAC mechanism
        # calculates hash
        # hash will be stored in database with record
        return 'VOID_763654MD5'  # VOID value

    def calculate_perimeter1(self, id_code: int):
        """
        Method finds nearest objects by looping all links
        :param id_code: specific id number of db object
        :return: list of linked objects in first perimeter
        """
        result = list()  # define result as an empty list
        input_data = self.analyze_database_structure()  # input data are obtained from analyze database structure method
        exfil_list = input_data['vectors']  # exfiltrate all vectors(links) from dictionary
        print('EXFIL:', exfil_list)  # print list to screen
        for i in exfil_list:  # start looping all vectors in list
            finded_object = self.full_match_id_find(i)
            for k in range(0, len(finded_object)):
                if finded_object[k]['object_id1'] == id_code:  # if value changed from string to integer is equal to id
                    result.append(finded_object[k]['object_id2'])  # append vector(link) id to result list
                if finded_object[k]['object_id2'] == id_code:  # if value changed from string to integer is equal to id
                    result.append(finded_object[k]['object_id1'])  # append vector(link) id to result list
        print(result)  # prints result
        return result  # return result list

    def calculate_perimeter2(self, id_code: int):
        result = list()  # define result as an empty list
        input_data = self.analyze_database_structure()  # obtain input data from analyze database method
        exfil_list = input_data['vectors']  # define exfil list as part of input data dictionary [vectors]
        p1_links = self.calculate_perimeter1(id_code=id_code)  # calculate first perimeter to obtain
        print('PERIMETER1 LINKS',p1_links)  # first perimeter links ids
        print('EXFILTRATION LINKS', exfil_list)  # exfil links are still all vectors and links in database
        # TODO Maybe we should remove first perimeter from DB?
        # for i in p1_links:  # loops trhu first perimeter links
        #     for k in exfil_list:  # loops thru all vectors in database
        #         for g in range(0, len(k)):  # loops in all values of links
        #             if eval(str(k[g])) == id_code and i == k[2]:  # if vector is found which includes perimeter2 object
        #                 res = k[g+1]  # result is next value in list
        #                 if res == k[2]:  # if value is not next but previous
        #                     res = k[g-1]  # define res as previous value in list
        #                 print('HURRAY', res)  # prints MESSAGE and perimeter2 link
        #                 result.append(res)
        #                 result.append(self.calculate_perimeter1(res))  # calculate perimeter2 links with perimeter1 method
        print('PERIMETER TWO :', result)  # print perimeter2 result
        return result  # return result list
#
#     # TODO Obsolete chunk of junk code - REFACTOR OR REMOVE LATER
#     # def calculate_routes_and_vectors(self, start: bytes, exclude=None):
#     #     """ Method search DBTree for vectors and routes from root object but CAN NOT calculate reverse or side routes"""
#     #     routes = list()  # define routes as an empty list
#     #     result = list()  # define reuslt as an empty list
#     #     search = start  # define search as passed value
#     #     for i in self.DBTree:  # loops thru DBTree
#     #         piece_of_data = i['data']  # defines piece of data as part of dict
#     #         search_engine = re.match(search, piece_of_data)  # define search engine as regex match object
#     #         if search_engine:  # if match object exist
#     #             print('FOUND')  # prints msg
#     #             search_engine.group()  # obsolete code
#     #             pos = search_engine.span()  # finds span values - position in string
#     #             # print(pos)
#     #             result.append(piece_of_data[pos[0]:pos[1]])  # appends searched copied object
#     #             # add link object
#     #             # print(i['id'])
#     #             link = bytearray(str(i['id']), encoding='utf8')  # define link as id part of dictionary
#     #             result.append(link)
#     #             # add second object
#     #             result.append((piece_of_data[10:19]))  # TODO What if second object is not behind ?
#     #             search = bytes(piece_of_data[10:19])
#     #     result.append(b'END ROUTE')
#     #     routes.append(result)
#     #     print(result)
#     #     return routes

    # V I E W S

    def view_all(self):
        [print(i) for i in self.DBTree]

    # C H E C K S

    @staticmethod
    def check_id_len(id_code: int):
        """
         Method to check length of id code.
        :param id_code: integer value of id code
        :return: Boolean
        """
        if len(str(id_code)) == 9:  # if len is 9 digits long
            return True  # return True
        if len(str(id_code)) != 9:
            return False  # if not return False

    # def check_root_record(self):
    #     for i in self.DBTree:  # loops thru record result
    #         # ROOT RECORD DETECTION
    #         if i['id'] == 111111111:  # checking if root record is found
    #             print('ROOT RECORD DETECTED') # print msg
    #             return True
    #     print('ROOT RECORD IS MISSING')


    # P Y T E S T

    def test_id(self):
        assert len(str(self.calculate_id())) == 9





if __name__ == '__main__':
    db_obj = GDBResource(filename='db.json')
    # db_obj.drop_database()
    # db_obj.print_basic_statistics()
    # db_obj.db_object_record(object_type='program', data='print("Hello")', confirmed=True)
    # db_obj.db_object_record(object_type='person', data='DELTA', confirmed=True)
    # db_obj.db_link_record(670206254, 559027525, True, data='author')
    # [print(i) for i in db_obj.DBTree]
    # db_obj.print_basic_statistics()
    # db_obj.calculate_perimeter2(670206254)
    # db_obj.print_basic_statistics()
    # db_obj.find_text('ALPHA')
