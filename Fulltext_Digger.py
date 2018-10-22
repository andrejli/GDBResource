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
        self.tags2find = ('#NAME', '#SURNAME', "#DOB", '#ID')
        self.catalog = self.catwalk()  # Walk tru all data files with os.walk
        for r in range(0, len(self.catalog)):
            file_value = self.catalog.pop()
            print(file_value)
            self.final_index[file_value] = self.fulltext_search(filename=file_value)
            self.file_index = set()
        [print(i) for i in self.final_index]  # TODO make print all values

    def catwalk(self):
        cat_result = set()
        directory = str(os.getcwd())
        w = os.walk(directory)
        for routes, dirs, files in w:
            for k in files:
                if k.count('.data') >= 1 and len(k) == 37:
                    cat_result.add(str(routes) + '/' + k)
        print(cat_result)
        return cat_result

    def fulltext_search(self, filename: str, ):
        text_buffer = str()
        with open(filename, mode='r', encoding='utf8') as f:
            text_buffer = f.read()
            print(text_buffer)
        result_count = text_buffer.count('<')
        print(result_count)
        result = re.findall(pattern=r'\<(.*)\>\n', string=text_buffer)
        self.file_index = set(result)
        print(self.file_index)
        return self.file_index

    def parse_tag(self, tag_string: str):
        result = dict()
        word_list = tag_string.split(' ')
        result['otype'] = word_list[0]
        data_string = str()
        for i in range(1, len(word_list)):
            data_string += word_list[i] + ' '
        result['data'] = data_string[:-1]
        return result

    def compare_data(self):
        # TODO Make it happen :)
        pass


if __name__ == '__main__':
    obj = FulltextDigger()
