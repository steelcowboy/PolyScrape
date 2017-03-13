import requests, bs4, json, sys  
from bs4 import BeautifulSoup 

def get_courses(department):
    catalog = {}

    catalog_req = requests.get(f"http://catalog.calpoly.edu/coursesaz/{department}")
    soup = BeautifulSoup(catalog_req.text, 'html.parser')

    courses = soup.find_all("div", "courseblock")

    for courseblock in courses:
        catalog_title = ""

        title_block = courseblock.p

        for string in title_block.strings:
            string = string.rstrip('\n').replace('\xa0', ' ')
            if 'units' in string or 'unit' in string:
                catalog[catalog_title]['units'] = string[0]
            else:
                # There is a better way to handle this but this should work  
                course_and_title = string.split('.')
                catalog_title = course_and_title[0]
                
                catalog[catalog_title] = {}
                catalog[catalog_title]['title'] = course_and_title[1]

        course_prereqs = title_block.next_sibling

        prereqs_html = course_prereqs.p.next_sibling

        if prereqs_html is not None:
            prereqs_string = [] 

            for x in prereqs_html.children:
                if isinstance(x, bs4.element.NavigableString):
                    prereqs_string.append(x)
                elif isinstance(x, bs4.element.Tag):
                    prereqs_string.append(x['title'])
            catalog[catalog_title]['prereqs'] = ''.join(
                    [s.replace('\xa0', ' ').replace('Prerequisite: ', ' ')
                        for s in prereqs_string])

        for obj in courseblock.children:
            if isinstance(obj, bs4.element.Tag) and "courseblockdesc" in obj['class']: 
                desc_string = [] 
                for x in obj.p.children:
                    if isinstance(x, bs4.element.NavigableString):
                        desc_string.append(x)
                    elif isinstance(x, bs4.element.Tag):
                        desc_string.append(x['title'])
                catalog[catalog_title]['decription'] = ''.join(
                        [s.replace('\xa0', ' ').replace('Prerequisite: ', ' ')
                            for s in desc_string])

    return catalog 

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("USAGE: get_cp_catalog.py <DEPARTMENT>")
        sys.exit(1)

    cat = sys.argv[1]

    catalog = get_courses(cat)
    with open(f"{cat}_catalog.json", 'w') as catfile:
        catfile.write(json.dumps(catalog, indent=4))


"""This is a courseblock 
<div class="courseblock">
    <p class="courseblocktitle">
        <strong>CSC 101. Fundamentals of Computer Science I.
            <span class="courseblockhours">4 units </span>
        </strong>
    </p>

    <div class="noindent courseextendedwrap">
        <p class="noindent">Term Typically Offered: F, W, SP</p>
        <p>Prerequisite: Completion of ELM requirement, and passing score on MAPE or <a class="bubblelink code" href="/search/?P=MATH 117" onclick="return showCourse(this, 'MATH 117');" title="MATH 117">MATH 117</a> with a grade of C- or better or <a class="bubblelink code" href="/search/?P=MATH 118" onclick="return showCourse(this, 'MATH 118');" title="MATH 118">MATH 118</a> with a grade of C- or better, or consent of instructor.</p>
    </div>

    <div class="courseblockdesc">
        <p>Basic principles of algorithmic problem solving and programming using methods of top-down design, stepwise refinement and procedural abstraction.  Basic control structures, data types, and input/output.  Introduction to the software development process:  design, implementation, testing and documentation.  The syntax and semantics of a modern programming language.  Credit not available for students who have taken CSC/<a class="bubblelink code" href="/search/?P=CPE 108" onclick="return showCourse(this, 'CPE 108');" title="CPE 108">CPE 108</a>.  3 lectures, 1 laboratory.  Crosslisted as CPE/<a class="bubblelink code" href="/search/?P=CSC 101" onclick="return showCourse(this, 'CSC 101');" title="CSC 101">CSC 101</a>.</p>
    </div>
"""
