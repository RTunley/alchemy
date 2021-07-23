import os, shutil
import openpyxl as opxl
import tempfile
from alchemy import application

def get_temp_directory():
    temp_dir = tempfile.TemporaryDirectory()
    application.config['UPLOAD_FOLDER'] = temp_dir
    return temp_dir

def make_class_template(dir):
    wb = opxl.Workbook()
    ws1 = wb.active
    ws1.title = "Class Template"

    ws1["A1"] = "Student Id"
    ws1["B1"] = "E-mail"
    ws1["C1"] = "Family Name"
    ws1["D1"] = "Given Name"

    filename = 'Class_Template.xlsx'
    wb.save(os.path.join(dir.name, filename))

    return filename
