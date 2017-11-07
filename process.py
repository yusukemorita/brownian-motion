import datetime
from subprocess import call
import os
import cv2 as cv
import numpy as np
from functions import sort_and_write_to_excel

# define necessary variables

current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M")
video_path = '/Users/yusukemorita/' + input('input file path after /Users/yusukemorita/ (eg. Desktop/30sec.mov) : ')
dir_path = '/Users/yusukemorita/brownian_motion/{}/'.format(current_time)
background = cv.imread('/Users/yusukemorita/brownian_motion/background.png')

# create necessary directories

call('mkdir ~/brownian_motion/{}'.format(current_time), shell=True)
call('mkdir ~/brownian_motion/{}/original'.format(current_time), shell=True)
call('mkdir ~/brownian_motion/{}/subtracted'.format(current_time), shell=True)

# 動画を画像ファイルに変換

call('ffmpeg -i {} -r 10 ~/brownian_motion/{}/original/%03d.png'.format(video_path, current_time), shell=True)

# 画像から背景画像を引き算

for idx, filename in enumerate(os.listdir(dir_path + 'original')):
    original_image = cv.imread(dir_path + 'original/' + filename)
    subtracted_image = cv.subtract(original_image, background)
    cv.imwrite(dir_path + 'subtracted/{}.png'.format("%03d" % (idx + 1)), subtracted_image)

# 画像の円を検出、circle_arrayに円の座標を記入
# circle_array = [
#   {"photo_num" => 1, "circles" => [[x1, y1], [x2, y2], [x3, y3]]},
#   {"photo_num" => 2, "circles" => [[x1, y1], [x2, y2], [x3, y3]]},
#                                 ...
#   {"photo_num" => n, "circles" => [[x1, y1], [x2, y2], [x3, y3]]}
# ]
circle_array = []

for photo_num, filename in enumerate(os.listdir(dir_path + 'subtracted')):
    img_path = dir_path + 'subtracted/' + filename
    img = cv.imread(img_path, 0)
    img = cv.medianBlur(img,5)

    try:
        circles = cv.HoughCircles(img,cv.HOUGH_GRADIENT,1,20,param1=50,param2=18,minRadius=0,maxRadius=100)
        circles = np.uint16(np.around(circles))
        print('found circles in photo_num: {}'.format(photo_num))

        circle_hash = {
            "photo_num" : photo_num,
            "circles" : []
            }
        for circle in circles[0]:
            circle_hash["circles"].append([circle[0], circle[1]])

        circle_array.append(circle_hash)

    except:
        print('no circles found in photo_num: {}'.format(photo_num))

# remove empty elements from circle_array
circle_array = [item for item in circle_array if item]

sort_and_write_to_excel(circle_array, current_time)
