import os
import hashlib


class ContainerEditor(object):
    """
    Class opens small editor in console to enter document such as report or
    more complex info to database GDPResource
    """

    def __init__(self):
        self.plaintext = list()  # define text as empty variable (list of rows)
        self.editor_message = 'You are entering Simple editor to edit and store informations in GDPResource database\n' \
                              'for more info write :wq to quit' \
                              '\n PRESS ENTER TO CONTINUE'
        self.filename = str()
        self.__help__ = 'SIMPLE EDITOR COMMANDS:\n' \
                        ':q to quit\n' \
                        ':wq to save and quit\n' \
                        ':h to enter help\n'

        self.flag = True
        # M A I N   L O O P
        os.system('clear')
        print(self.editor_message)
        input()
        while self.flag is True:  # infinite loop
            print(self.editor_message)
            self.view_text()  # view given text in console
            self.input_row()  # input new row
        self.__repr__()

    def input_row(self):
        """
        Method inputs new row to class variable self.plaintext
        :return: row string (awaiting a command string)
        """
        row = input()  # built in function input string variable to console
        self.check_command(row)  # check if row string is not command string
        self.plaintext.append(row)  # append row string to list of rows stored in self.plaintext
        return row  # returns row

    def check_command(self, command):
        """
        Method awaits and serves as event handler for commands given from editor
        :param command: command string (vim compatible)
        :return: None
        """
        row = command  # defines row as a commnad given by input to console
        # if row == ':q':  # when command string equal this string DO:
        #     quit()  # quit from editor
        if row == ':wq':  # when command string equal this string DO:
            self.save_all()  # saves all to file
            self.flag = False
        # if row == ':h':
        #     self.flag = False  # TODO Do it so you coudnt quit editor to see help
        #     print(self.__help__)

    def view_text(self):
        """
        Method performs render of editor screen i terminal
        :return:
        """
        os.system(command='clear')  # system command to clear screen in Linux
        # TODO Make Win and Darwin compatible
        [print(i) for i in self.plaintext]  # comprehension in Python to print all rows from self.plaintext
        return  # return to main

    def convert2bytes(self):
        """
        This method converts list of rows stored in self.plaintext to string.
        Then converts string with linebreaks to bytes for further operations
        :return: returns all text from self.plaintext as bytes
        """
        string = str()  # defines string as empty string variable
        for i in self.plaintext:  # loops tru self.plaintext and DO:
            string += i + '\n'  # add row plus linebreak symbol to string
        # print(string)
        result = bytes(string, encoding='utf8')  # encode string to final result bytes
        return result  # return bytes with all text stored in variable self.plaintext

    @staticmethod
    def hash_it(text: bytes):
        """
        Method calculate md5 hash string from bytes
        :param text: text in bytes
        :return: string md5 hash algorithm
        """
        sha = hashlib.md5()  # Default algorithm
        sha.update(text)  # add text and update claculation
        result = sha.hexdigest()  # digest hexadecimal string
        return result  # retuns strin to main

    def save_all(self):
        """
        Method saves all data to file as binary
        :return: if success returns True
        """
        text1nbytes = self.convert2bytes()  # convert text to bytes
        self.filename = str(self.hash_it(text1nbytes)) + '.data'  # defines filename
        with open(file=self.filename, mode='wb') as f:  # opens file in write binary mode
            f.write(text1nbytes)  # write bytes to file
            print('SAVED TO', self.filename)  #
        return True

    def __repr__(self):
        return self.filename


if __name__ == '__main__':
    obj = ContainerEditor()
