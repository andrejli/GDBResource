from DataStructure import *
import SimpleEditor
import cmd
import os
import sys
from CONFIG import EDITOR, EXT_DB
if EXT_DB == 'redis':
    import redis
from Views import *
from Fulltext_Digger import FulltextDigger
from Encryption import *


class GdbResourceConsole(cmd.Cmd):
    def __init__(self):
        super(GdbResourceConsole, self).__init__()
        self.database = GDBResource(filename='db.json')

    @staticmethod
    def parse(arg):
        """Convert a series of zero or more numbers to an argument tuple"""
        return tuple(map(int, arg.split()))  # splits integer argument into tuple

    @staticmethod
    def parse_string(arg):
        """Convert a series of zero or more numbers to an argument tuple"""
        return tuple(map(str, arg.split()))  # splits string arguments into tuple

    @staticmethod
    def enter_data():
        """
        Method calls internal editor to enter basic data within database
        :return:
        """
        record_text = SimpleEditor.ContainerEditor()
        return record_text.__repr__()

    def edit_in_external_editor(self, id_data: str):
        """
        Method checks if datafile has valid length
        :param id_data:  checks if data file exist
        :return:
        """
        if len(id_data) == 37:  # if data contains existing data filename
            comd = EDITOR + ' ' + id_data
            os.system(command=comd)
        else:
            self.enter_data()  # Use included simple editor
        return

    @staticmethod
    def edit_file_in_vim(filename: str):
        """
        Method opens via os.system command external editor to edit data file
        :param filename: filename to edit
        :retlurn:
        """
        open_cmd = EDITOR + ' ' + filename
        os.system(command=open_cmd)
        return

    # A D D   N E W   O B J E C T S   A N D   L I N K S   T O   D A T A B A S E

    def do_nr(self, args):  # ADD NEW RECORD
        """
        Initializes new database record
        :param args:    object_type(string)
                        data(string)
                        state of confirmation(Boolean)
        :return:
        """
        conf_boolean = False  # default value of confirmation parameter
        obj_type = input('OBJECT TYPE')  # input object type parameter
        data = self.enter_data()
        conf = input('CONFIRMATION STATE(y/n')  # input confirmation parameter
        if conf == 'y':  # if yes DO
            conf_boolean = True  # change default value to True
        self.database.db_object_record(confirmed=conf_boolean, object_type=obj_type, data=data)  # write record to db

    def do_nl(self, args):  # ADD NEW LINK
        """
        Initializes new database link between objects
        :param args:    obj1(9digit ID number)
                        obj2(9digit ID number)
                        object_type(string)
                        data(string)
                        state of confirmation(Boolean)
                        reversed link(Boolean)
        :return:
        """
        conf_boolean = False  # default value of confirmation parameter
        reverse_boolean = False  # default value of reverse parameter
        # obj_type = input('OBJECT TYPE')
        if len(self.parse_string(args)) != 2:
            print('No valid parameters given !!!')
            return
        data = input('ENTER DATA')  # input data
        conf = input('CONFIRMATION STATE (y/n) :')  # input confirmation parameter
        if conf == 'y':  # if yes DO
            conf_boolean = True  # change default value to True
        rev = input('REVERSE LINK (y/n) :')  # input reverse parameter
        if rev == 'y':  # if yes DO
            reverse_boolean = True  # change default value to True
        self.database.db_link_record(object1_id=self.parse(args)[0], object2_id=self.parse(args)[1], data=data,
                                     reverse=reverse_boolean, confirmed=conf_boolean)  # write link to database

    # S E L E C T I O N   C O M M A N D S

    # TODO Add records to SELECTION
    # TODO Remove record from SELECTION
    # TODO Export SELECTION to .json

    # E D I T   O B J E C T S  A N D  L I N K S

    def do_eid(self, args):  # EDIT ID
        """
        Method finds id in database loads it to result, removes id from database and
        saves new modified record to database with same id_code
        :param args: id_code(9digit,
        :return:
        """
        if self.parse(args) == tuple():  # if argument doesnt exist DO
            print('id_code is required')  # print msg to console
            return False  # end command
        if len(str(self.parse(args)[0])) != 9 or str(self.parse(args)[0]).isdecimal() is not True:  # if argument doesnt exist
            print('id_code is 9digit long decimal')  # print msg to console
            return False  # end command
        id_code = self.parse(args)[0]  # parse id_code from args
        result = self.database.full_match_id_find(id_code=id_code)  # finds id code in db
        print(result)  # print result to console
        if result is None:
            return False
        result_dict = result[0]  # extract dictionary from list
        self.database.remove_id(id_code)  # remove id from db
        if result is not False:  # if result exists DO
            if result_dict['object_type'] != 'link':  # if result is record
                conf_boolean = result[0]['confirmed']  # read confirmed from dictionary
                obj_type = result[0]['object_type']  # read object type from dictionary
                data = str(result[0]['data'])
                self.edit_in_external_editor(id_data=data)  # input new data
                conf = input('CONFIRMATION STATE(y/n')  # change confirmed parameter
                if conf == 'y':  # if yes do
                    conf_boolean = True  # change default value to True
                # IF CONFIRMED IS TRUE CANNOT BE MODIFIED TO FALSE AGAIN
                self.database.db_object_record(id_code=id_code, confirmed=conf_boolean, object_type=obj_type, data=data)
                # create new record with modified data or confirmed
            if result_dict['object_type'] == 'link':  # if object type is equal link
                obj1 = result_dict['object_id1']  # loads obj1 from dictionary
                obj2 = result_dict['object_id2']  # loads obj2 from dictionary
                conf_boolean = result_dict['confirmed']  # loads confirmed from dictionary
                reverse_boolean = result_dict['reverse']  # loads reversed from dictionary
                # obj_type = input('OBJECT TYPE')
                data = input('DATA')  # modify data
                conf = input('CONFIRMATION STATE (y/n) :')  # modify confirmed
                if conf == 'y':  # if yes DO
                    conf_boolean = True  # change confirmed to True
                rev = input('REVERSE LINK (y/n) :')  # mod reversed
                if rev == 'y':  # if yes DO
                    reverse_boolean = True  # change value to True
                if rev == 'n':  # if no DO
                    reverse_boolean = False  # change value to False
                self.database.db_link_record(id_code=id_code, object1_id=obj1, object2_id=obj2, data=data,
                                             reverse=reverse_boolean, confirmed=conf_boolean)  # write link to db
                return True  # returns True  # TODO Bug Everytime when link is edited quits programm

    def do_rid(self, args):  # REMOVE ID
        """
        Method finds id in database loads it to result, removes id from database and
        saves new modified record to database with same id_code
        :param args: id_code,
        :return:
        """
        id_code = self.parse(args)[0]  # parses id code from arguments
        result = self.database.full_match_id_find(id_code=id_code)  # finds id and loads to list NO DUPLICITY
        print('FULLMATCH', result)  # prints to console
        if result is not False:  # if code was found proceed
            # Remove associated links and vectors
            links2remove = list()  # define variable as an empty list
            all_links = self.database.find_object_type(object_type='link')  # find all links in db
            print(all_links)  # prints list with links dictionaries
            for i in all_links:  # loop tru all links
                if id_code == i['object_id1'] or id_code == i['object_id2']:  # compare if id code is present in the link
                    print('LINK TO REMOVE', i['id'])  # control print to console
                    links2remove.append(i['id'])  # add link to list of links to remove from db
                else:
                    pass
            print(links2remove)  # prints out to console all links to remove
            [self.database.remove_id(i) for i in links2remove]  # comprehension to remove all associated links
            self.database.remove_id(id_code)  # remove id from database
            self.database.db_root_record()  # calculate new root record
            self.database.save_all_to_json(file=self.database.filename)  # save all to json file

    #  F I N D  O B J E C T S  A N D  L I N K S

    def do_fid(self, args):  # FIND ID IN DATABASE
        """
        Find id in objects, links and fulltext in data
        :param args:
        :return:
        """
        if len(self.parse(args)) != 1:
            print('No valid parameters given !!!')
            return
        result = self.database.find_id(id_code=self.parse(args)[0])  # finds id in db
        print(result)

    def do_ft(self, args):  # FIND TEXT IN DATABASE
        """
        Find text in data
        :param args:  text(string)  WITHOUT SPACE !!!
        :return:
        """
        text2find = str()
        if len(self.parse_string(args)) != 1:
            for i in range(0, len(self.parse_string(args))):
                text2find += self.parse_string(args)[i] + " "
            text2find = text2find[:-1]  # Removes last added SPACE
        else:
            text2find = self.parse_string(args)[0]
        # TODO Automaticcaly find ID of records and append them to result
        result = self.database.find_text(text=text2find)  # finds text in data
        print("RESULT OF FULTEXT SEARCH:\n",result)
        return

    def do_fot(self, args):  # FIND OBJECT TYPE
        """Find object type
            :param args:  object type(string)  WITHOUT SPACE !!!
            :return:
                """
        if len(self.parse_string(args)) != 1:
            print('No valid parameters given !!!')
            return
        self.database.find_object_type(object_type=self.parse_string(args)[0])  # finds object type in db

    def do_lsdb(self, args):  # LIST ALL DATABASE RECORDS AND LINKS UNSORTED
        """
        List all database links and objects to console unsorted
        """
        standard_view(db=self.database.DBTree)
        # self.database.analyze_database_structure()  # analyse db structure
        # self.database.print_basic_statistics()  # print statisstics
        # self.database.view_all()  # prints all objects and links

    def do_lsot(self, args):  # LIST ALL OBJECT TYPES STORED IN DB
        all_ot = self.database.view_all_object_types()
        [print(i) for i in all_ot]

    # A D V A N C E D   F I N D   P R O C E D U R E S   A N D   M E T H O D S

    def do_near(self, parameters):  # FIND NEAR OBJECTS
        """
        Method calculates first perimeter of asscociated object
        :param parameters: id code - 9digit decimal number
        :return:
        """
        if len(self.parse(parameters)) != 1:
            print('No valid parameters given !!!')
            return
        id_code = self.parse(parameters)[0]
        result = self.database.near_objects(id_code=id_code)
        print('NEAREST OBJECTS : ', result)
        # OBJECTS NOT FAR AWAY
        result2 = self.database.not_far_objects(id_code=id_code)
        for i in result:
            result2.remove(i)
        print('OBJECTS NOT FAR', result2)

    def do_ql(self, parameters):  # ARE TWO OBJECTS LINKED ?
        """
        Method compares all associated links of two objects. If intersection of two sets is more than 1
        returns logical True
        :param parameters: two id numbers from database
        :return:  logical True or False
        """
        # TODO DOESN'T WORK ??? TEST WAS SUCCESSFUL
        if len(self.parse(parameters)) != 2:
            print('No valid parameters given !!!')
            return
        result = False
        id1 = self.parse(parameters)[0]
        id2 = self.parse(parameters)[1]
        result = self.database.association(id1=id1, id2=id2)
        print(f'OBJECTS {id1} AND {id2} ARE LINKED :', result)

    # A D M I N   C O M M A N D S
    def do_init(self, args):  # INIT NEW EMPTY DATABASE
        """ Method initializes empty database in memory and save to defined .json file"""
        if len(self.parse_string(args)) != 1:
            print('No valid .json file name !!!')
            return
        # TODO Require Admin Password
        if self.parse_string(args)[0] != '':  # if filename is given as argument
            self.database.filename = self.parse_string(args)[0]  # changes database name to filename
        self.database.init_new_database()  # inits new database with empty root record

    def do_drop(self, args):  # DROP ???
        """ Method drops(remove) all associated records,links and .data
        files from database and cwd"""
        # TODO Require Admin Password
        self.database.drop_database()  # drop all records and links
        print('REMOVE ONLY DATA FILES associated with DB.Tree')
        for f in self.database.DBTree:
            if len(f['data']) == 37:
                cmd = 'rm ' + f['data']
                print(cmd)
                os.system(command=cmd)
        return True

    def do_drop_all(self, args):  # DROP ALL DBTREE
        """ Method drops(remove) all records,links and .data
        files from cwd"""
        # TODO Require Admin Password
        self.database.drop_database()
        index = FulltextDigger.catwalk()  # makes index of all data files in cwd
        # self.database.drop_database()  # drop all records and links
        print('REMOVE ALL DATA FILES IN DIRECTORY')
        for f in range(0, len(index)):
            cmd = 'rm ' + index.pop()
            print(cmd)
            os.system(command=cmd)
            # TODO Issue program terminates and exits Cmd
        return

    def do_switch(self, args):  # SWITCH TO ANOTHER DBTREE
        """
        Switch to another database
        :param args: filename of existing database
        :return:
        """
        if len(self.parse_string(args)) != 1:
            print('No valid .json file name !!!')
            return
        db_file = self.parse_string(args)[0]  # parses args as db filename
        self.database = GDBResource(filename=db_file)  # loads file to db

        # TODO Sync primary db with db server (Redis)

    def do_encrypt(self, args):  # ENCRYPT ALL DATA
        """
        Encrypt all database files with Simple PWD
        """
        pwd = input("PASSWORD :")
        files = FulltextDigger.catwalk()
        # TODO FILE LOAD TO memory
        # TODO FILE ENCRYPT WITH Password
        # TODO FILE SAVE TO FILE
        pass


    @staticmethod
    def do_exit(parameters):  # EXIT CMD CONSOLE
        """
        Method exits database
        :param parameters: None
        :return: None
        """
        print('DONE')
        quit()

    @staticmethod
    def do_clear(parameters):  # CLEAR TERMINAL DISPLAY
        """
        Clears teminal display
        """
        if sys.platform == 'win32':
            os.system(command='cls')
        else:
            os.system(command="clear")
        return



if __name__ == '__main__':
    GdbResourceConsole().cmdloop()
