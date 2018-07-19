import random
import os
import json
import re
from CONFIG import AUTOSAVE


class GDBResource(object):
    """ Link based database to store data in memory and then commit to file.
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
    # db_obj.check_root_record()
    # [print(i) for i in db_obj.DBTree]
    db_obj.DBObject_record(otype='person', data=bytearray('Andrej', encoding='utf8'), id_code=None)
    # db_obj.DBObject_record(otype='link', data=bytearray('111111111:100000001', encoding='utf8'), id_code=100000008)
    db_obj.DBObject_record(otype='person', data=bytearray('Sylvia', encoding='utf8'), id_code=None)
    # db_obj.DBObject_record(otype='link', data=bytearray('439942805:872436024', encoding='utf8'), id_code=None)
    db_obj.DBObject_record(otype='person', data=bytearray('Leon', encoding='utf8'), id_code=None)
    # db_obj.DBObject_record(otype='collection', data=bytearray('518856625:872436024:439942805:179044888:FAMILY MEMBERS', encoding='utf8'), id_code=None)
    # db_obj.DBObject_record(otype='link', data=bytearray('100000004:100000002', encoding='utf8'), id_code=100000006)
    # db_obj.DBObject_record(otype='link', data=bytearray('179044888:325229255', encoding='utf8'), id_code=None)
    # db_obj.DBObject_record(otype='person', data=bytearray('RUM Club', encoding='utf8'), id_code=None)
    # db_obj.db_root_record(otype='root', data=bytearray('a96b572e7ae74fba72ba2d56efdf1e1a608ee3549a6a83e0dc4840544122ac54ddd161b712882313a14faea351bf2e111c164ccb47ef62213525a68bfa88c731f1d93862c24a5354b28e9c9f6e6f9336b3931cb28b95e9b1bbd56784db72a2c5ebb2c598763f86de4de8acdad2c8cfb9d08ca75131e8ac822f128c933aa23cf1591850c9b19580bcb7fc617249f7f5f516fa6d1339a9adcdb3e545978d2b21dffff4a168952078cdabc519f8b9ad14743a8615fcf8679f913c74bce2637b5b9c4d399fe0feca2b3fddabc593fe1dfeabab75d09151bc2d4d3752fb2f57c8c66aee7b6cb9622bcefc83d4cd63c16291e7bca678c7774c0f06736b3899144893d054d6a96d27236727aa36c60c33de247b19cc635e3deee8a714d88272a9c983c2f7a12d5c18a1d1fb05df49aa6cfc4cea93f6c818520513df3611912ff976ea33243c8c4fb66bb5759d6825e23be3403f0e616c189602fca02f4fc5637a3c8cfb23bb3cb99836eba1a83550628c47178e337c57d6f9051353e948cfef87b3920dc48c3fd23826a1385ba39c14db9192dde2b52a3857ecfd1a66ca53db121115dde6279ecac6e9a6384057f67824f6c6da7d73426280eecba539b8972c773e3cf559a19f5a9895ee3bc9de14bf282c444f03da168bd10d1c66eb9c8bbf7c5d6ca32b9aaa778556da428cdc3112909dce38efb424688fb7376fca0d2484cc50237c3268f5154a0babe42428797beb53c4991bc184c3b0abee5bff98b5942a654c77f952d9294c9c3631c7713c7678ed0198ec1fcdbfd37b13cf40438eb23f2f9d373bd93f3ad27b72b421dd0efabee911a7894105c119f9491cbc011a7a17d3f0ccccd9f6cdf3a322ae98be8912c9f2578f1953ddc8ce2fa7817b4d821caf74e44efcf60dae0ece615aef4817df93dd198c8ddabaf75872656378e2f82ced24446751fce9c4f4ce58854d8881a4b7f40eafc12e4a63254455512253ace71529284b3db6dbbfbee02258ab19782df7be40e75f5b4f24afe5ea6b22eec2e247b536b2b21b62c38fa6e7853a82fda53828716c5acc7a75d45cfee79636bbbf77ed1ada9ea0437f7bb73b4e775f3ba1ec85b9e470647652ef584330f9d4abc1c988466bff113f6e4c5b356dafc2d32a73e4fffcfe2969469437526868fbfac22cca2a952e428b1856aae8866fea7a4886da6f8146b621cae79e4d38245e967815f3dbf1b0ebcb52b8b57ebdf976a9bf648d92b9f2df75d61f50b345daa33ce567c135065f28d4db13b1b4e294954516aaa5bbf2056369dde9ac0e570ee79b1a07f25fd89d7b6d6a91e46e3a4d48e497e117888ccbdeff7ed21efeb812eb4b3ea15585c82793888eab26848b38c94a7b1ca676c0cbe6fea220f17ceb11ed411702ab77abc069d336877820edb217d4f6a9eae6fd9ddf8c19376e3da27a945c091f56546f56e693a5e48e137e396f3c1365e4f67df0fe35a0f3c9861f28e59744e2a7a1759f3a7b90308a9b988456f3123705ee5a1c26dc7fe97958777bc89c43a546ff321d6e836e1dd72ca6b942a1db0e793ed9c759887c4ca03ed248152abb2f5d55bbd861496bdad399e4cf115c3327b364763172afa24c61459c9b820ce51c18bd9a2a2d833aaad9381e1aae3bb435c7acf2acb753e6c7786272eea9c1d977c4ee818d4e90f1581dffc8259dab92aede74b6fef93dab8fb854f2c58f1aa6fa1d3d83dd9947e1a3377fbe83a441f66dcad5cd46cfbbe0ed3e216aa83dd7feff913b417bb59dd5bcb6e2dc58d6cb4d0202e634e89cc757aa9fbaa3187cead794aad6527d56d9fd02e721f13c8761de887dd53be6d736979dee4ca8af8072fd1ab82122dcd0491a1653f86fd276b67314ddc8d27a1d3cf902b73bb3a3d05fe6216505dfa5e793961caa571cac7a8ff4c7e8373a4c720c784cfb45ee20e2cc69e09cea39f3bbf1776733cba51f95b49539ed459ee9238f3b9485b01a14e9be76935f449c6f9b34f42a26d54b672557a1abe442d0158a54a2f96bdfb48bfe3cc98cccf6956e18a21787de297c2df74cab16fbc201b43658b926b96845dacf989e9798668e9181947a1c17a9a2c7ec08f68d0381b29fc5ed57b95052d68bd46648af20b610e3d87ef79e78c5fa2e7f11ce8ece74eae3b4ec73932c233485e31ed265754c55f032ebdde97cd1e5265036e94d53b116de577f49f6e648eaace49b77159ecedabd24865717546b2a1df91937dffe17145711c84656a316bcc7c249c32bfaf5505ca7958a9f58aee5818af44b41abd13ff0bcf214ef6bd03f39a049e19d7511629f1d92a9b71fa21bfc84a165d9b049b5b534e5412341dedc7aceec17e09d9bfde693befeb8674741de01123266b5c3d2c90ed78ab9c83b5c147cbe5e77565cc5697e3e2291ec87af1c184288b022194d7261de020f98e297f4c792bf6c1ece490d23071fdac2c3e69307a868872c1545152cac991a6aa1e1630966643605027e2dc46b554736abe1149452392211074fd87d956425c4d51fd49da5394482fbb879eabc44c9c8f2929a9016abc6af2baf6985c6c625eb2e2e6c13ce556cdf41726bbebf032bba3b5a99049de4db14bbe8a68ecd12a2fad88642d77065296943dafec60db87781a178acfc5cbb390d24d888ee847734f80c4f0ed1df527c887f1af79a9fe3f47e1069eae55f3c55542829ab1c5a34d2d3958d4e539cca4913d787dd1c12535c08d1fdb23709d8135f422b932de6f633a849654f8263935b5f7bc6881136afce7967a8dd62e946daa113bd9abef4b9825a7a7199257623129291edb2b427fddcd1ded2a1912616f7856ed8a71252e3bed81e28ca162aed4865b5374a7594d93f1bbad615a3972c5c42f9823561f5a972b88afc69c18477b094e052994ce4a2e15544a41e882b0abd63e5b6becd48e17ba23948512ee6d15b69c69ceee976bf5ade3b809bfb98991ea3dc80b222492a9b785ab7db276b9f15e7f2bad452e56818d292be92d2766f5e111a57c7851881334e499709353b8752595ad49f68c4caf84f7c76a715ed225cab28d2aa4b44e48b6dcb6c9ee2d6809c521f29e461837379719d732d9e27cec63aa3b9ad9fe95cf5c44fd5d65eabfdc5cb983db05c19a25b9691c4eaa66cf2d3d28b422eb66abe57eb7fa3161b8b12e3e6b9808ae8144373cf1a7e516546fb6f2d85c13db297eadeee2a6c07071634312af219adcc5223ca2570f66d716d549d418c653498e2e46af3186bf6457e355b8f8127ed36a460d784f5c975252a74bffe635486b5e2b57f31efddc7462b788b2ffc42d296a61b8b6ae37861de75e82fdd4fd46de3d2f8e673eb1d06bd2bf1affd628b2f23db75c0546cd5a93d1e5418fc75548cc354f21da1d256a4a38b98387dd2e3b1d64af6a541757d65c9b2d148bbee9146c78c50691537fdaae0acc468273d3c245aad821453f90cf2f9f1dc8d98a56976aec917a10afdbdc81a927285d8a317eb2d01a9e79252863211f77ddd6e15c1944f2d39673f74ec1d4166cfc4bd2f593f31f67f84fd61fea2424bf4ee77d11e60a5b2b8570e860b3491d6ffcf7c569bdc8be366dfacbce1c84a9ff32a5b8d57b7ba9ce137859e524177e336ee44eca9d34db51464c5f36215d9cf42dfc3ca89a0e911b18f325ebb462fa517cd555a2346ebdef35543a9ee180a1ff9574fed0ecb339a2c4dd7c680a483bc5c2784bc4e79a58bea4c66bd9e4893e633a6e172d42f6165df76573b560d0224992281ddc5f0e340bd90825790c0a62152fb2c1e2cd150e6cc1788b8915011ff758acda0b9da7b467b5b17ccdf84e0c7e3acbcd1ca1a11278e17729f5c24c2c7ecf0362e112932f19be2abe811862c44d7e13d3da34e56ac4b1866f1df16dd2ca491de1d6cd97a9ea98b8e05df7fbee8facdefae14e8de2e5f762275f974f54dd993f3c15fd2d79708cb7ccd434b5693595a212b3d8f0c3cf2d30d1c9737a3ee8ef18b855e3c61581b0263d53619a3e313e8242875ca4f026c723e8da477c77871dfb9223ba4d78264e3c1636041722bcd7f654df53bcf27fd2419d210f04542d2a44788a8a19ff1e788c4eb82c5c7ebdbbfbcd698f751354cfd3de89f0d37b74d64d22baa6d1e1601f725799524895ab54305ac8e92c3b3d892baa91fcac3617d1cef30edb820ce703c1e4b1f4a8a9ed99934e272d877cd01798948430b3a36e4ba5319a81cbab842ade1b7766b6aac4369454837452b3745f2026e8b220fec65f9e529fda1263014f6ebe8dbbe28413f68a066464642321499e4b21139cf69a01948b5f8d97719ae38e50bc8befe73ebb54651366b644714fad72a62c7ddb9c8ad8e2e8b1a9210f68beb9de179883fa695eaaa516c722cc6cc355354758a2174e28511d82c7c1bebf97c5a1fa76e266ec99011c19189e5dd28f557844132413515ca172055befb7d86356d3469232fea61e4157457b83bde6b9738c6611962b06cca95c6e3cc996f479774da92477071ae9b8f3c6d5386285bf56f761caf6f6f32d8ab9a58f41b8a8e353c8dde56109ae11672802a87edc11f239f745fdcdbbd1eb71985f68a942737e5d4ac7b715fc31682872115b504fe96243c96a744c49783c84bea8a62631be2d9c2db777c2f2985bc8abc6fdc7453a3a46fcb8b2852eabbe482d4c56f2722cb7587378ad8ea262f8ddc3bac6ca26ec5e42c46d4c9bed1d665602304b98de4770936ca886eb81e4ac8ce51262c47de2433adf62185888ee812dd1bba7bae3b87801dcab4ac83c1309292865b84d5e71fb95f0be9fe5165084c627ab35aa956557579d287187c4c864505c6ed1881e343ca61d6c226bf926a6e635d9dee15d79f085d091c05714ea827420bc725ddb1be4cef86195d5544eb97f168ccdf6e692dbc8863f36e6433ccf7db7c42e49f926a8abbcc810c54d9af0f2168bd7b42dedd9293651a87743e6ce4a727e4cecf5fa99c923fc096a6223239f585a8c31164f2166bcbc1bd9354d82a55fd358e75eed8afe589cf787e58da0db0bd3d8bb0b178f64e73571f6a4ff626a7661be911b55e5efe2cd961f61153c91171e545fbbb79d6be110edf6a1114bfaa2d336c5c556c780804f5189f9997272305ea4df5e1021ccd6a594b6f5dd7586f4d1c4196ba19acf4d04fdf124a683eeeefce1d9df4f63c1183ac70cde213d74b7c8833b793e0e38aac92791a4a7b55ae3c3ca5b6b7db3eb6d37fe98fd541a6f452dd309dfedbed35ab9deee1a183a7d42acbce37f4fcaf3c54cb268377181d1c422e16ff8c83bca189374fd57e247b4ac1a79bdd478ec797ce816ee8adbcceea9cfedb88fb5e8b54243b52f553bee622217fe5f47e471f623e7dc36cb2199272a8751654cfa8409ea1', encoding='utf8'))


    # db_obj.analyze_database_structure()  # WORKS
    # db_obj.find_otype('car')  # WORKS
    # db_obj.add_id_to_selection(310964869)  # WORKS
    # db_obj.export_to_json('export.json')  # WORKS
    # db_obj.import_from_json('export.json')  # WORKS
    # db_obj.save_all_data()  # WORKS
    # db_obj.calculate_perimeter2(518856625) # WORKS
    db_obj.print_basic_statistics()

    # TODO Add view all object types