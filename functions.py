import xlsxwriter
import csv

current_circle_positions = []
# [{"circle_id" : 1, "x" : x, "y" : y},
#  {"circle_id" : 2, "x" : x, "y" : y},
#                ...
#  {"circle_id" : n, "x" : x, "y" : y}]

def find_closest_position(circle): # circle = [x, y]

    min_diff = 1000
    min_id = None

    for position in current_circle_positions:
        diff = abs(circle[0] - int(position["x"])) + abs(circle[1] - int(position["y"]))
        if diff < min_diff:
            min_diff = diff
            min_id = position["circle_id"]

    if min_diff < 50:
        current_circle_positions[min_id]["x"] = circle[0]
        current_circle_positions[min_id]["y"] = circle[1]
        return min_id
    else: # create new circle
        new_id = len(current_circle_positions)
        current_circle_positions.append({
            "circle_id" : new_id,
            "x" : circle[0],
            "y" : circle[1]
            })
        return new_id

def sort_and_write_to_excel(array, file_name, dir_path):

    workbook = xlsxwriter.Workbook(dir_path + file_name + '.xlsx')
    worksheet = workbook.add_worksheet()

    for photo_circles in array:
        row = photo_circles["photo_num"] + 2
        worksheet.write(row, 0, photo_circles["photo_num"])
        print('writing photo_num : {}'.format(photo_circles["photo_num"]))
        for circle in photo_circles["circles"]:
            # circle = [x1, y1]
            col = find_closest_position(circle) * 2 + 1
            worksheet.write(row, col    , circle[0])
            worksheet.write(row, col + 1, circle[1])

    # add labels to top of worksheet
    for idx, item in enumerate(current_circle_positions):
        worksheet.write(0, idx * 2 + 1, item["circle_id"])
        worksheet.write(1, idx * 2 + 1, 'x')
        worksheet.write(1, idx * 2 + 2, 'y')

    workbook.close()

def sort_and_write_csv(array, file_name, dir_path):

    # f = open('/Users/yusukemorita/brownian_motion/raw_data.csv','a')
    f = open(dir_path + file_name + '.csv','w')

    for photo_circles in array:
        print('writing photo_num : {}'.format(photo_circles["photo_num"]))
        for circle in photo_circles["circles"]: # circle = [x1, y1]
            circle_id = find_closest_position(circle)
            csv_array =[photo_circles["photo_num"], circle_id + 3, circle[0], circle[1]]
            f.write(','.join(str(x) for x in csv_array) + '\n')

    f.close()
