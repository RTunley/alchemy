import os
os.environ['ALCHEMY_CONFIG'] = 'TestConfig'
from alchemy import application as app
from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, Question, Tag, Paper, PaperQuestion, Clazz, Student
import test.create_test_objects as cto
import csv
import io
import openpyxl as opxl

def course_student_number(course):
    num_students = 0
    for clazz in course.clazzes:
        num_students+= len(clazz.students)

    return num_students

class BaseTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        test_account = cto.create_account()
        test_course = cto.create_course(test_account)
        test_clazz = cto.add_clazz(test_course)
        student_list = cto.add_students_and_aws_users(test_course, test_clazz)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

    def test_index(self):
        course = Course.query.first()
        response = self.client.get('/course/{}/cohort/index'.format(course.id), follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    def test_add_student(self):
        course = Course.query.first()
        clazz = Clazz.query.first()
        num_students = len(clazz.students)
        given_name = 'Alejandro'
        family_name = 'Fukovich'
        new_id = 12345678
        new_email = 'af12345678@schoolofrock.com'
        data = dict(given_name = given_name, family_name = family_name, clazz_id = clazz.id,  student_id = new_id, student_email = new_email)
        response = self.client.post('/course/{}/cohort/add_student'.format(course.id), data = data,
        follow_redirects = True)
        self.assertEqual(len(clazz.students), num_students+1)
        new_student = Student.query.filter_by(id = 12345678).first()
        self.assertEqual(new_student.aws_user.family_name, family_name)
        self.assertEqual(new_student.aws_user.given_name, given_name)
        self.assertEqual(new_student.aws_user.email, new_email)

    def test_add_class_csv(self):
        course = Course.query.first()
        initial_num_students = course_student_number(course)
        cwd = os.getcwd()
        csv_filepath = os.path.join(cwd,'new_class.csv')
        with open(csv_filepath, 'w+') as class_csv:
            filewriter = csv.writer(class_csv, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['ID', 'family name', 'given name', 'e-mail'])
            filewriter.writerow(['4321', 'Trench', 'Mariana', 'mariana.trench@schoolofrock.com'])

        csv_content = open(csv_filepath)
        file_content = csv_content.read().encode('UTF-8')
        csv_content.close()
        data = dict(clazz_code = 'newclasscode')
        data['file'] = (io.BytesIO(file_content), csv_filepath)
        response = self.client.post('/course/{}/cohort/upload_excel'.format(course.id), data = data,
        follow_redirects = True)
        os.remove(csv_filepath)

        self.assertEqual(len(course.clazzes), 2)
        new_num_students = course_student_number(course)
        self.assertEqual(new_num_students, initial_num_students+1)
        new_clazz = Clazz.query.filter_by(code = 'newclasscode').first()
        self.assertTrue(len(new_clazz.students), 1)
        new_student = Student.query.filter_by(id = 4321).first()
        self.assertEqual(new_student.aws_user.family_name, 'Trench')
        self.assertEqual(new_student.aws_user.given_name, 'Mariana')
        self.assertEqual(new_student.aws_user.email, 'mariana.trench@schoolofrock.com')


    def test_add_class_xlxs(self):
        course = Course.query.first()
        initial_num_students = course_student_number(course)
        cwd = os.getcwd()
        excel_filepath = os.path.join(cwd,'new_class.xlsx')
        wb = opxl.Workbook()
        sheet = wb.active
        data = {'A1': 'ID', 'B1': 'Family Name', 'C1': 'Given Name', 'D1':'email', 'A2': 4321, 'B2': 'Trench', 'C2': 'Mariana', 'D2': 'mariana.trench@schoolofrock.com'}
        for cell in data:
            sheet[cell] = data[cell]
        wb.save(excel_filepath)

        excel_content = opxl.writer.excel.save_virtual_workbook(wb)
        data = dict(clazz_code = 'newclasscode')
        data['file'] = (io.BytesIO(excel_content), excel_filepath)
        response = self.client.post('/course/{}/cohort/upload_excel'.format(course.id), data = data,
        follow_redirects = True)
        os.remove(excel_filepath)

        self.assertEqual(len(course.clazzes), 2)
        new_num_students = course_student_number(course)
        self.assertEqual(new_num_students, initial_num_students+1)
        new_clazz = Clazz.query.filter_by(code = 'newclasscode').first()
        self.assertTrue(len(new_clazz.students), 1)
        new_student = Student.query.filter_by(id = 4321).first()
        self.assertEqual(new_student.aws_user.family_name, 'Trench')
        self.assertEqual(new_student.aws_user.given_name, 'Mariana')
        self.assertEqual(new_student.aws_user.email, 'mariana.trench@schoolofrock.com')

if __name__ == '__main__':
    unittest.main()
