import xlsxwriter

workbook = xlsxwriter.Workbook('/Users/yusukemorita/Desktop/test.xlsx')
worksheet = workbook.add_worksheet()

current_circle_positions = [
    {"circle_id" : 1, "x" : 12, "y" : 1},
    {"circle_id" : 2, "x" : 34, "y" : 2},
    {"circle_id" : 3, "x" : 56, "y" : 3}
    ]

for idx, item in enumerate(current_circle_positions):
    worksheet.write(0, idx * 2 + 1, item["circle_id"])
    worksheet.write(1, idx * 2 + 1, 'x')
    worksheet.write(1, idx * 2 + 2, 'y')


#for circle_hash in array:
#    row = circle_hash["photo_num"] + 2
#    worksheet.write(row, 1, row - 2)
#    for circle in circle_hash["circles"]:
#        # circle = [x1, y1]
#        col = find_closest_position(circle) * 2 + 1 # or something like that
#        worksheet.write(row, col    , circle[0])
#        worksheet.write(row, col + 1, circle[1])

workbook.close()
