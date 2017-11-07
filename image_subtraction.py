import cv2 as cv
import numpy as np

average = cv.imread('/Users/yusukemorita/Desktop/OUT.png')

for x in range(1, 105):
    num = "%03d" % (x)
    test_image = cv.imread('/Users/yusukemorita/Desktop/test/{}.png'.format(num))

    result = cv.subtract(test_image, average)

    cv.imwrite('/Users/yusukemorita/Desktop/result/{}.png'.format(num), result)



#cv.imshow('result', result)
#cv.waitKey(5000)

#result = cv.subtract(average, test_image)
#cv.imshow('result', result)
#cv.waitKey(0)
