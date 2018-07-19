
SALT = 'KNOWN SECRET'  # TODO Include HMAC
# TODO include Hash string calculation

# DEFINE PLAINTEXT
string = 'Andrej Licko'  # define plaintext string
str_values_list = list()  # define string value list as an empty list
[str_values_list.append(ord(i)) for i in string]  # add integer representation of symbols to list
print(str_values_list)  # print value list
value = 0

# DEFINE PASSWORD
# TODO Prepare password must bu same length as plaintext
string2 = 'Andrej isiel do obchodu a teraz ide domov'  # define plaintext string
str_values_list2 = list() # define string value list as an empty list
[str_values_list2.append(ord(i)) for i in string2]  # add integer representation of symbols to list
print(str_values_list2)  # print value list


class SimpleSubstitution(object):

    def __init__(self):
        """ Simple substitution encryption class for demonstrative and game purposes ONLY
        NOT USABLE IN PRODUCTION
        For best result should be password TRUE random or cryptographic suitable Pseudo Random Generated and same
        length as encrypted plaintext

        """
        pass

    @classmethod
    def encrypt_simple_substitution(cls, plaintext_values: list, pwd_values: list):
        """
        Method to encrypt plaintext simple substitution with simple +. For best result should be password TRUE random
        or cryptographic suitable Pseudo Random Generated and same length as encrypted plaintext
        :param plaintext_values: list of values 0 to 255
        :param pwd_values: list of values 0 to 255
        :return: list of encrypted values 0 to 255
        """
        if len(pwd_values) > len(plaintext_values):
            plaintext_values = SimpleSubstitution.mod_plaintext_length(len(pwd_values), plaintext_values)
        if SimpleSubstitution.check_same_length(plaintext_values, pwd_values) is False: # check if values have same length
            pwd_values = SimpleSubstitution.mod_pwd_length(len(plaintext_values), pwd_values)

        # SUBSTITUTION ENCRYPT OPERATION
        raw_sum = list(map(lambda x, y: x + y, plaintext_values, pwd_values))

        # MOD RESULTS TO VALUES NOT MORE THAN 255
        for i in range(0,len(raw_sum)):
            if raw_sum[i] > 255:
                val = raw_sum[i] - 255
                raw_sum.pop(i)
                raw_sum.insert(i, val)
        print('ENCRYPTED VALUES:', raw_sum, '\n')
        return raw_sum

    @classmethod
    def decrypt_simple_substitution(cls, encrypted_values: list, pwd_values: list):
        """
        Method to decrypt plaintext simple substitution with simple +
        :param encrypted_values: list of values 0 to 255
        :param pwd_values: list of values 0 to 255
        :return: list of decrypted values 0 to 255
        """
        result = ''
        if SimpleSubstitution.check_same_length(encrypted_values, pwd_values) is False: # check if values have same length
            pwd_values = SimpleSubstitution.mod_pwd_length(len(encrypted_values), pwd_values)
        # SUBSTITUTION ENCRYPT OPERATION
        raw_sum = list(map(lambda x, y: x - y, encrypted_values, pwd_values))

        # MOD RESULTS TO VALUES NOT MORE THAN 255
        for i in range(0,len(raw_sum)):
            if raw_sum[i] < 0:
                val = raw_sum[i] + 255
                raw_sum.pop(i)
                raw_sum.insert(i, val)
        print('DECRYPTED VALUES:', raw_sum, '\n')

        # CONVERT RAW DECRYPTED VALUES TO STRING RESULT
        for i in raw_sum:
            result += chr(i)
            # TODO CUT 255's
        print('DECRYPTED MESSAGE ', result, '\n')
        return result

    @classmethod  # method is class and should be accesible as tool if needed
    def check_same_length(cls, values1: list, values2: list):
        """
        Method to compare length of two list.
        :param values1: list of values
        :param values2: list of values
        :return: Boolean value
        """
        if len(values1) == len(values2):  # if value are same length
            return True
        if len(values1) != len(values2):  # if values are NOT same length
            return False

    @classmethod  # method is class and should be accesible as tool if needed
    def mod_plaintext_length(cls, pwd_length: int, plaintext_values: list):
        """
        Method is needed if password is longer as plaintext. Modifies plaintext to same length
        with appending value 255 in list
        :param pwd_length: integer represent length of password values list
        :param plaintext_values:  # list of plaintext values shorter than pwd
        :return: returns password list of values in same length as plaintext
        """
        result_plaintext = plaintext_values  # result include plaintext values
        for i in range(0, pwd_length-len(plaintext_values)):  # loops to fill plaintext
            result_plaintext.append(255)  # fill plaintext with value 255
        print(result_plaintext, len(result_plaintext))  # print result and his length
        return result_plaintext  # return result list with added values 255

    @classmethod  # method is class and should be accesible as tool if needed
    def mod_pwd_length(cls, plaintext_length: int, pwd_values: list):
        """
        Method needed to mod password length to plaintext length by repeating password N times.
        This is simplest method to do it ... but there are methods much more sophisticated
        :param plaintext_length: integer representing length of plaintext shorter than plaintext
        :param pwd_values: list of password values representing symbols in password
        :return: returns password list of values in same length as plaintext
        """
        result_pwd = list()  # defines result as empty list
        for i in range(0, plaintext_length):  # loops in range of length of plaintext
            [result_pwd.append(k) for k in pwd_values]  # append symbols in password to result list to repeat password N times
        print(result_pwd, len(result_pwd))  # print final result password and his length
        return result_pwd  # return result list with N x passwords with same length as plaintext


if __name__ == '__main__':  # if this program runs as MAIN program DO:
    # No instance of whole class is needed to gain access to methods
    encrypted = SimpleSubstitution.encrypt_simple_substitution(str_values_list,str_values_list2)
    decrypted = SimpleSubstitution.decrypt_simple_substitution(encrypted, str_values_list2)