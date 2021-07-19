import os, shutil
import openpyxl as opxl

def output_results_excel(paper, clazz, dir):
    num_questions = len(paper.paper_questions)
    student_list = []
    for s in clazz.students:
        student_list.append(s)
    num_students = len(student_list)
    wb = opxl.Workbook()
    ws = wb.active
    ws.cell(row = 2, column = 3).value = 'Question ID:'
    ws.cell(row = 3, column = 3).value = 'Order ID:'
    ws.cell(row = 4, column = 3).value = 'Question Totals:'
    ws.cell(row = 5, column = 1).value = 'Student ID'
    ws.cell(row = 5, column = 2).value = 'Given Name'
    ws.cell(row = 5, column = 3).value = 'Family Name'
    for i in range(num_questions):
        ws.cell(row = 2, column = i+4).value = paper.paper_questions[i].question.id
        ws.cell(row = 3, column = i+4).value = paper.paper_questions[i].order_number
        ws.cell(row = 4, column = i+4).value = paper.paper_questions[i].question.points

    for i in range(num_students):
        ws.cell(row = 6+i, column = 1).value = student_list[i].id
        ws.cell(row = 6+i, column = 2).value = student_list[i].given_name
        ws.cell(row = 6+i, column = 3).value = student_list[i].family_name

    filename = '{}_{}_results.xlsx'.format(clazz.code, paper.title)
    wb.save(os.path.join(dir, filename))
    return(filename)
