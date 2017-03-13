import sys, json
from parse_string import parse_string

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("USAGE: test_string_catalog.py <DEPARTMENT>")
        sys.exit(1)

    cat = sys.argv[1]

    with open(f"{cat}", 'r') as catfile:
        inp = json.loads(catfile.read())

    # print(inp)
    for key,val in inp.items():
        for k,v in val.items():
            if k == "prereqs":
                parse_string(v)
