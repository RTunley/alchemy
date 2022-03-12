## Temporary place for designing the Snapshot functionality ##

## course will need a new attribute - checkpoints. This will be a 1-to-many relationship, as one course can have multiple checkpoints. They will also need a new method, as below:

def get_snapshots(self):
    snapshot_list = []
    for checkpoint in self.checkpoints:
        snapshot_list.append(checkpoint.snapshot)
    return(snapshot_list)

## Classes ##

## Checkpoints are specific to courses and will be looped through to generate Snapshot reports ##
class Checkpoint:
    def __init__(self, name, course, snapshot, paper_list):
        self.name = name
        self.course = course
        self.snapshot = snapshot
        self.papers = paper_list

    ## Before the reports are published, the papers included in a checkpoint can be edited by a Head of Department ##
    def edit_included_papers(self, paper_list):
        self.papers = []
        for paper in paper_list:
            self.papers.append(paper)

    ## Snapshot reports will all be published together, but teachers will not finish all their marking and data entry at the same time --> need an easy way for individual courses to signal their 'readiness' for publishing.
    def check_if_ready(self):
        for paper in self.papers:
            if not paper.has_all_scores():
                return False
            else:
                return True

## Snapshots are instantiated by school admin, not individual courses. ##
class Snapshot:
    def __init__(self, name, course_list):
        self.name = name
        self.courses = course_list
        self.checkpoints = []
        self.is_published = False

    def check_if_ready(self):
        for checkpoint in self.checkpoints:
            if not checkpoint.check_if_ready():
                return False
            else:
                return True

    def publish(self):
        if self.check_if_ready():
            self.is_published = True

    #Snapshot reports are like your typical report card - they contain a brief summary of the student achievement in each course they taking, and will contain links to the more detailed checkpoint reports for each course. ##

## Endpoints ##

## These endpoints will be in snapshots.py, but accessed throughout the site ##

## will get called on school.index --> doesn't exist yet. But this function would only be accessible above the course or department level.
def new_snapshot(name, course_list):
    new_snapshot = Snapshot(name, course_list)
    ## Default course_list will be 'all', but there are situations where some courses publish snapshots and others don't. Want to keep this option open for future.
    for course in  new_snapshot.course_list:
        new_checkpoint = Checkpoint(new_snapshot.name, course, new_snapshot, [])
        course.checkpoints.append(new_checkpoint)
        new_snapshot.checkpoints.append(new_checkpoint)

## Called on clazz.index and cohort.index for admin, teachers, and students
def student_checkpoint_report(student, paper_list):
    ## Calculate necessary quantities for student checkpoint report, organize into pythonic objects like with previous reports. Then, send these objects to the HTML templates for student_checkpoint_report ##
    pass

## Called on clazz.index but only for admin and teachers
def clazz_checkpoint_report(clazz, paper_list):
    ## Calculate necessary quantities for clazz checkpoint report, organize into pythonic objects like with previous reports. Then, send these objects to the HTML templates for clazz_checkpoint_report ##
    pass

## Called on cohort.index, only for admin (maybe teachers)
def cohort_checkpoint_report(course, paper_list):
    ## Calculate necessary quantities for cohort checkpoint report, organize into pythonic objects like with previous reports. Then, send these objects to the HTML templates for cohort_checkpoint_report ##
    pass

## Called on student.index - for students, teachers, and admin
def student_snapshot_report(student, data_objects):
    ## Requires some sort of list of data_objects, each of which would come from a course that the student is taking. These data_objects contain quantities like their average score and grade from that course ##
    pass


## Sequence ##

## 1) School admin runs new_snapshot() through UI

## 2) It creates new checkpoints for all the courses in course_list. new_snapshot default is_published attribute is false --> this should prevent any access to the snapshot reports (for each student) or checkpoint reports (for students, clazzes, and cohorts).

## 3) Course-level admin assign papers to the checkpoint.papers attribute for each course. A Checkpoint's readiness to be included in a Snapshot will automatically signalled once all scores are uploaded from all clazzes in a course.

## 4) Once all checkpoints from all courses are ready, Snapshot.check_if_ready() will return true. After this point, Snapshot.publish() can be called to make all checkpoint reports and snapshot reports available for viewing.
