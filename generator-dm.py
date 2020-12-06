import csv
import os
import re
from sys import getdefaultencoding
from pylibdmtx.pylibdmtx import encode
from pylibdmtx.pylibdmtx import decode
from PIL import Image

def search_for_orders():
    project_path = 'order'
    files_order = []
    for root, dirs, files in os.walk(project_path):
        for _files in files:
            if re.findall(r'.csv', str(_files)):
                files_order.append(str(root) + '/' + str(_files))
    return files_order

def reader_task_file():
    path_task_file = 'task.csv'
    with open(path_task_file, "r") as f_obj:
        reader = csv.reader(f_obj, delimiter=',')
        next(reader)
        file_task = []
        for row in reader:
            file_task.append(row)
        return file_task

def task_designer(files_order, file_task):
    task_list = []
    task = {'gtn':'', 'name':'', 'order':[], 'total_number_of_codes':int, 'error':[]}
    for item_task in file_task:
        task['gtn'] = item_task[0]
        task['name'] = item_task[1]
        number_of_codes = 0
        for item_order in files_order:
            if re.findall(item_task[0], str(item_order)):
                task['order'].append(item_order)
                number_of_codes_row = re.findall(r'(?<=quantity_)\d+', str(item_order))
                number_of_codes += int(number_of_codes_row[0])
        task['total_number_of_codes'] = number_of_codes
        task_list.append(task)
        task = {'gtn':'', 'name':'', 'order':[], 'total_number_of_codes':int, 'error':[]}
    return task_list

def creating_datamatrix(item_order, order_file, img_path, lable):
    order = open(item_order)
    reader = csv.reader(order, delimiter='\t')
    file_name = 0
    # index_file = open(r'project/index.html', 'w+')
    order_file.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link href="https://fonts.googleapis.com/css?family=PT+Sans&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
    <title>Document</title>
</head>
<body>

    <div class="container">''' + '\n')
    for row in reader:
        file_name = file_name + 1
        encoded = encode(" ".join(row).encode('utf8'))
        print(" ".join(row).encode('utf8'))
        gtn = re.findall(r'(?<=01)(.*?)(?=21)', str(" ".join(row).encode('utf8')))
        print(" ".join(gtn))
        serial_number = re.findall(r'(?<=21)(.*)(?=x1d91)', str(" ".join(row).encode('utf8')))
        serial_number = str(" ".join(serial_number))
        serial_number = serial_number.replace('\\', ' ')
        serial_number = serial_number.replace('<', '&lt;')
        print(serial_number)
        img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
        img.save(img_path + '/' + str(file_name) + '.png')
        order_file.write('''
        <div class="layout">
            <div class="img-wrapper">
                <img src="''' + 'img/' + str(file_name) + '.png' + '''" alt="datamatrix BarCode">
            </div>
            <div class="data-wrapper">
                <p> ''' + lable + '''</p>
                <p class="number">(01) ''' + str(" ".join(gtn)) + '''</p>
                <p class="number">(21) ''' + serial_number + '''</p>
            </div>
        </div>''' + '\n')
    order_file.write('''
    </div>

</body>
</html>
''')

def creat_project(tasks_to_be_completed):
    name_project = 'labels' + '/' + input('Введите название проекта: ')
    print(name_project)
    os.mkdir(name_project)
    index_file = open(name_project + '/' + 'index.html', "w+")
    index_file.close()
    for task in tasks_to_be_completed:
        os.mkdir(name_project + '/' + task['gtn'] + '_' + task['name'])
        for item_order in task['order']:
            order_name = ' '.join(re.findall(r'(?<=order/).+(?=.csv)', item_order))
            os.mkdir(name_project + '/' + task['gtn'] + '_' + task['name'] + '/' + order_name)
            os.mkdir(name_project + '/' + task['gtn'] + '_' + task['name'] + '/' + order_name + '/' + 'img')
            img_path = str(name_project + '/' + task['gtn'] + '_' + task['name'] + '/' + order_name + '/' + 'img')
            os.mkdir(name_project + '/' + task['gtn'] + '_' + task['name'] + '/' + order_name + '/' + 'css')
            css_file = open(name_project + '/' + task['gtn'] + '_' + task['name'] + '/' + order_name + '/css/' + 'style.css', 'w+')
            css_file.write('''.container {
                                    font-family: 'PT Sans', sans-serif;
                                }

                                body {
                                    padding: 0;
                                    margin: 0;
                                }

                                .layout {
                                    margin: 0 auto;
                                    width: 4.3cm;
                                    height: 2.4cm;
                                    display: flex;
                                    padding: 0;
                                    box-sizing: border-box;
                                    padding-top: 5px;
                                }

                                .img-wrapper, .data-wrapper {
                                    display: inline-block;
                                    margin-top: 0;
                                }

                                .data-wrapper {
                                    margin-top: 2px;
                                }

                                .img-wrapper {
                                    margin: 0 0 0 0;
                                }

                                p {
                                    margin: 0;
                                    font-size: 8px;
                                    font-weight: 700;
                                }

                                p.number {
                                    font-size: 8px;
                                }

                                .layout img {
                                    width: 70px;
                                    height: auto;
                                }

                                @page {
                                    size: 4.3cm 2.5cm;
                                }

                                @media print {

                                    .layout { page-break-after: always;}

                                } ''')
            css_file.close()
            order_file = open(name_project + '/' + task['gtn'] + '_' + task['name'] + '/' + order_name + '/' + order_name + '.html', "w+")
            lable = task['name']
            creating_datamatrix(item_order, order_file, img_path, lable)
            # order_file.write('Hello, World!!!')
            order_file.close()
    return name_project

def save_task(name_project, tasks_to_be_completed):
    index_file = open(name_project + '/' + 'index.html', "w+")
    for task in tasks_to_be_completed:
        index_file.write('<p>' + 'GTI: ' + task['gtn'] + '</p>')
        index_file.write('<p>' + 'Надпись на этикетке: ' + task['name'] + '</p>')
        for item_order in task['order']:
            index_file.write('<p>' + ' '.join(re.findall(r'(?<=order/).+', item_order)) + '</p>')
        index_file.write('<p>' + 'Количество кодов: ' + str(task['total_number_of_codes']) + '</p>')
        index_file.write('<hr>')
    index_file.close()






if __name__ == "__main__":
    files_order = search_for_orders()
    # print(files_order)
    file_task = reader_task_file()
    print(file_task)
    tasks_to_be_completed = task_designer(files_order, file_task)
    # print(tasks_to_be_completed)
    # for task in tasks_to_be_completed:
    #     print('GTI:', task['gtn'])
    #     print('Надпись на этикетке:', task['name'])
    #     print(task['order'])
    #     for item_order in task['order']:
    #         print(item_order)
    #         print(' '.join(re.findall(r'(?<=order/).+', item_order)))
    #     print('Количество кодов:', task['total_number_of_codes'], '\n')
    name_project = creat_project(tasks_to_be_completed)
    save_task(name_project, tasks_to_be_completed)