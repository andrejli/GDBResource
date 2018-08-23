from DataStructure import *
import cmd


class GdbResourceConsole(cmd.Cmd):
    def __init__(self):
        super(GdbResourceConsole, self).__init__()
        self.database = GDBResource(filename='db.json')

    @staticmethod
    def parse(arg):
        """Convert a series of zero or more numbers to an argument tuple"""
        return tuple(map(int, arg.split()))

    @staticmethod
    def parse_string(arg):
        """Convert a series of zero or more numbers to an argument tuple"""
        return tuple(map(str, arg.split()))

    # A D D   N E W   O B J E C T S   A N D   L I N K S   T O   D A T A B A S E

    def do_nr(self, args):  # ADD NEW RECORD
        """
        Initializes new database record
        :param args:    object_type(string)
                        data(string)
                        state of confirmation(Boolean)
        :return:
        """
        conf_boolean = False
        obj_type = input('OBJECT TYPE')
        data = input('DATA')
        conf = input('CONFIRMATION STATE(y/n')
        if conf == 'y':
            conf_boolean = True
        self.database.db_object_record(confirmed=conf_boolean, object_type=obj_type, data=data)

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
        conf_boolean = False
        reverse_boolean = False
        # obj_type = input('OBJECT TYPE')
        data = input('DATA')
        conf = input('CONFIRMATION STATE (y/n) :')
        if conf == 'y':
            conf_boolean = True
        rev = input('REVERSE LINK (y/n) :')
        if rev == 'y':
            reverse_boolean = True
        self.database.db_link_record(object1_id=self.parse(args)[0], object2_id=self.parse(args)[1], data=data,
                                     reverse=reverse_boolean, confirmed=conf_boolean)

    #  F I N D  O B J E C T S  A N D  L I N K S

    def do_fid(self, args):  # FIND ID IN DATABASE
        """
        Find id in objects, links and fulltext in data
        :param args:
        :return:
        """
        self.database.find_id(id_code=self.parse(args)[0])

    def do_ft(self, args):  # FIND ID IN DATABASE
        """
        Find text in data
        :param args:  text(string)  WITHOUT SPACE !!!
        :return:
        """
        self.database.find_text(text=self.parse_string(args)[0])

    def do_fot(self, args):  # FIND ID IN DATABASE
        """
        Find object type
        :param args:  object type(string)  WITHOUT SPACE !!!
        :return:
        """
        self.database.find_object_type(object_type=self.parse_string(args)[0])

    def do_lsdb(self, args):  # LIST ALL DATABASE RECORDS AND LINKS UNSORTED
        """
        List all database links and objects to console unsorted
        """
        self.database.analyze_database_structure()
        self.database.print_basic_statistics()
        self.database.view_all()


if __name__ == '__main__':
    GdbResourceConsole().cmdloop()
