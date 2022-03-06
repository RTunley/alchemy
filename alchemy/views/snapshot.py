## Temporary place for designing the Snapshot functionality ##

## course will need a new attribute - checkpoints. This will be a 1-to-many relationship, as one course can have multiple checkpoints ##

## Checkpoints are specific to courses and checkpoints will be looped through to generate Snapshot reports ##
class Checkpoint:
    def __init__(self, name, course, snapshot, paper_list):
        self.name = name
        self.course = course
        self.snapshot = snapshot
        self.papers = paper_list
        self.is_ready = False

    ## Before the reports are published, the papers included in a checkpoint can be edited by a Head of Department ##
    def edit_included_papers(self, paper_list):
        self.papers = []
        for paper in paper_list:
            self.papers.append(paper)

    ## Snapshot reports will all be published together, but teachers will not finish all their marking and data entry at the same time --> need an easy way for individual courses to signal their 'readiness' for publishing.
    def check_if_ready(self):
        for paper in self.papers:
            if not paper.has_all_scores():
                self.is_ready = False
            else:
                self.is_ready = True

    def generate_checkpoint_reports(self):
        for clazz in self.course.clazzes:
            for student in clazz.students:
                make_student_checkpoint_report(student, self.papers)
            make_clazz_checkpoint_report(clazz, self.papers)
        make_cohort_checkpoint_reports(course.clazzes, self.papers)

## Snapshots are instantiated by school admin, not individual courses. ##
class Snapshot:
    def __init__(self, name, course_list):
        self.name = name
        self.courses = course_list
        self.is_ready = False
        self.checkpoints = []

    def check_if_ready(self):
        for checkpoint in self.checkpoints:
            if not checkpoint.is_ready():
                self.is_ready = False
            else:
                self.is_ready = True

    #Snapshot reports are like your typical report card - they contain a brief summary of the student achievement in each course they taking, and will contain links to the more detailed checkpoint reports for each course. ##
    def generate_snapshot_reports(self):
        if self.is_ready == True:
            for clazz in self.course.clazzes:
                for student in clazz.students:
                    ##See below about the data_objects vinput variable ##
                    make_student_snapshot_report(student, data_objects)

def new_snapshot(name, course_list):
    new_snapshot = Snapshot(name, course_list)
    for course in  new_snapshot.course_list:
        new_checkpoint = Checkpoint(new_snapshot.name, course, new_snapshot, [])
        course.checkpoints.append(new_checkpoint)
        new_snapshot.checkpoints.append(new_checkpoint)

def make_student_checkpoint_report(student, paper_list):
    ## Calculate necessary quantities for student checkpoint report, organize into pythonic objects like with previous reports. Then, send these objects to the HTML templates for student_checkpoint_report ##
    pass

def make_clazz_checkpoint_report(student, paper_list):
    ## Calculate necessary quantities for clazz checkpoint report, organize into pythonic objects like with previous reports. Then, send these objects to the HTML templates for clazz_checkpoint_report ##
    pass

def make__checkpoint_report(student, paper_list):
    ## Calculate necessary quantities for cohort checkpoint report, organize into pythonic objects like with previous reports. Then, send these objects to the HTML templates for cohort_checkpoint_report ##
    pass

def make_student_snapshot_report(student, data_objects):
    ## Requires some sort of list of data_objects, each of which would come from a course that the student is taking. These data_objects contain quantities like their average score and grade from that course ##
    pass
