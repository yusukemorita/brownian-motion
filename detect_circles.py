import cv2 as cv
import numpy as np
import xlsxwriter

img_path = '/Users/yusukemorita/' + input('input file path after /Users/yusukemorita/ : ')
img = cv.imread(img_path,0)
img = cv.medianBlur(img,5)

#cimg = cv.cvtColor(img,cv2.COLOR_GRAY2BGR)

circles = cv.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,
        param1=50,param2=18,minRadius=0,maxRadius=30)
circles = np.uint16(np.around(circles))

# first circle
print('x: ' + str(circles[0][0][0]))
print('y: ' + str(circles[0][0][1]))
# second circle
print('x: ' + str(circles[0][1][0]))
print('y: ' + str(circles[0][1][1]))

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('/Users/yusukemorita/Desktop/test_excel.xlsx')
worksheet = workbook.add_worksheet()
circle_array = []

for idx, circle in enumerate(circles[0]):
    circle_array.append([circle[0], circle[1]])

print( circle_array )

# Some data we want to write to the worksheet.
#expenses = (
#    ['Rent', 1000],
#    ['Gas',   100],
#    ['Food',  300],
#    ['Gym',    50],
#)

worksheet.write(0, 1, 'circle_1')
worksheet.write(0, 3, 'circle_2')
# Start from the first cell. Rows and columns are zero indexed.
row = 1
col = 1

# Iterate over the data and write it out row by row.
for x_val, y_val in (circle_array):
    worksheet.write(row, col    , x_val)
    worksheet.write(row, col + 1, y_val)
    col += 2

workbook.close()

#for i in circles[0,:]:
#    # draw the outer circle
#    cv.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
#    # draw the center of the circle
#    cv.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
#
#cv.imshow('detected circles',cimg)
#cv.waitKey(0)
#cv.destroyAllWindows()
