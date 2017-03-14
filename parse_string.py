import re
"""
To fix:
    'Corequisite:'
    'Recommended:'
    'x, y, and z' -> and_list([x, y, z])
"""

class none_list(list):
    def __init__(self, lst):
        list.__init__(self, lst)
        self.kind = "none"

    def expand(self, func):
        lst = []
        for x in self:
            if isinstance(x, str):
                lst.append(x)
            else:
                lst.append(getattr(x, func)())
        return lst

    def get_dict(self):
        lst = self.expand("get_dict")
        return {self.kind: lst} 
    
    def english(self):
        lst = self.expand("english") 
        return '(' + f' {self.kind} '.join(lst) + ')'

class or_list(none_list):
    def __init__(self, lst):
        none_list.__init__(self, lst)
        self.kind = "or"

class and_list(none_list):
    def __init__(self, lst):
        none_list.__init__(self, lst)
        self.kind = "and"

def clean_string(string):
    # Just nuke the string in this case
    string = string.replace("Term Typically Offered: TBD", '')
    string = string.replace("Consent of instructor", '')
    string = string.lstrip()
    string = string.replace('.', '')
    # Makes parsing a bit easier
    string = string.replace(' and either ', '; and ')
    string = string.replace(' with a grade of C- or better', '')
    string = string.replace(' or equivalent', '')
    string = string.replace('or consent of instructor', '')
    string = string.replace('or instructor consent', '')
    string = string.rstrip()
    string = string.rstrip(',')
    # Weird if two removed statements are in a row sometimes you get this
    string = string.replace(' ,', '')
    if debug:
        print(f"Cleaned string: {string}")
    return string

def split_corequisite(string):
    if 'Corequisite: ' in string:
        outer_list = string.split('Corequisite: ')
        coreqs = outer_list.pop(-1)
        if len(outer_list) == 1:
            outer_dict = split_by_semicolon(outer_list[0]).get_dict()
            coreq_dict = split_by_semicolon(coreqs).get_dict()
            return {**outer_dict, **{"coreqs": coreq_dict}}
        else:
            print("Uh oh, something's wrong. Splitting off 'Corequisite: ' resulted in " +
                    f"a list of length {len(outer_list)}. Dumping vars:")
            print(outer_list)
    else:
        return split_by_semicolon(string)

def split_by_semicolon(string):
    outer_list = None
    for i,x in enumerate(string):
        if x == ";":
            search_section = string[i+1:i+5]
            remove_section = None

            split_list = string.split(";")

            if "and" in search_section:
                outer_list = and_list(split_list)
                remove_section = " and "
            elif "or" in search_section:
                outer_list = or_list(split_list)
                remove_section = " or "
            else:
                # Semicolon seems to imply and if not stated
                split_list[-1] = split_list[-1][1:]
                outer_list = and_list(split_list)

            if remove_section is not None:
                # Replace the search section since we don't need it anymore 
                outer_list[-1] = outer_list[-1].replace(remove_section, "", 1)

    if outer_list is None:
        if debug:
            print(f"String split by semicolons: {string}")
        return split_by_comma(string) 
    # It's a list, so need to dissect further
    else:
        if debug:
            print(f"Semicolon-split list: {outer_list}")
        for i,x in enumerate(outer_list):
            outer_list[i] = split_by_comma(x)
        return outer_list

def split_by_comma(string):
    comma_list = None 
    for i,x in enumerate(string):
        if x == ",":
            search_section = string[i+1:i+5]
            remove_section = None

            split_list = string.split(",")

            if "and" in search_section:
                comma_list = and_list(split_list)
                remove_section = " and "
            elif "or" in search_section:
                comma_list = or_list(split_list)
                remove_section = " or "

            if remove_section is not None:
                # Replace the search section since we don't need it anymore 
                comma_list[-1] = comma_list[-1].replace(remove_section, "", 1)

    if comma_list is None:
        if debug:
            print(f"String split by commas: {string}")
        return split_by_coordinating_conjunction(string) 
    else:
        if debug:
            print(f"Comma-split list: {comma_list}")
        for i,x in enumerate(comma_list):
            comma_list[i] = split_by_coordinating_conjunction(x)
        return comma_list

def split_by_coordinating_conjunction(string):
    if "one of the following: " in string:
        string = string.replace("one of the following: ", '')
        if debug:
            print(f"'one of the following' in string: {string}")
        return split_by_coordinating_conjunction(string) 
    elif "and" in string:
        if ',' in string:
            string = string.replace(" and", ',')
            split_list = string.split(', ')
        else:
            split_list = string.split(" and ")

        return and_list(split_list)
    elif "or" in string:
        if ',' in string:
            string = string.replace(" or", ',')
            split_list = string.split(', ')
        else:
            split_list = string.split(" or ")
        return or_list(split_list)
    
    return string

def parse_string(string):
    print(string)
    string = clean_string(string)

    outer_list = split_corequisite(string)    
    if not isinstance(outer_list, str):
        # print(outer_list.english())
        print(outer_list)
        print("\n")
    else:
        print(outer_list) 
        print("\n")


debug=False
if __name__=="__main__":
    import sys

    if len(sys.argv) == 1:
        strings = [
        "Completion of ELM requirement, and passing score on MAPE or MATH 117 with a grade of C- or better or MATH 118 with a grade of C- or better, or consent of instructor.",

        "MATH 118 or equivalent.",

        "MATH 141 or MATH 161 with a grade of C- or better, or consent of instructor.",

        "CSC/CPE 103 with a grade of C- or better, or instructor consent.",

        "CPE/CSC 357; and CSC 141 or CSC 348.",

        "CSC 141 or CSC 348, and MATH 142; or CPE/CSC 103 and MATH 248."
        ]
    else:
        args = sys.argv 
        if '-d' in args or '--debug' in args:
            debug=True
            args.remove('-d' if '-d' in args else '--debug')
        strings = args[1:]

    for x in strings:
        parse_string(x)
