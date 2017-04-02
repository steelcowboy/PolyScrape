import re, sys
"""
To fix:
    'x, y, and z' -> and_list([x, y, z])
        Note: Works some of the time
    '(or equivalent)'
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

class single(list):
    def __init__(self, obj):
        list.__init__(self, [obj])
        self.kind = single

    def get_dict(self):
        return {'single': self[0]}

    def english(self):
        return f"{self[0]}"

def clean_string(string):
    # Just nuke the string in this case
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
    string = string.rstrip(';')
    # Weird if two removed statements are in a row sometimes you get this
    string = string.replace(' ,', '')
    if debug:
        print(f"Cleaned string: {string}")
    return string

def split_corequisite(string):
    if 'Corequisite: ' in string:
        outer_list = string.split('Corequisite: ')
        outer_list = [x.lstrip().rstrip() for x in outer_list]

        coreqs = outer_list.pop(-1)
        if len(outer_list) == 1:
            outer_dict = split_recommended(outer_list[0])
            coreq_dict = split_recommended(coreqs)
            if debug:
                print(f"Coreq outer dict: {outer_dict}")
                print(f"Found coreqs: {coreq_dict}")

            if isinstance(outer_dict, str):
                outer_dict = single(outer_dict).get_dict() 
            else:
                outer_dict = outer_dict.get_dict()

            return {**outer_dict, **{"coreqs": coreq_dict}}
        else:
            print("Uh oh, something's wrong. Splitting off 'Corequisite: ' resulted in " +
                    f"a list of length {len(outer_list)}. Dumping vars:")
            print(outer_list)
    else:
        out = split_recommended(string)
        if out:
            if isinstance(out,str):
                return single(out)
            elif isinstance(out,dict):
                return out
            else:
                return out.get_dict()

    return None 

def split_recommended(string):
    if 'Recommended: ' in string:
        outer_list = string.split('Recommended: ')
        outer_list = [x.lstrip().rstrip() for x in outer_list]

        recom = outer_list.pop(-1)
        if len(outer_list) == 1:
            outer_dict = split_by_semicolon(outer_list[0])
            recom_dict = split_by_semicolon(recom)
            if debug:
                print(f"Recom outer dict: {outer_dict}")
                print(f"Found recommended: {recom_dict}")

            if isinstance(outer_dict, str):
                outer_dict = single(outer_dict).get_dict() 
            else:
                outer_dict = outer_dict.get_dict()

            if isinstance(recom_dict, str):
                recom_dict = single(recom_dict).get_dict() 
            else:
                recom_dict = recom_dict.get_dict()


            return {**outer_dict, **{"recommended": recom_dict}}
        else:
            print("Uh oh, something's wrong. Splitting off 'Recommended: ' resulted in " +
                    f"a list of length {len(outer_list)}. Dumping vars:")
            print(outer_list)
    else:
        out = split_by_semicolon(string)
        if out:
            if isinstance(out,str):
                return single(out)
            else:
                return out

    return None 

def split_by_semicolon(string):
    outer_list = None
    for i,x in enumerate(string):
        if x == ";":
            search_section = string[i+1:i+5]
            remove_section = None

            split_list = string.split(";", 1)
            split_list = [x.lstrip().rstrip() for x in split_list]


            if "and" in search_section:
                outer_list = and_list(split_list)
                remove_section = " and "
            elif "or" in search_section:
                outer_list = or_list(split_list)
                remove_section = " or "
            else:
                # Semicolon seems to imply 'and' not stated
                if split_list[-1] == ' ':
                    split_list[-1] = split_list[-1][1:]
                outer_list = and_list(split_list)
            
            if remove_section is not None:
                # Replace the search section since we don't need it anymore 
                outer_list[-1] = outer_list[-1].replace(remove_section, "", 1)
            
            # Need to break since we're only looking for first semicolon
            break

    if outer_list is None:
        if debug:
            print(f"String split by semicolons: {string}")
        return split_by_comma(string) 
    # It's a list, so need to dissect further
    else:
        # Might use this to handle more complex string 
        if ";" in outer_list[-1]:
            if debug:
                print(f"Decomposing \"{outer_list[-1]}\" further")
            outer_list[-1] = split_by_semicolon(outer_list[-1])

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
            split_list = [x.lstrip().rstrip() for x in split_list]

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
        return split_by_one_of(string) 
    else:
        if debug:
            print(f"Comma-split list: {comma_list}")
        for i,x in enumerate(comma_list):
            comma_list[i] = split_by_one_of(x)
        return comma_list

def split_by_one_of(string):
    # Handle multiple cases
    one_of = ["and one of the following: ", "and one of the following courses: "]
    for x in one_of:
        # Still trying to figure out how to handle this
        if x in string:
            string = string.split(x) 
            string = list(filter(None, string))

            if debug:
                print(f"'and one of the following' in string: {string}")

            if len(string) == 2:
                # In case it's a weird type of string
                string[0] = split_by_coordinating_conjunction(string[0])

                # This will not work if there is "and one of the following" multiple times  
                or_stuff = string[1].replace(' or', ',').split(', ')
                return and_list([string[0], or_list(or_stuff)])
            else:
                return or_list(string[0].replace(' or', ',').split(', '))

    one_of = ["or one of the following: ", "or one of the following courses: "]
    for x in one_of:
        # Still trying to figure out how to handle this
        if x in string:
            string = string.split(x) 
            string = list(filter(None, string))

            if debug:
                print(f"'or one of the following' in string: {string}")

            # In case it's a weird type of string
            string[0] = split_by_coordinating_conjunction(string[0])

            # This will not work if there is "and one of the following" multiple times  
            or_stuff = string[1].replace(' or', ',').split(', ')
            return and_list([string[0], or_list(or_stuff)])

    return split_by_coordinating_conjunction(string)

def split_by_coordinating_conjunction(string):
    conjs = [" or ", " and "]
    for c in conjs:
        if c in string:
            if debug:
                conjunction = c.lstrip().rstrip()
                print(f"Found '{conjunction}' in string: {string}")

            if ',' in string:
                string = string.replace(c, ',')
                split_list = string.split(', ')
            else:
                split_list = string.split(c)

            split_list = list(filter(None, split_list))
            
            # Some weird strings have no commas or anything special
            for i,x in enumerate(split_list):
                # This will do nothing if fully decomposed
                split_list[i] = split_by_coordinating_conjunction(x)

            if c == " and ":
                return and_list(split_list)
            else:
                return or_list(split_list)
    
    if string[:4] == "and ":
        string = string[4:]
    elif string[:3] == "or ":
        string = string[3:]

    return string

def parse_string(string):
    if string is None:
        return
    string = clean_string(string)
    outer_list = split_corequisite(string)
    return outer_list 


debug=False
if __name__=="__main__":
    import sys

    if len(sys.argv) == 1:
        print("USAGE: parse_string.py STRING")
        sys.exit(1)
    else:
        args = sys.argv 
        if '-d' in args or '--debug' in args:
            debug=True
            args.remove('-d' if '-d' in args else '--debug')
        strings = args[1:]

    for x in strings:
        print(x)
        parse_result = parse_string(x)
        print(f"{parse_result}\n")
