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
    def is_ready(self):
        for paper in self.papers:
            if not paper.has_all_scores():
                return False
            else:
                return True

## Snapshots are instantiated by school admin, not individual courses. ##
#Snapshot reports are like your typical report card - they contain a brief summary of the student achievement in each course they taking, and will contain links to the more detailed checkpoint reports for each course. ##
class Snapshot:
    def __init__(self, name, course_list):
        self.name = name
        self.courses = course_list
        self.checkpoints = []
        self.is_published = False

    def is_ready(self):
        if not self.checkpoints:
            return False
        else:
            for checkpoint in self.checkpoints:
                if not checkpoint.check_if_ready():
                    return False
                else:
                    return True

    def publish(self):
        if self.check_if_ready():
            self.is_published = True


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
def student_checkpoint_report(student, checkpoint):
    if checkpoint.is_ready():
        checkpoint_profile = make_checkpoint_profile(student, checkpoint)
        return flask.render_template('student_checkpoint_report', checkpoint_profile = checkpoint_profile)
    ## - checkpoint_profile contains all the detailed data needed for the checkpoint_report
    ## make_checkpoint_profile probably in reports.data_manager
    ## - Send checkpoint_profile to the HTML templates for student_checkpoint_report ##
    else:
        pass

## Called on clazz.index but only for admin and teachers
def clazz_checkpoint_report(clazz, checkpoint):
    if checkpoint.check_if_ready():
        student_checkpoint_profiles = []
        for student in clazz:
            checkpoint_profile = make_checkpoint_profile(student, checkpoint)
            student_checkpoint_profiles.append(checkpoint_profile)

        clazz_checkpoint_profile = make_group_checkpoint_profile(student_checkpoint_profiles)
        return flask.render_template('clazz_checkpoint_report', checkpoint_profiles = student_checkpoint_profiles)
    ## - Calculate all student_checkpoint_profiles
    ## - use these as inputs for clazz_checkpoint_profile (most likely)
    ## - send this objects to the HTML template for clazz_checkpoint_report ##
    else:
        pass

## Called on cohort.index, only for admin (maybe teachers)
def cohort_checkpoint_report(course, checkpoint):
    if checkpoint.check_if_ready():
        student_checkpoint_profiles = []
        for clazz in course.clazzes:
            for student in clazz.students:
                checkpoint_profile = make_checkpoint_profile(student, checkpoint)
                student_checkpoint_profiles.append(checkpoint_profile)

        cohort_checkpoint_profile = make_group_checkpoint_profile(student_checkpoint_profiles)
        return flask.render_template('cohort_checkpoint_report', checkpoint_profiles = student_checkpoint_profiles)
    ## - Calculate all student_checkpoint_profiles
    ## - use these as inputs for cohort_checkpoint_profile (most likely)
    ## - send this to the HTML template for cohort_checkpoint_report ##
    else:
        pass

## Called on student.index - for students, teachers, and admin
def student_snapshot_report(student, snapshot):
    if snapshot.check_if_ready():
        checkpoint_summary_list = []
        for clazz in student.clazzes:
            checkpoint_summary = make_checkpoint_summary(student, clazz.course, snapshot)
            checkpoint_summary_list.append(checkpoint_summary)
        return flask.render_template('student_snapshot_report', checkpoint_summaries = checkpoint_summary_list)
        ## - Requires 'student_checkpoint_summary', each of which would come from a course that the student is taking
        ## make_checkpoint_summary probably located in reports.data_manager
        ## - These summaries contain quantities like their average score and grade from that course ##
        ## - Send these data_objects to template for student_snapshot_report
    else:
        pass

## Sequence ##

## 1) School admin runs new_snapshot() through UI

## 2) It creates new checkpoints for all the courses in course_list. new_snapshot default is_published attribute is false --> this should prevent any access to the snapshot reports (for each student) or checkpoint reports (for students, clazzes, and cohorts).

## 3) Course-level admin assign papers to the checkpoint.papers attribute for each course. A Checkpoint's readiness to be included in a Snapshot will automatically signalled once all scores are uploaded from all clazzes in a course.

## 4) Once all checkpoints from all courses are ready, Snapshot.check_if_ready() will return true. After this point, Snapshot.publish() can be called to make all checkpoint reports and snapshot reports available for viewing.


## Plan
## Snapshots
## 1) Implement snapshots in models
## 2) create a get_course_list function and a new_snapshot endpoint in school.py
## 3) Write some html for viewing and calling the endpoint into school/snapshots.html
