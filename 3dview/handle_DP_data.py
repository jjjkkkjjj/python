import os
import csv

def write_simpleDP_data(diff_detail, filepath1, filepath2, Limit):
    tmp1 = filepath1.split('/')
    tmp2 = filepath2.split('/')

    filepath = ""

    for i in range(len(tmp1) - 1):
        filepath += tmp1[i] + "/"
    filepath += "DPdata"

    if not os.path.isdir(filepath):
        os.makedirs(filepath)

    filepath += "/" + tmp1[len(tmp1) - 1].rstrip('.CSV') + "-" + tmp2[len(tmp2) - 1].rstrip('.CSV') + "-" + str(Limit) + ".CSV"

    with open(filepath, "wb") as f:
        writer = csv.writer(f)
        for corr_data in diff_detail:
            writer.writerow(corr_data)

    return

def read_simpleDP_data(input_filepath, reference_filepath):
    tmp1 = input_filepath.split('/')
    tmp2 = reference_filepath.split('/')

    filepath = ""
    return_data = []

    for i in range(len(tmp1) - 1):
        filepath += tmp1[i] + "/"
    filepath += "DPdata"

    files = os.listdir(filepath)

    choosable_list = []

    input_name = tmp1[len(tmp1) - 1].rstrip('.CSV')
    reference_name = tmp2[len(tmp2) - 1].rstrip('.CSV')

    for file in files:
        name = file.split('-')
        if name[0] == input_name and name[1] == reference_name:
            choosable_list.append(name[2].rstrip('.CSV'))

    if len(choosable_list) == 0:
        return False, return_data, -1
    else:
        print ("choose limitation number")
        print (choosable_list)

    input_str = str(input())
    while not input_str in choosable_list:
        print ("you chose wrong number")
        input_str = str(input())

    filepath += "/" + input_name + "-" + reference_name + "-" + input_str + ".CSV"
    with open(filepath, "rb") as f:
        reader = csv.reader(f)

        for row in reader:
            tmp = []
            for data in row:
                tmp.append(int(data))
            return_data.append(tmp)

    return True, return_data, int(input_str)