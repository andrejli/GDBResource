import random
import os
import json
import re
from CONFIG import AUTOSAVE


class GDBResource(object):
    """ Link based graph database to store data in memory and then commit to file.
        Database has objects:
            :: db_root_record - master base key for blockchain encryption mechanism
            :: DBObject_record - with parameters :: otype =(Person, Asset, Phone, Car, etc.)
                                                :: data is bytearray containing data about object OR
                                                :: objects two ids of objects link is connecting OR
                                                :: multiple ids as a collection
                                                :: id identification number of object if None db generates new id
            :: DBObject link  - with parameters :: otype: link
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
        self.SALT = 'KNOWN SECRET'  # is used with db_root_record to obtain BASE KEY
        self.DBTree = list()  # defines empty DBTree list
        self.selection = None  # selection of records is initiated as None
        self.loaded_raw_data = self.load_all_data()  # loads all data from file  # TODO Change to JSON
        self.parse_store_to_DBTree()  # parse data to DBTree  # TODO Change to JSON
        # TODO Check integrity of database -
        print('DATABASE READY TO USE')

    # D A T A B A S E   O B J E C T S

    def db_root_record(self, otype: str, data: bytearray):
        """ Defines data structure of root record and stores it to DBTree
        """
        db_record = dict()  # defines as an empty dictionary
        id_code = 111111111  # id code of root record is always nine ones
        db_record['id'] = id_code  # writes id to dictionary
        db_record['otype'] = otype  # writes otype to dictionary
        db_record['data'] = data  # TODO Generate or obtain 1800bytes key
        self.DBTree.append(db_record)  # append dict to DBTree
        if AUTOSAVE is True:
            self.save_all_data()
        return

    def DBObject_record(self, otype: str, data: bytearray, id_code=None):
        """ Defines data structure of object
        :param  otype: object type(person, link, collection, report, asset, etc.)
                data: data stored as bytearray
                id_code: calculated or defined integer from 100000000 to 999999999
        """
        db_record = dict()  # defines DBrecord as dict
        if id_code is not None:  # if id_code is not given
            db_record['id'] = id_code  # overrides generation of new id in loads and in specific cases
        else:  # if id_code is None DO:
            id_code = self.calculate_id()  # generate new id_code
            db_record['id'] = id_code  # store id in dict
        db_record['otype'] = otype  # store otype in dict
        db_record['data'] = data  # store data in dict
        self.DBTree.append(db_record)  # append dict to DBTree
        if AUTOSAVE is True:
            self.save_all_data()
        return

    # S I M P L E   F I N D   M E T H O D S

    def find_id(self, id_code: int, db=None):
        """ find id with default source set as self.DBTree and could be set to selection or specific query
        :param id_code: identification code
        :param db: database source to search
        :return: list of found records in source
        """
        result = []  # define result as an empty list
        source = self.DBTree  # setting default value of source
        if db is None:  # if db is not defined DO:
            source = self.DBTree  # switch to default
        else:
            source = db  # else db is selection or other source # TODO Think about
        print('\nFOUND IN OBJECTS:\n')  # find in objects:
        for i in source:  # loops thru database to check all records
            # check records stored in [id]:
            if i['id'] == id_code:  # if id is found
                print(i)  # print record to screen
                result.append(i)  # append record to result list TODO Think about to change result to dict
        print('\nFOUND IN LINKS, REPORTS AND COLLECTIONS:\n')  # fulltext regex search in [data] part of dictionary
        for i in source:  # loops thru database to check all records
            # check links and collections stored in [data]:
            search = re.match(str(id_code), i['data'])  # regex match search in data string
            if search:  # if success DO
                print(i)  # print record to screen
                result.append(i)  # append record to result list
        return result  # returns result list

    def find_otype(self, otype: str, db=None):
        """ method finds object type and list all to screen
        :param otype: object type(person, link, collection, report)
        :param db: source to search if None - default DBTree
        :return: list of found records in source
        """
        result = list()  # define result as an empty list
        source = self.DBTree  # define default source as self.DBTree function
        if db is None:  # if db is not defined
            source = self.DBTree  # use default database
        else:
            source = db  # use other defined source as selection etc.
        print('\nFOUND IN OBJECT TYPES:\n')  #
        for i in source:  # loops records in source
            search = re.match(otype, i['otype'])  # regex match in [otype] part of dictionary
            if search:  # if result
                print(i)  # print record
                result.append(i)  # append record to result dict
        return result  # return result list

    def find_text(self, text: str, db=None):
        result = list()
        source = self.DBTree
        if db is None:
            source = self.DBTree
        else:
            source = db
        print('\nFOUND IN OBJECT TYPES:\n')
        for i in source:
            # check links and collections:
            search = re.match(bytes(text, encoding='utf8'), i['data'])
            if search:
                print(i)
                result.append(i)
        return result

    # S E L E C T  R E C O R D S

    def select_all(self):
        self.selection = self.DBTree
        print('\nSELECTION FROM DATABASE :\n')
        [print(i) for i in self.selection]
        return self.selection

    def add_id_to_selection(self, id_code: int):
        if self.selection is None:
            self.selection = list()
        for i in self.DBTree:
            if i['id'] == id_code:
                self.selection.append(i)
        print('\nSELECTION FROM DATABASE :\n')
        [print(i) for i in self.selection]
        return

    def remove_id_from_selection(self, id_code: int):
        if self.selection is not None:
            for i in self.selection:
                if i['id'] == id_code:
                    self.selection.append(i)
            print('\nSELECTION FROM DATABASE :\n')

    def drop_selection(self):
        """ Method to drop selection of records
        :return:
        """
        self.selection = None
        return


    # A D M I N  P R O C E D U R E S

    def init_new_database(self):
        """ Method to initialize new database.
        :return:
        """
        self.DBTree = list()  # drop old and make empty function
        # make new empty root record
        self.db_root_record(otype='root', data=bytearray('ROOT TABLE', encoding='ascii'))
        self.save_all_data()  # save it to instance db file
        return  #

    def drop_database(self):
        """ Method to drop all database
        :return:
        """
        for i in self.DBTree:  # loop all records
            self.DBTree.remove(i)  # remove all records
        self.save_all_data()  # save empty
        cmd = 'rm ' + self.filename  # remove file
        os.system(command=cmd)  # execute via os.system command  # TODO Use shutil module
        return

    # F I L E   A N D   D A T A   M A N I P U L A T I O N
    # TODO Make incremental save possible
    def save_all_data(self):
        """ Saves all records in DBTree to specified file
        :return: True if success
        """
        try:
            cmd = 'rm ' + self.filename
            os.system(command=cmd)
        except FileNotFoundError:
            print('FILE DOESNT EXIST YET  !!!')
        finally:
            with open(file=self.filename, mode='w') as f:
                for i in range(0, len(self.DBTree)):
                    data_to_save = str(self.DBTree[i]) + '\n'
                    print(data_to_save)
                    # lines.append(data_to_save)
                    f.writelines(data_to_save)
                print('ALL SAVED')
                return True

    def load_all_data(self):
        """ Method to load all data from file self.filename
        :return:
        """
        result = list()
        try:
            with open(file=self.filename, encoding='utf8') as f:
                while True:
                    raw_data = f.readline()
                    if len(raw_data) == 0:
                        break
                    print(raw_data)
                    result.append(raw_data)
        except FileNotFoundError:
            self.init_new_database()
        finally:
            print('DONE')
            return result

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
                json.dump({'DBTree': converted_dbtree}, f)  # dumps converted list to file
                print(f'EXPORTED TO JSON: {file}')  # print message
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

    # E X P O R T   I M P O R T   C O M M A N D S

    def export_to_json(self, file: str):
        """ Export all records in DBTree to specified file
                :return: True if success
                """
        try:
            cmd = 'rm ' + file  # try to remove old saved file
            os.system(command=cmd)  # execute system command via os.system
        except FileNotFoundError:  # exception handle
            print('FILE DOESNT EXIST YET  !!!')  # print msg
        finally:
            with open(file=file, mode='w') as f:  # open file as f
                # CONVERT DBtree to serializable data
                converted_dbtree = self.DBTree  # makes copy of DBTree function
                for i in converted_dbtree:  # loops thru dicts
                    i['data'] = str(i['data'])  # changes bytearrays to strings
                json.dump({'DBTree': converted_dbtree}, f)  # dumps converted list to file
                print(f'EXPORTED TO JSON: {file}')  # print message
                return True  # return

    def import_from_json(self, file: str):
        """ Method to import all records from specified file to DBTree instance
                        :return: True if success
                                 False if rejected
                        """
        with open(file=file, mode='r') as f:  # open file as f
            converted_dbtree = json.load(f)  # loads json from file
            [print(converted_dbtree['DBTree'][i]) for i in range(0, len(converted_dbtree['DBTree']))]
            key = input(f'IMPORTED FROM JSON: {file} (y/n')  # TODO Make method to yes/no
            if key == 'y':
                for i in range(0, len(converted_dbtree['DBTree'])):
                    # TODO check duplicity of records
                    self.DBTree.append(converted_dbtree['DBTree'][i])
                    return True  # return
            if key == 'n':
                return False

    def parse_store_to_DBTree(self):
        """ Method to load objects from file and insert them back to record dict to list DBTree"""
        objects = self.loaded_raw_data
        otype = ''
        id_code = int()
        for i in objects:
            # REASSEMBLE ID
            if i[2:4] == 'id':
                id_code = eval(i[7:16])
                self.check_id_len(id_code=id_code)
            # REASSEMBLE OTYPE
            if i[19:24] == 'otype':
                otype_word = re.findall(r'\w+', i[24:])
                otype = otype_word[0]
            # REASSEMBLE DATA  # TODO Refactor Later using re or other module
            for k in range(0, len(i)-4):
                if i[k:k+4] == 'data':
                    raw_data = i[k:]
                    raw_data_list = raw_data.split("b'")
                    raw_data_string = raw_data_list[1]
                    pure_data_string = raw_data_string[:len(raw_data_string)-4]
                    d = bytearray(pure_data_string, encoding='utf8')
                    self.DBObject_record(otype=otype, data=d, id_code=id_code)
        return

    # A N A L Y Z E R S  A N D  D A T A B A S E   S T A T I S T I C S

    def analyze_database_structure(self):
        """ Method to analyze structure of database
        :return: dict with all values of routes(root to object links), vectors (links) and objects.
        """
        result = dict()  # define variable as an empty dictionary
        objects = list()  # define variable as an empty list
        routes = list()  # define variable as an empty list
        vectors = list()  # define variable as an empty list
        collections = list() # define variable as an empty list
        record_result = list()  # define variable as an empty list
        # LOOP TO FIND ALL IDS IN DATA PART OF RECORD
        for i in self.DBTree:  # loops all values in DBTree
            collect_ids = re.findall(r'\d+\d+\d+\d+\d+\d+\d+\d+\d', str(i['data']))  # regex findall of 9digits numbers
            # collect_ids = list(filter(self.check_id_len, collect_ids))  # obsolete due regex refactoring TODO Test and remove
            collect_ids.append(i['id'])  # append id integer of record  # TODO check if not usefull in start of current loop
            if collect_ids:  # if exists DO
                record_result.append(collect_ids)  # append to record_result list
        # CHECK EXISTENCE OF ROOT Record
        self.check_root_record()
        # MAIN ROUTES DETECTION  # TODO DOesn't work BUGS ARE ANYWHERE
        # if i[0] == '111111111':  # if root record is found in links
        #     print('MAIN ROUTE DETECTED')  # print msg
        #     routes.append(i)  # append route to routes list
        for i in record_result:  # loops thru record found TODO Merge with previous loop an test
            if len(i) == 1:  # if length of i is equal 1 it's object
                objects.append(i)  # append i to objects
            if len(i) == 3:  # if length of i is equal 1 it's vector
                vectors.append(i)  # append i to vectors
            if len(i) > 3:  # if length of i is equal 1 it's collection or report
                collections.append(i)  # append i to vectors

        result['routes'] = routes  # defines part of result dict
        result['vectors'] = vectors  # defines part of result dict
        result['objects'] = objects  # defines part of result dict
        result['collections'] = collections  # defines part of result dict
        # [print(result[i]) for i in ['routes', 'vectors', 'objects', 'collections']]
        return result

    def print_basic_statistics(self):
        """ Method prints out to screen basic statistics of database"""
        input_data = self.analyze_database_structure()  # use analyze method to obtain data
        print('\nROUTES :\n', len(input_data['routes']))  # print number of routes to root object  # TODO Think if not obsolete
        print('\nVECTORS :\n', len(input_data['vectors']))  # print number of vectors
        print('\nOBJECTS :\n', len(input_data['objects']))  # print number of objects
        print('\nCOLLECTIONS OR REPORTS:\n', len(input_data['collections']))  # print number of objects
        return

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

    def calculate_perimeter1(self, id_code: int):  # TODO Check if not necessery
        result = list()  # define result as an empty list
        input_data = self.analyze_database_structure()  # input data are obtained from analyze database structure method
        exfil_list = input_data['vectors']  # exfiltrate all vectors(links) from dictionary
        print('EXFIL:', exfil_list)  # print list to screen
        for i in exfil_list:  # start looping in list
            for k in i:  #  start looping in vector, link values
                if eval(str(k)) == id_code:  # if value changed from string to integer is equal to id
                    result.append(i[2])  # append vector(link) id to result list
        print(result)  # prints result
        return result  # return result list


    def calculate_perimeter2(self, id_code: int):  # TODO Doesn't work
        result = list()  # define result as an empty list
        input_data = self.analyze_database_structure()  # obtain input data from analyze database method
        exfil_list = input_data['vectors']  # define exfil list as part of input data dictionary [vectors]
        p1_links = self.calculate_perimeter1(id_code=id_code)  # calculate first perimeter to obtain
        print('PERIMETER1 LINKS',p1_links)  # first perimeter links ids
        print('EXFILTRATION LINKS', exfil_list)  # exfil links are still all vectors and links in database
        # TODO Maybe we should remove first perimeter from DB?
        for i in p1_links:  # loops trhu first perimeter links
            for k in exfil_list:  # loops thru all vectors in database
                for g in range(0, len(k)):  # loops in all values of links
                    if eval(str(k[g])) == id_code and i == k[2]:  # if vector is found which includes perimeter2 object
                        res = k[g+1]  # result is next value in list
                        if res == k[2]:  # if value is not next but previous
                            res = k[g-1]  # define res as previous value in list
                        print('HURRAY', res)  # prints MESSAGE and perimeter2 link
                        result.append(res)
                        result.append(self.calculate_perimeter1(res))  # calculate perimeter2 links with perimeter1 method
        print('PERIMETER TWO :', result)  # print perimeter2 result
        return result  # return result list

    # TODO Obsolete chunk of junk code - REFACTOR OR REMOVE LATER
    # def calculate_routes_and_vectors(self, start: bytes, exclude=None):
    #     """ Method search DBTree for vectors and routes from root object but CAN NOT calculate reverse or side routes"""
    #     routes = list()  # define routes as an empty list
    #     result = list()  # define reuslt as an empty list
    #     search = start  # define search as passed value
    #     for i in self.DBTree:  # loops thru DBTree
    #         piece_of_data = i['data']  # defines piece of data as part of dict
    #         search_engine = re.match(search, piece_of_data)  # define search engine as regex match object
    #         if search_engine:  # if match object exist
    #             print('FOUND')  # prints msg
    #             search_engine.group()  # obsolete code
    #             pos = search_engine.span()  # finds span values - position in string
    #             # print(pos)
    #             result.append(piece_of_data[pos[0]:pos[1]])  # appends searched copied object
    #             # add link object
    #             # print(i['id'])
    #             link = bytearray(str(i['id']), encoding='utf8')  # define link as id part of dictionary
    #             result.append(link)
    #             # add second object
    #             result.append((piece_of_data[10:19]))  # TODO What if second object is not behind ?
    #             search = bytes(piece_of_data[10:19])
    #     result.append(b'END ROUTE')
    #     routes.append(result)
    #     print(result)
    #     return routes

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
        for i in self.DBTree:  # loops thru record result
            # ROOT RECORD DETECTION
            if i['id'] == 111111111:  # checking if root record is found
                print('ROOT RECORD DETECTED') # print msg
                return True
        print('ROOT RECORD IS MISSING')


    # P Y T E S T

    def test_id(self):
        assert len(str(self.calculate_id())) == 9


if __name__ == '__main__':
    db_obj = GDBResource(filename='test7.txt')



    db_obj.print_basic_statistics()

    # TODO Add view all object types