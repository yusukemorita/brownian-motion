import datetime
from subprocess import call
import os
import cv2 as cv
import numpy as np
from functions import sort_and_write_csv

def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
    return cv.LUT(image, table)

def adjust_image(img):
    img = cv.medianBlur(img,5)
    return img

def detect_circles(img):
    circles = cv.HoughCircles(img,cv.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=30,maxRadius=60)
    result = []

    if circles is None:
        print('no circles found in photo_num: {}'.format(photo_num))

    else:
        print('found circles in photo_num: {}'.format(photo_num))
        circles = np.uint16(np.around(circles))
        for circle in circles[0]:
            result.append([circle[0], circle[1]])

    return result

def print_clear(string):
    print('')
    print('')
    print('>'*40)
    print('')
    print(string)
    print('')
    print('>'*40)
    print('')
    print('')

def create_background(dir_path):
    print_clear('creating background image')
    call('convert {}original/0*.png -evaluate-sequence median {}background.png'.format(dir_path, dir_path), shell=True)
    background = cv.imread('{}background.png'.format(dir_path))
    return background

# define necessary variables

current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M")
video_path = '/Users/yusukemorita/Desktop/' + input('input file name in Desktop : ')
dir_path = '/Users/yusukemorita/brownian_motion/{}/'.format(current_time)

# create necessary directories

print_clear('creating directories')
call('mkdir {}'.format(dir_path), shell=True)
call('mkdir {}original'.format(dir_path), shell=True)
call('mkdir {}subtracted'.format(dir_path), shell=True)

# 動画を画像ファイルに変換

print_clear('converting video file to images')
call('ffmpeg -i {} -r 30 {}/original/%03d.png'.format(video_path, dir_path), shell=True)

background = create_background(dir_path)

# 画像から背景画像を引き算, gamma correction

print_clear('subtracting background image from images with particles')
for idx, filename in enumerate(os.listdir(dir_path + 'original')):
    original_image = cv.imread(dir_path + 'original/' + filename)
    result = cv.subtract(original_image, background)
    result = adjust_gamma(result, gamma=2.0)
    cv.imwrite(dir_path + 'subtracted/{}.png'.format("%03d" % (idx + 1)), result)

# 画像の円を検出、circle_arrayにphoto_circles(photo_numと円の座標)を記入
# circle_array = [
#   {"photo_num" => 1, "circles" => [[x1, y1], [x2, y2], [x3, y3]]},
#   {"photo_num" => 2, "circles" => [[x1, y1], [x2, y2], [x3, y3]]},
#                                 ...
#   {"photo_num" => n, "circles" => [[x1, y1], [x2, y2], [x3, y3]]}
# ]
print_clear('detecting circles')
circle_array = []

for photo_num, filename in enumerate(os.listdir(dir_path + 'subtracted')):
    img_path = dir_path + 'subtracted/' + filename
    img = adjust_image(cv.imread(img_path, 0))
    detected_circles = detect_circles(img)

    if len(detected_circles) > 0:
        photo_circles = {
            "photo_num" : photo_num,
            "circles" : detected_circles
            }
        circle_array.append(photo_circles)

# remove empty elements from circle_array
circle_array = [item for item in circle_array if item]

print_clear('writing to csv')
sort_and_write_csv(circle_array, current_time, dir_path)
