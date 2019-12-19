#shebang

#imports
import re
import os
import itertools
import hashlib

# main class
from typing import Iterator


class Autotag(object):
    """
    Class takes any utf8 encoded text in any languague to analyze and learn.
    From every word makes SALTED hashstring and stores them into tag files.
    Every time new text is entered compares words with stored words in dictionary.
    Program tries identify existing tags in text. If program don't understand
    word program will be asking user to assign TAG or identify word as part
    of multiword.
    """

    def __init__(self, filename_w_path: str):
        self.file = filename_w_path  # define class variable with processed file
        self.loaded_string = str()  # define class variable with loaded string
        self.splited_string = list()  # define loaded string splited to list
        self.pure_splited_string = list()
        self.all_words_index = dict()  # indexing all collected words
        self.relevant_words = list()  # define collected relevant words
        self.combinations = list()
        # define class variables

        # M A I N   P R O C E D U R E
        self.loaded_string = self.load_content()  # load string from file
        self.splited_string = self.transform_2_words(self.loaded_string)  # transfer string to list of words
        # self.all_sentences = self.transform_2_sentences()
        self.find_tags()  # find if exist already tags in
        self.find_pure_tags()  # extract existing tags
        for i in self.splited_string:  # loops splited strings
            self.pure_splited_string.append(self.remove_end_symbols(i))   # transfer splited string
            # to pure without end symbols
        result_part1 = self.calculate_single_word_hashes()  # add single word hashes
        self.combinations = self.calculate_all_relevant_combinations()  # make combinations of all
        # words starting with Capital or number
        result_part2 = self.calculate_multi_word_hashes()  # add all multi word hashes
        final_result = result_part1.copy()  # copies part 1 to empty dict
        final_result.update(result_part2)  # adds part 2 to merge both parts into final
        [print(i, final_result[i]) for i in final_result]  # print
        # TODO Add all calculated relavant combination hashes to result dictionary
        # self.learn_by_sentences()
        # self.identify_multi_word_names()
        # self.learn_process()

    # F I L E   M A N A G E M E N T

    def load_content(self):
        """
        Method reads content of file to memory as utf8 string
        :return: string
        """
        with open(file=self.file, mode='r', encoding='utf8') as f:
            result = f.read()
        return result

    # T R A N S F O R M A T I O N S  A N D  C O N V E R T O R S

    @staticmethod
    def transform_2_words(text: str):  # TODO check if sorted set would be better
        """
        Method transforms loaded string to list of words
        :return: list
        """
        result = text.split(sep=' ')
        return result

    @staticmethod
    def transform_2_sentences(text: str):
        """
        Method transforms loaded string to list of sentences ENDINNG with DOT
        :return: list of sentences
        """
        result = text.split(sep='. ')
        print('SENTENCES\n', result)
        for i in result:  # Add end symbol of every sentence.
            if result[i][0:-1] != '.':
                result[i] += '.'
        return result

    @staticmethod
    def remove_end_symbols(word: str):
        """
        Method removes end symbols of sentences and like .,!?,
        becaiuse they are irrelevant for hash calculations
        :return: word string
        """
    
        if word[-1] == '.' or word[-1] == '?' or word[-1] == '!' or word[-1] == '!':
            wo_last = len(word)-1
            word = word[0:wo_last]
            # print(word)  # Control print to console
        return word

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

    # T A G S   D E T E C T I O N

    def find_tags(self):
        """
        Method finds existing decorated TAGS in text. If they are found stop Autotagging process.
        :return: Boolean
        """
        for i in self.splited_string:
            if re.search(pattern=r'<\S\S\S*', string=i):
                print(i, '\t', re.search(pattern=r'<\S\S\S*', string=i))
                print('FILE WAS ALREADY TAGED')
                return True
            else:
                return False

    def find_pure_tags(self):
        """
        Method extracts existing tags from loaded text string
        :return: list
        """
        raw_tags = self.loaded_string.split(r'?<>')
        semi_raw_tags = raw_tags[0].split('\n')
        pure_tags = list(filter(lambda x: x != '', semi_raw_tags))
        print(pure_tags)
        return pure_tags

    def extract_known_tags(self):
        pass

    def find_words(self, sentence: str):
        """ Method transfers all words to index of all words"""
        print('CATCHED NAMES :')
        # TODO Check if sorted dict would be better
        for i in range(0, len(self.splited_string)):
            self.all_words_index[i] = self.splited_string[i]
        print(self.all_words_index)
        return

    # H A S H   A L G O R I T H M   C A L C U L A T I O N S

    def calculate_single_word_hashes(self):
        """
        Method filter all words with capital letter at start and calculates hash for them. Also updates class variable
        list of all relevant words
        :return: dict with hash values
        """
        result = dict()
        for i in self.pure_splited_string:
            if i[0].isupper() is True or i[0].isnumeric() is True:
                result[i] = self.hash_it(i.encode(encoding='utf8'))
                self.relevant_words.append(i)
        print(result)
        return result

    def calculate_multi_word_hashes(self):
        """
                Method filter all words with capital letter at start and calculates hash for them. Also updates class variable
                list of all relevant words
                :return: dict with hash values
                """
        result = dict()
        for i in self.combinations:
            # i = i[-1]  # remove SPACE on the end of single combination
            result[i] = self.hash_it(i.encode(encoding='utf8'))
        print(result)
        return result

    def calculate_all_words_combinations(self):
        """
        Method calculates all combinations of all values of words
        :return:
        """
        comb_result = list()
        for r in range(2, 5):
            comb_result += itertools.combinations(self.splited_string, r)
        print(comb_result)
        self.filter_all_relevant_combinations(comb_result)

        # TODO Filter only values of list with all words with capitals

    def calculate_all_relevant_combinations(self):
        """
        Method calculate all relevant words calculations
        :return:
        """
        comb_result = list()
        purified_comb_result = list()
        for r in range(2, 5):
            comb_result += itertools.combinations(self.relevant_words, r)
        print(comb_result)
        comb_result = self.filter_all_relevant_combinations(comb_result)
        for i in comb_result:
            purified_comb_result.append(i[0:-1])
        print('PURIFIED ', purified_comb_result)
        return purified_comb_result

    # F I L T E R S   T O  D E T E C T   R E L E V A N T   M U L T I W O R D S
    @staticmethod
    def filter_all_relevant_combinations(combinations: list):
        """
        Method filters all relevant combinations of words
        """
        Upper_capitals = list()
        result = ''
        counter = 0
        for i in combinations:
            for k in range(0, len(i)):
                if i[k][0].isupper() is True or i[k][0].isnumeric() is True:
                    result += str(i[k]) + ' '
                    counter += 1
                    print(counter, result, '\n')
            if counter == len(i):
                Upper_capitals.append(result)
                print(Upper_capitals)
            result = ''
            counter = 0
        print(Upper_capitals)
        return Upper_capitals



# compare with existing database from json

# if found add matching TAG with RETURN

# TODO Make filter to learning function to not ask stupid questions :)

# if not ask for user

# save hash to matching tag

# reassemble text file in string

# save him to original textfile
# P Y T E S T   T E S T S

def test_remove_end_symbols():
    obj = Autotag('Autotag_test.txt')
    assert obj.remove_end_symbols('Hello.') == 'Hello'


def test_transform2words():
    obj = Autotag('Autotag_test.txt')
    assert obj.transform_2_words(text='Hello World') == ['Hello', 'World']


def test_transform2sentence():
    obj = Autotag('Autotag_test.txt')
    assert obj.transform_2_sentences(text='Hello World. Welcome to Jamaica.') == []


if __name__ == '__main__':
    obj = Autotag('Autotag_test.txt')
