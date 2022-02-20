## Temporary place for designing the Snapshot functionality ##

class Snapshot(object):
    def __init__(self, course, name, paper_list):
        self.course = course
        self.name = name
        self.papers = paper_list

def new_snapshot(course, name, paper_list):
    new_snapshot = Snapshot(course, name, paper_list)
    

# def take_snapshot(name, paper_list):

    # Back end:
    # 1) Calculate culumative marks for individual students
    #
    # 2) Prepare other values / data sets for use in analysing individual students (graphs, report sections, etc)
    #
    # 3) Calculate average achievement for cohort/clazzes
    #
    # 4) Prepare other values / data sets for use in analysing cohort/clazzes (graphs, report sections, etc)

    # Front End
    #
    # 1) Update table on Course indexing
    #
    # 2) Make new columns in cohort / clazz student lists w/ grades and report buttons
    #
    # 3) Add entry to some sort of table on Cohort index
