import openpyxl as opxl
from alchemy import application, models
import os
import csv
import tempfile

ALLOWED_EXTENSIONS = set(['xlsx', 'csv'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extension(filename):
    split_tuple = os.path.splitext(filename)
    ext = split_tuple[1]
    return(ext)

def get_temp_directory():
    temp_dir = tempfile.TemporaryDirectory()
    application.config['UPLOAD_FOLDER'] = temp_dir
    return temp_dir

def delete_temp_directory(temp_dir):
    temp_dir.cleanup()

#Expects student info in the following columns: [family name, given name, ID, e-mail]
def add_new_clazz(db, filename, clazz):
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        for line in reader:
            student_id = line[0]
            family_name = line[1]
            given_name = line[2]
            email = line[3]
            new_aws_user = models.AwsUser(family_name = family_name, given_name = given_name, email = email, username = given_name+family_name+str(student_id), group = 'student', sub = 'aws-sub'+given_name+family_name+str(student_id))
            new_student = models.Student(aws_user = new_aws_user, id = student_id, clazzes = [clazz])
            db.session.add(new_aws_user)
            db.session.add(new_student)

    db.session.commit()

def convert_to_csv(file_path):
    (new_file_title, ext) = os.path.splitext(file_path)
    wb = opxl.load_workbook(file_path)
    sheet = wb.active
    csv_filename = new_file_title+'.csv'
    col = csv.writer(open(csv_filename, 'w', newline=""))

    for r in sheet.rows:
        col.writerow([cell.value for cell in r])

    return(csv_filename)

# def parse_clazz_excel(filename, clazz):
#     wb = opxl.load_workbook(filename)
#     ws = wb.active
#     num_students = ws.cell(column = 2, row = 2).value
#     student_list = []
#
#     for i in range(num_students):
#         student_id = ws.cell(column = 1, row = 5+i).value
#         student_family_name = ws.cell(column = 2, row = 5+i).value
#         student_given_name = ws.cell(column = 3, row = 5+i).value
#         new_student = models.Student(id = student_id, family_name = student_family_name, given_name = student_given_name, clazzes=[clazz])
#         student_list.append(new_student)
#
#     return(student_list)

# def delete_current_clazzlist(clazz, db):
#     for s in clazz.students:
#         db.session.delete(s)
#     db.session.commit()
## TODO not used anymore, but maybe useful in future when switching over cohorts?

def parse_results_excel(filename, clazz, paper):
    wb = opxl.load_workbook(filename)
    ws = wb.active
    student_list = []
    for s in clazz.students:
        student_list.append(s)
    num_students = len(student_list)
    scores_list = []
    first_student_row = 6
    first_score_col = 4
    question_id_row = 2
    for i in range(num_students):
        for j in range(len(paper.paper_questions)):
            question_id = ws.cell(row = question_id_row, column = first_score_col+j ).value
            for paper_question in paper.paper_questions:
                if paper_question.question.id == question_id:
                    question = paper_question.question
            score_value = ws.cell(row = first_student_row+i, column = first_score_col+j ).value
            new_score = models.Score(value = score_value, question = question, student = student_list[i], paper = paper)
            scores_list.append(new_score)

    return(scores_list)

def write_scores_to_db(db, scores_list):
    for s in scores_list:
        db.session.add(s)
    db.session.commit()
