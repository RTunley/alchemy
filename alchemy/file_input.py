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

#Expects student info in the following columns: [ID, family name, given name, e-mail]
def add_new_clazz(db, filename, clazz):
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        for line in reader:
            student_id, family_name, given_name, email = line
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

def write_scores_to_db(db, scores_list):
    for s in scores_list:
        db.session.add(s)
    db.session.commit()
