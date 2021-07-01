import openpyxl as opxl
from alchemy import application, models
import os

ALLOWED_EXTENSIONS = set(['xlsx'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_directory(clazz):
    course = clazz.course
    account = course.account
    path = os.getcwd()
    account_folder = os.path.join(path, account.name)
    if not os.path.isdir(account_folder):
        os.makedirs(account_folder)
    course_folder = os.path.join(account_folder, course.name)
    if not os.path.isdir(account_folder):
        os.makedirs(account_folder)
    clazz_folder = os.path.join(course_folder, clazz.code)
    if not os.path.isdir(clazz_folder):
        os.makedirs(clazz_folder)
    application.config['UPLOAD_FOLDER'] = clazz_folder
    return clazz_folder

def delete_current_clazzlist(clazz, db):
    for u in clazz.users:
        if u.access_id == 3:
            db.session.delete(u)
    db.session.commit()

def parse_results_excel(filename, clazz, paper):
    wb = opxl.load_workbook(filename)
    ws = wb.active
    student_list = []
    for u in clazz.users:
        if u.access_id == 3:
            student_list.append(u)
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
            new_score = models.Score(value = score_value, question = question, user = student_list[i], paper = paper)
            scores_list.append(new_score)

    return(scores_list)

def write_scores_to_db(db, scores_list):
    for s in scores_list:
        db.session.add(s)
    db.session.commit()

def parse_clazz_excel(filename, clazz):
    wb = opxl.load_workbook(filename)
    ws = wb.active
    num_students = ws.cell(column = 2, row = 2).value
    user_list = []

    for i in range(num_students):
        student_id = ws.cell(column = 1, row = 5+i).value
        student_family_name = ws.cell(column = 2, row = 5+i).value
        student_given_name = ws.cell(column = 3, row = 5+i).value
        new_user = models.User(id = student_id, family_name = student_family_name, given_name = student_given_name,
                        access_id = 3, clazzes=[clazz])
        user_list.append(new_user)

    return(user_list)

def write_users_to_db(db, user_list):
    for u in user_list:
        db.session.add(u)
    db.session.commit()
