import random
import os
import json
import re
import Encryption
# import redis
# import cmd
# import pytest
from CONFIG import AUTOSAVE, EXT_DB

KEY = [145, 194, 229, 232, 202, 213, 227, 147, 156, 198, 226, 227]


class GDBResource(object):
    """ Link based graph database to store data in memory and then commit to JSON file or redis.
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
        self.SALT = 'Nautilus'# is used with db_root_record to obtain BASE KEY
        self.KEY = [145, 194, 229, 232, 202, 213, 227, 147, 156, 198, 226, 227]  # TODO Write Method to obtain KEY from ... server ???
        self.DBTree = list()  # defines empty DBTree list
        if EXT_DB == 'redis':
            import redis
            self.redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)
        self.SELECTION = None  # selection of records is initiated as None
        self.load_all_from_json()
        self.check_root_record()
        print('DATABASE LOADED AND READY TO USE')

    # D A T A B A S E   O B J E C T S

    def db_root_record(self):
        """
         Defines data structure of root record and stores it to DBTree
        :return:
        """
        for i in self.DBTree:  # loops thru DBTree
            if i['id'] == 111111111:  # if root is found DO:
                self.DBTree.remove(i)  # remove old root record
        db_record = dict()  # defines as an empty dictionary
        id_code = 111111111  # id code of root record is always nine ones
        db_record['id'] = id_code  # writes id to dictionary
        db_record['object_type'] = 'root'
        db_record['relationships'] = self.analyze_database_structure()  # writes relationships to dictionary
        db_record['data'] = self.KEY
        self.DBTree.append(db_record)  # append dict to DBTree
        if EXT_DB == 'redis':
            # A D D   T O   R E D I S   D B
            self.redis_db.hset(id_code, 'object_type', 'root')
            self.redis_db.hset(id_code, 'relationships', str(self.analyze_database_structure()))
            self.redis_db.hset(id_code, 'data', str(self.KEY))
        return

    def db_object_record(self, object_type: str, data: str, id_code=None, confirmed=False):
        """
        Method defines data structure of record, adds record to DBTree
        and update root object
        :param object_type: person, asset, report
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
        self.save_all_to_json(file=self.filename)
        if EXT_DB == 'redis':
            # A D D   T O   R E D I S   D B
            self.redis_db.hset(id_code, 'object_type', object_type)
            self.redis_db.hset(id_code, 'data', data)
            self.redis_db.hset(id_code, 'confirmed', str(confirmed))
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
        self.save_all_to_json(file=self.filename)
        if EXT_DB == 'redis':
            # A D D   T O   R E D I S   D B
            self.redis_db.hset(id_code, 'object_type', 'link')
            self.redis_db.hset(id_code, 'object1_id', object1_id)
            self.redis_db.hset(id_code, 'object2_id', object2_id)
            self.redis_db.hset(id_code, 'data', data)
            self.redis_db.hset(id_code, 'confirmed', str(confirmed))
            self.redis_db.hset(id_code, 'reverse', str(reverse))
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
                    # print(i["id"], '\t', i["object_type"], '\t', i["data"], '\t', i["confirmed"])  # print record to screen
                    pass
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
        # print('\nFOUND IN OBJECTS:\n')  # find in objects:
        for i in source:  # loops thru database to check all records
            # check records stored in [id]:
            if i['id'] == id_code:  # if id is found
                # print(i["id"], '\t', i["object_type"], '\t', i["data"], '\t', i["confirmed"])  # print record to screen
                result['OBJECTS'].append(i)  # append record to result dict
                return result

        # SEARCHING IN LINKS [OBJECT_ID1] AND [OBJECT_ID2] PART OF DICTIONARY
        print('\nFOUND IN LINKS:\n')  # find in objects:
        for i in source:  # loops thru database to check all records
            # check records stored in [id]:
            if i['object_type'] == 'link':
                if i['object_id1'] == id_code or i['object_id2'] == id_code:  # if id is found
                    # print(i["id"], '\t', i["object_id1"], '\t', i["object_id2"], i["data"], '\t', i["confirmed"])
                    result['LINKS'].append(i)  # append record to result dict
                    return result

        # SEARCHING IN ALL [DATA]
        # print('\nFOUND FULLTEXT IN DATA:\n')  # fulltext regex search in [data] part of dictionary
        for i in source:  # loops thru database to check all records
            # check links and collections stored in [data]:
            search = re.match(str(id_code), i['data'])  # regex match search in data string
            if search:  # if success DO
                # print(i)  # print record to screen
                result['OTHER'].append(i)  # append record to result list
        if len(result['OBJECTS']) == 0 and len(result['LINKS']) == 0 and len(result['OTHER']) == 0:
            result['OTHER'] = 'NOT FOUND'
            # print('NOT FOUND')
        return result  # returns result dict

    def find_id_links(self, id_code: int, db=None):
        """
        Method finds all links with given id_code of record. This method purpose is
        to remove all links with removed id from database
        :param id_code: 9digit int representing record or link in database
        :param db: default set to None. If any parameter is not given default
        :return: list of links to remove or manipulate
        """
        result = list()
        if db is None:  # if db is not defined DO:
            source = self.DBTree  # switch to default
        else:
            source = db  # else db is selection or other given source in memory
        # SEARCHING IN LINKS [OBJECT_ID1] AND [OBJECT_ID2] PART OF DICTIONARY
        print('\nFOUND IN LINKS:\n')  # find in objects:
        for i in source:  # loops thru database to check all records
            # check records stored in [id]:
            if i['object_type'] == 'link':
                if i['object_id1'] == id_code or i['object_id2'] == id_code:  # if id is found
                    # print(i["id"], '\t', i["object_id1"], '\t', i["object_id2"], i["data"], '\t', i["confirmed"])
                    result.append(i)  # append record to result dict
                    return result

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
        print('\nFOUND IN OBJECT TYPES:\n')  # TODO Move to views
        print('ID CODE\t\tOBJECT TYPE\t\tDATA\t\tCONFIRMED\n')
        for i in source:  # loops records in source
            search = re.match(object_type, i['object_type'])  # regex match in [object_type] part of dictionary
            if search:  # if result
                print(i["id"], '\t', i["object_type"], '\t', i["data"], '\t', i["confirmed"])  # print record to screen
                result.append(i)  # append record to result dict
        if len(result) == 0:
            result.append('NOT FOUND')
            # print('NOT FOUND')
        return result  # return result list

    def find_text(self, text: str, db=None):
        """
        Method searches text in string format in data values of all objects and links
        :param text: string value to search for
        :param db: source to search if None - default DBTree
        :return: list of finded records
        """
        result = list()  # define result as an empty list
        partial_result = list()  # define partial list as an empty list
        file2search = str()  # define file2search as an empty string
        # TODO Show basic statistics of Search
        # TODO Filter Root and other irrelevant data fields from search
        if db is None:  # if db is not given as parameter DO
            source = self.DBTree  # default defined database
        else:
            source = db  # if parameter db is given use it instead default
        # print('\nFOUND IN OBJECTS AND LINKS:\n')  #
        for i in source:  # loops in db
            try:
                file2search = i['data']  # search for fulltext
                with open(file=file2search, mode='r', encoding='utf8') as f:
                    file_content = f.read()
                    file_content = file_content.upper()  # Make string to upper characters
                    text = text.upper()  # make string to upper characters
                    partial_result = re.search(text, file_content)  # regular expression search
            except FileNotFoundError:
                pass
            finally:
                if partial_result:
                    print(file2search, ' FOUND ')
                    result.append(file2search)
                if partial_result is None:
                    # print(file2search, ' NOT FOUND ')
                    pass
                file_content = ''
        print(result)
        return result  # return list of records

    @staticmethod
    def fulltext_multiword_search(text, find):
        """
        Function takes text, removes special characters and split into bag
        of words. Then splits multiword to search also to list. splits it
        and try to find in bag. If success returns True
        :param text: string
        :param find: multiword string
        :return: Boolean value or None
        """
        # remove special characters
        special_chars = '.!@#$%^&*():"{}[]_-=+/<>'  # define special characters
        for i in special_chars:  # loops tru special characters
            text = text.replace(i, '')  # remove special character from text
        print(text)  # prints to console

        # split text to list of words
        bag = text.split(sep=' ')  # splits text to list of words
        print(bag)  # prints list to console

        # get number of words to find in words
        list_of_words_in_find = find.split(sep=' ')  # splits find to list
        num_of_words = len(list_of_words_in_find)  # get number of words in multiword

        try:
            for i in range(0, len(bag)):  # loops tru bag
                # construct constructed string to search
                constructed_string = bag[i] + ' '  # define constructed string as word plus SPACE
                for k in range(1, num_of_words):  # loops to add same number of words as find has
                    constructed_string += bag[i + k] + ' '  # adds next word and SPACE
                constructed_string = constructed_string[0:-1]  # final result must be modified by removing last SPACE
                print(constructed_string)  # prints to console
                if constructed_string == find:  # if find string is same as constructed string
                    print('GOTCHA')  # print SUCCESS to console
                    return True  # return True - find was found in text
                # print(i, constructed_string)
        except IndexError:  # if IndexError raises ... find is not in text return False
            print('DONE')
            return False
        finally:
            pass



    # A D V A N C E D   S E A R C H   W I T H   P E R I M E T E R  C A L C U L A T I O N S

    def near_objects(self, id_code: int):
        """
        Method calculates nearest asscociated objects (not links)
        :param id_code: 9digit id code of record in database
        :return: list of nearest objects
        """
        result = self.calculate_perimeter1(id_code=id_code)
        return result

    def not_far_objects(self, id_code: int):
        """
        Method calculates objects next to nearest(2links away)
        :param id_code: 9digit id code of record in database
        :return: list of objects not far
        """
        result = self.calculate_perimeter2(id_code=id_code)
        return result

    def association(self, id1: int, id2: int):
        """
        Method compares perimeter calculation of id1 and id2 and returns boolean if objects are linked
        :param id1: 9digit id code of record in database
        :param id2: 9digit id code of record in database
        :return:
        """
        i1_all_associated_objects = set()
        i2_all_associated_objects = set()
        i1_p1_objects = self.calculate_perimeter1(id_code=id1)
        if len(i1_p1_objects) != 0:
            i1_all_associated_objects = self.calculate_next_perimeters(id_code=id1, associated_objects=i1_p1_objects)
        if len(i1_p1_objects) == 0:
            result = False
            return result
        i2_p1_objects = self.calculate_perimeter1(id_code=id2)
        if len(i2_p1_objects) != 0:
            i2_all_associated_objects = self.calculate_next_perimeters(id_code=id2, associated_objects=i2_p1_objects)
        if len(i2_p1_objects) == 0:
            result = False
            return result
        for i in i1_all_associated_objects:
            for k in i2_all_associated_objects:
                if k == i:
                    result = True
                    return result
        result = False
        return result

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

    # E N C R Y P T I O N   A N D   D E C R Y P T   D A T A

    def obtain_key(self, id_code=None):
        """
        Method to obtain base key from Root record and decrypt with SALT
        :return: base key (string) used for further encryption of data
        """
        if id_code is None:
            id_code = 111111111
        for i in self.DBTree:  # loops db
            if i['id'] == id_code:  # if root record is found DO
                root_data = i['data']  # extract data from root record
                print(root_data)  # control print to console
                raw_root_string = root_data[1:-1]  # # remove brackets
                raw_root_list = raw_root_string.split(',')  # split string to list with , as separator
                print(raw_root_list)  # control print to console
                raw_root_ints = list()  # defines empty list
                [raw_root_ints.append(eval(i)) for i in raw_root_list]  # change values from string to integers
                print(raw_root_ints)  # control print to console

        string2 = self.SALT  # define plaintext string
        str_values_list2 = list()  # define string value list as an empty list
        [str_values_list2.append(ord(i)) for i in string2]  # add integer representation of symbols to list
        print(str_values_list2)  # print value list
        base_key = Encryption.SimpleSubstitution.decrypt_simple_substitution(encrypted_values=raw_root_ints,
                                                                             pwd_values=str_values_list2)
        # decryption of two lists - salt and key from root record
        print(base_key)  # control print to console
        return base_key  # return base key string

    def calculate_next_key(self, values: list, enc=True):
        next_key = list()
        base_key = self.obtain_key()
        # P R E P A R E   K E Y
        key_values_list = list()  # define string value list as an empty list
        [key_values_list.append(ord(i)) for i in base_key]  # add integer representation of symbols to list
        print(key_values_list)  # print value list
        if enc is True:
            # ENCRYPTION
            next_key = Encryption.SimpleSubstitution.encrypt_simple_substitution(
                plaintext_values=values, pwd_values=key_values_list)  # TODO Remove AttributeError
        return next_key

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
        self.save_all_to_json(file=self.filename)  # save empty file
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
                if i['id'] == 111111111:
                    self.DBTree.remove(i)
                    self.db_root_record()
                    self.save_all_to_json(file=self.filename)  # TODO !!!!!
                    # self.db_root_record()

    def save_all_to_json(self, file: str):
        """ Export all records in DBTree to specified file
                :return: True if success
                """
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
                # [print(converted_dbtree['DBTree'][i]) for i in range(0, len(converted_dbtree['DBTree']))]
                self.DBTree = list()  # removes all data and import new from json
                for i in range(0, len(converted_dbtree['DBTree'])):
                    self.DBTree.append(converted_dbtree['DBTree'][i])
        except FileNotFoundError:
            # self.init_new_database()
            # print('NEW DATABASE WAS INITIALIZED')
            print('DATABASE json file was not find')
            return False
        finally:
            print('DONE')
            return True  # return
# TODO Refresh database command
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
            # collect_ids = list(filter(self.check_id_len, collect_ids))
            #  obsolete due regex refactoring TODO Test and remove
            collect_ids.append(i['id'])  # append id integer of record  # TODO check if not usefull in start of current loop
            if collect_ids:  # if exists DO
                record_result.append(collect_ids)  # append to record_result list
        # CHECK OBJECTS AND LINKS IN DBTREE
        for i in self.DBTree:
            if i['object_type'] == 'link':
                # print('VALID LINK FOUND')
                vectors.append(i['id'])
            if i['object_type'] == 'root':
                # print('VALID ROOT OBJECT FOUND')
                pass
            if i['object_type'] != 'link' and i['object_type'] != 'root':
                # print('VALID OBJECT FOUND')
                objects.append(i['id'])

        result['vectors'] = vectors  # defines part of result dict
        result['objects'] = objects  # defines part of result dict
        # result['collections'] = collections  # defines part of result dict
        # [print(result[i]) for i in ['vectors', 'objects']]
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
        # print(f'SEARCH FOR NEAREST LINKS AND OBJECTS FOR :{id_code}')
        result = list()  # define result as an empty list
        input_data = self.analyze_database_structure()  # input data are obtained from analyze database structure method
        exfil_list = input_data['vectors']  # exfiltrate all vectors(links) from dictionary
        # print('EXFIL:', exfil_list)  # print list to screen
        for i in exfil_list:  # start looping all vectors in list
            finded_object = self.full_match_id_find(i)
            for k in range(0, len(finded_object)):
                if finded_object[k]['object_id1'] == id_code:  # if value changed from string to integer is equal to id
                    result.append(finded_object[k]['object_id2'])  # append vector(link) id to result list
                if finded_object[k]['object_id2'] == id_code:  # if value changed from string to integer is equal to id
                    result.append(finded_object[k]['object_id1'])  # append vector(link) id to result list
        # print(result)  # prints result
        return result  # return result list

    def calculate_perimeter2(self, id_code: int):
        """
        Method calculates second perimeter of id_code by looping
        all objects from first perimeter
        :param id_code:  9 digit number
        :return: list of objects in second perimeter
        """
        result = list()  # define result as an empty list
        input_data = self.analyze_database_structure()  # obtain input data from analyze database method
        exfil_list = input_data['vectors']  # define exfil list as part of input data dictionary [vectors]
        p1_objects = self.calculate_perimeter1(id_code=id_code)  # calculate first perimeter to obtain
        # print('PERIMETER1 OBJECTS', p1_objects)  # first perimeter links ids
        # print('EXFIL ALL LINKS FROM DB', exfil_list)  # exfil links are still all vectors and links in database
        # TODO Refactor to calculate all associated links
        for i in p1_objects:  # loops tru first perimeter links
            result.append(i)  # append perimeter1 object to result list
            partial_result = self.calculate_perimeter1(i)  # calculates p1 objects to id from p1_objects
            for k in partial_result:  # loops partial result list
                if k != id_code:  # if id in partial result is not equal to idcode
                    result.append(k)  # append obj to result
        # print('PERIMETER TWO OBJECTS:', result)  # print perimeter2 result
        return result  # return result list

    def calculate_next_perimeters(self, id_code: int, associated_objects: list):
        """
        Method calculates second perimeter of id_code by create infinite loop to research
        all associated objects in database
        :param id_code: 9 digit number
        :param associated_objects: list of objects to calculate next perimeters
        :return: list of objects in second perimeter
        """
        # TODO Doesn't work properly - doesn't find all associated links and objects
        # count = itertools.count(0, 1)
        all_associated_old = set()  # defines empty set used as value from previous loop to compare
        all_associated_obj = set()  # defines empty set used as total result of all associated obj in database
        result = list()  # defines result as an empty list
        flag = True  # variable flag is used as a trigger
        input_data = self.analyze_database_structure()  # obtain input data from analyze database method
        exfil_list = input_data['vectors']  # define exfil list as part of input data dictionary [vectors]
        # print('PERIMETER1 OBJECTS', associated_objects)  # first perimeter links ids
        # print('EXFIL ALL LINKS FROM DB', exfil_list)  # exfil links are still all vectors and links in database
        while flag is True:  # infinite loop with flag as trigger
            for i in associated_objects:  # loops tru first perimeter links
                result.append(i)  # adds object to result
                partial_result = self.calculate_perimeter1(i)  # calculates p1 objects to id from p1_objects
                for k in partial_result:  # loops partial result list
                    if k != id_code:  # if id in partial result is not equal to idcode
                        result.append(k)  # append obj to result
            # print('NEXT PERIMETER OBJECTS:', result)  # print next perimeter result
            [all_associated_obj.add(h) for h in result]  # add all calculated obj to set representing total result
            if all_associated_obj == all_associated_old and len(all_associated_obj) != 0:  # if there are not new
                # objects and it is not first run in loop  #
                [all_associated_obj.add(h) for h in result]
                # count.__next__()
                flag = False  # raise flag to exit loop
                # print('ALL ASSOCIATED OBJECTS IN DB', all_associated_obj)  # prints total result
            if result:  # if result exists
                [all_associated_obj.add(h) for h in result]
                associated_objects = result  # sets value of associated obj as result for next loop
                all_associated_old = all_associated_obj  # sets copy of variable to old to compare in next loop
                result = list()  # reset result as empty list
        # print('ALL', result)  # prints result
        # TODO recalculate all p1 from all_associated obj to be sure
        return all_associated_obj  # return all associated objects in db

    # V I E W S

    def view_all(self):
        """
        Method views all records in database
        :return:
        """
        [print(i) for i in self.DBTree]
        return

    def view_all_object_types(self):
        """
        Method views all object types in database without Root record
        :return:
        """
        result = set()
        for i in self.DBTree:
            if i['object_type'] != 'root':
                result.add(i['object_type'])
        return result

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

    def check_root_record(self):
        """
        Method tries to find Root record in database. If Root record is not present then
        :return:
        """
        counter = 0
        for i in self.DBTree:  # loops thru record result
            # ROOT RECORD DETECTION
            if i['id'] == 111111111:  # checking if root record is found
                print('ROOT RECORD DETECTED') # print msg
                counter += 1
        if counter == 0:
            print('ROOT RECORD IS MISSING - NEW WILL BE CALCULATED')
            self.db_root_record()
            return None
        if 0 < counter > 1:
            for i in range(0, counter-1):
                for k in self.DBTree:
                    if ['id'] == 111111111:
                        self.DBTree.remove(k)
                        print('MORE ROOT RECORDS DETECTED')
            return False
        if counter == 1:
            self.save_all_to_json(file=self.filename)
            return True

    def close(self):
        pass

# P Y T E S T   T E S T S


@pytest.fixture(scope='module')  # decorator of class with scope definition
def obj():  # function to define class for all tests
    print('------setup-fixture------------')  # marker to show execution of code
    obj = GDBResource(filename='test_db.json')  # instance of class for testing purpose
    yield obj  # yields instance to tests
    print('------teardown-------------')  # marker to show execution of code
    obj.close()  # colling closing function of instance


def test_id(obj):
    assert len(str(obj.calculate_id())) == 9


def test_id_length(obj):
    assert obj.check_id_len(id_code=123456) is False
    assert obj.check_id_len(id_code=123456789) is True


def test_fulltext(obj):
    assert obj.fulltext_multiword_search('Analyza dokazala hovno!', 'Peter') is None
    assert obj.fulltext_multiword_search('Analyza dokazala hovno!', 'Analyza') == True
    assert obj.fulltext_multiword_search('Analyza dokazala hovno!', 'dokazala') == True
    assert obj.fulltext_multiword_search('Analyza dokazala hovno!', 'hovno') == True


def test_check_root(obj):
    assert obj.check_root_record() is True


def test_analyze_db_structure(obj):
    assert obj.analyze_database_structure() == {'objects': [781513433], 'vectors': []}


def test_load_from_json(obj):
    assert obj.load_all_from_json() is True
    # obj.filename = 'crap.json'
    # assert obj.load_all_from_json() is False  # TODO Doesnt work

# TODO Add more tests


class DbEncryption(object):
    """Class Encrypt and Decrypt every data file in directory with given KEY"""
    def whole_db_encryption(self):  # encrypts all data fields in db records in memory
        """
        Method takes KEY value list and apply simple substitution every db data file
        So links between objects and idcodes stays revealed but data in files is encrypted
        :return:
        """
        pass

    def whole_db_decryption(self):  # decrypts all data fields in db records in memory
        """
        Method takes KEY value list and apply simple substitution every db data file
        So links between objects and idcodes stays revealed but data in files is encrypted
        :return:
        """
        pass


if __name__ == '__main__':
    db_obj = GDBResource(filename='db.json')

