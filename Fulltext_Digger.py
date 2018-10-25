import re
import os
from DataStructure import *

class FulltextDigger(object):
    """
    Class loops tru all data files and finds all stored tags in format:
     <otype data>/return sign must be present!!!!
     makes index of all files and their tags in memory.
     Compares each other and find equal tags in data files.
     Then transforms this findings into new links with 'alias' data.

     FULLTEXT DATA WORKS ONLY WITH DECRYPTED DATA FILES.
     ENCRYPTED DATA CAN'T BE SEARCHED BY PERSON WITHOUT PERMISSION !!!
    """
    def __init__(self):
        # D E F I N E   C L A S S   V A R I A B L E S
        self.final_index = dict()  # define final dictionary as empty variable
        self.file_index = set()  # define index of files as an empty set
        self.alias_index = list()
        # C R E A T E   C A T A L O G   O F   D A T A   F I L E S
        self.catalog = self.catwalk()  # Walk tru all data files with os.walk
        # M A I N   P R O C E D U R E  ==>
        self.scrape_data_files()
        # R E P R E S E N T   R E S U L T
        self.represent_gathered_tags()
        # print('FIND FULLMATCH ALIASES')
        # [print(i) for i in self.alias_index]

    def scrape_data_files(self):
        """
        Method loops tru data file catalog and pops files to fulltext search.
        Collected tags are stored as list values to dictionary with filename
        as key. Result of this procedure is class dictionary variable self.final_index
        :return: None
        """
        for r in range(0, len(self.catalog)):  # loops tru all data files
            file_value = self.catalog.pop()  # pop file from set
            print(file_value)  # control print to console
            # start method to fulltext search all decrypted files
            self.final_index[file_value] = self.fulltext_search(filename=file_value)
            self.file_index = set()  # reset value passed already to final index dictionary
        return

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

    @staticmethod
    def parse_tag(self, tag_string: str):
        """
        Method parses tag to otype - object type AND data in string
        :param tag_string:
        :return: returns dictionary with otype and data
        """
        result = dict()
        word_list = tag_string.split(' ')
        result['otype'] = word_list[0]
        data_list = list()
        for i in range(1, len(word_list)):
            data_list.append(word_list[i])
        result['data'] = data_list
        return result

    def represent_gathered_tags(self):
        """
        This method is used to visualize result of fulltext search to console.
        Class variable self.final_index is parsed and presented in console in
        readable form.
        :return: None
        """
        for i in self.final_index:
            print(i)
            for tags in self.final_index[i]:
                print(tags)
                print("COMPARE FULLMATCH TAGS IN DATA\n")
                self.compare_data(filename=i, tag=tags)
                print("COMPARE PARTIAL TAGS IN DATA\n")
                self.compare_parsed_data(filename=i, tag=tags)
        return

    def compare_data(self, filename: str, tag: str):
        """
        Method takes tag from self.final_index and compares with all other
        tags in self.final_index. If value is Equal prints out to console.
        :param filename: filename of actual .data
        :param tag: tag to compare with other tags
        :return:
        """
        for i in self.final_index:
            for tags in self.final_index[i]:
                if tags == tag and i != filename:
                    print('MATCH  ', filename, '\t', tag)
                    self.alias_index.append([filename, tag])
        return

    def compare_parsed_data(self, filename: str, tag: str):
        """
        Method takes tag from self.final_index and compares with all other
        tags in self.final_index. If value is Equal prints out to console.
        :param filename: filename of actual .data
        :param tag: tag to compare with other tags
        :return:
        """
        # TAG preparation
        tag1_words = self.parse_tag(filename, tag)
        print(tag1_words)
        for i in self.final_index:  # loops tru data files
            for tags in self.final_index[i]:  # loops tru tags
                tag2_words = self.parse_tag(i, tags)
                mapped_booleans = map(lambda x, y: x == y, tag1_words["data"], tag2_words["data"])
                result = list(mapped_booleans)
                for l in result:
                    if len(result) == 1:
                        # S P E C I F Y  P H O N E  T A G
                        if tag1_words['otype'] == "PHONE" and result[0] is True:
                            print('PARSED TAGS MATCH', filename, tag, '\t', i, )
                    if len(result) >= 2:
                        # S P E C I F Y  P E R S O N   T A G
                        if tag1_words['otype'] == "PERSON" and result[0] is True and result[1] is True:
                            print('PARSED TAGS MATCH', filename, tag, '\t', i,)

                    if result.__contains__(True):
                        print('SENSITIVE MATCH TRIGGERED')
                    # TODO Add other Tags Logic Specify
                # compare words with map function
                # self.alias_index.append([filename, tag])
        return


if __name__ == '__main__':
    obj = FulltextDigger()
