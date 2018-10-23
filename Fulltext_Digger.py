import re
import os


class FulltextDigger(object):
    """
    Class loops tru all data files and finds all stored tags in format:
     <otype data>/return sign must be present!!!!
     makes index of all files and their tags in memory.
     Compares each other and find equal tags in data files.
     Then transforms this findings into new links with 'alias' data.

     FULLTEXT DATA WORKS ONLY WITH DECRYPTED DATA FILES.
     ENCRYPTED DATA CAN'T BE INDEXED BY PERSON WITHOUT PERMISSION !!!
    """
    def __init__(self):
        self.final_index = dict()  # define final dictionary as empty variable
        # self.tags2find = ('#NAME', '#SURNAME', "#DOB", '#ID')
        self.catalog = self.catwalk()  # Walk tru all data files with os.walk
        for r in range(0, len(self.catalog)):  # loops tru all data files
            file_value = self.catalog.pop()  # pop file from set
            print(file_value)  # control print to console
            # start method to fulltext search all decrypted files
            self.final_index[file_value] = self.fulltext_search(filename=file_value)
            self.file_index = set()  # reset value passed already to final index dictionary
        self.represent_gathered_tags()

    @staticmethod
    def catwalk():
        """
        Method walk tru all currently working directory (cwd) files finds all .data files
        with 32digits long name and pair with actual path to file.
        :return: set of .data files with actual routes
        """
        cat_result = set()  # defines result as set
        directory = str(os.getcwd())  # defines directory as cwd
        w = os.walk(directory)  # defines w as result of walk method from os.module
        for routes, dirs, files in w:  # loops tru output of routes and dirs walk method
            for k in files:  # loops tru files result of walk method
                if k.count('.data') >= 1 and len(k) == 37:  # set conditions .data and 37digits total length of filename
                    cat_result.add(str(routes) + '/' + k)  # add route with filename to result
        print(cat_result)  # control print result
        return cat_result  # return set of values

    def fulltext_search(self, filename: str, ):
        """
        Method loads .data file and search for tags with regular expression of Python3 module
        When find tag < >\n adds to local file index
        :param filename: .data filename with path
        :return: set of tag values in file
        """
        # text_buffer = str()
        with open(filename, mode='r', encoding='utf8') as f:  # open file in text read mode
            text_buffer = f.read()  # read all text from file
            # print(text_buffer)  # control print all buffered text
        result_count = text_buffer.count('<')  # control search of tags in file (finding also repetiteve tags)
        print(result_count)  # control print to console
        result = re.findall(pattern=r'\<(.*)\>\n', string=text_buffer)  # using re.findall method to find all tags
        self.file_index = set(result)  # adding result to set to get rid of repetitive tags
        print(self.file_index)  # control print of result stored in class variable
        return self.file_index  # obsolete but good

    def parse_tag(self, tag_string: str):
        """
        Method parses tag to otype - object type AND data in string
        :param tag_string:
        :return: returns dictionary with otype and data
        """
        result = dict()
        word_list = tag_string.split(' ')
        result['otype'] = word_list[0]
        data_string = str()
        for i in range(1, len(word_list)):
            data_string += word_list[i] + ' '
        result['data'] = data_string[:-1]
        return result

    def represent_gathered_tags(self):
        for i in self.final_index:  # TODO make print all values
            print(i)
            for tags in self.final_index[i]:
                print(tags)


    def compare_data(self):
        # TODO Make it happen :)
        pass


if __name__ == '__main__':
    obj = FulltextDigger()
