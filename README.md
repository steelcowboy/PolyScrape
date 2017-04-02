# PolyScrape v0.1
Some tools to scrape the Cal Poly catalog

get_cp_catalog:
- Type in the catalog title in lower case (e.g. aero) to scrape the 
  department catalog into JSON format

parse_prereq_string:
- Can use independently on a single sting, otherwise import the parse_string function
  to get a machine-readable representation of the prereqs string

test_prereq_parser:
- Pass it a JSON file and it will parse all prereqs in the file
