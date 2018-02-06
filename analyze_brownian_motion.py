import datetime
from subprocess import call
import os
import cv2 as cv
import numpy as np
import csv
import collections

current_circle_positions = []
# [{"circle_id" : 1, "x" : x, "y" : y},
#  {"circle_id" : 2, "x" : x, "y" : y},
#                ...
#  {"circle_id" : n, "x" : x, "y" : y}]
# 0 <= circle_id

def main():
    # define necessary variables
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    vid_filename = input('input file name in Desktop : ')
    video_path = '/Users/yusukemorita/Desktop/' + vid_filename
    dir_path = '/Users/yusukemorita/brownian_motion/{}/'.format(current_time)

    # 画像の処理
    make_directories(dir_path)
    convert_video_to_photos(video_path, dir_path)
    background = create_background(dir_path)
    subtract_background(dir_path, background)

    # 画像の円を検出、circle_arrayにphoto_circles(photo_numと円の座標)を記入
    # circle_array = [
    #   {'photo_num': 1, 'x': 123, 'y': 345},
    #   {'photo_num': 1, 'x': 123, 'y': 345},
    #   {'photo_num': 1, 'x': 123, 'y': 345},
    #   {'photo_num': 2, 'x': 123, 'y': 345},
    #   {'photo_num': 2, 'x': 123, 'y': 345},
    #                   ...
    #   {'photo_num': n, 'x': 123, 'y': 345}
    # ]
    print_clear('detecting circles')
    circle_array = []

    for photo_num, filename in enumerate(os.listdir(dir_path + 'subtracted')):
        img_path = dir_path + 'subtracted/' + filename
        img = adjust_image(cv.imread(img_path, 0))
        detected_circles = detect_circles(img)

        if len(detected_circles) > 0:
            print('found circles in photo_num: {}'.format(photo_num))
            for circle in detected_circles:
                circle_hash = {
                    'photo_num' : photo_num,
                    'x' : circle[0],
                    'y' : circle[1]
                }
                circle_array.append(circle_hash)

        else:
            print('no circles found in photo_num: {}'.format(photo_num))

    circle_array = add_circle_ids(circle_array)
    circle_array, common_ids = remove_scarce_circles(circle_array)

    new_id = int(input('input smallest new id : '))
    write_csv(circle_array, dir_path, new_id, common_ids)
    print_coverage(circle_array, new_id, vid_filename)
    print('finished analysing {}'.format(vid_filename))

def make_directories(dir_path):
    call('mkdir {}'.format(dir_path), shell=True)
    call('mkdir {}original'.format(dir_path), shell=True)
    call('mkdir {}subtracted'.format(dir_path), shell=True)

def convert_video_to_photos(video_path, dir_path):
    print_clear('converting video file to images')
    call('ffmpeg -i {} -r 30 {}/original/%04d.png'.format(video_path, dir_path), shell=True)

def subtract_background(dir_path, background):
    print_clear('subtracting background image from images')
    for idx, filename in enumerate(os.listdir(dir_path + 'original')):
        original_image = cv.imread(dir_path + 'original/' + filename)
        result = cv.subtract(original_image, background)
        result = adjust_gamma(result, gamma=2.0)
        cv.imwrite(dir_path + 'subtracted/{}.png'.format(filename.split('.')[0]), result)

def find_closest_circle_id(circle): # circle = {'photo:num': n, 'x': x, 'y': y}
    min_diff = 1000
    min_id = None

    for position in current_circle_positions:
        diff = abs(int(circle['x']) - int(position["x"])) + abs(int(circle['y']) - int(position["y"]))
        if diff < min_diff:
            min_diff = diff
            min_id = position["circle_id"]

    if min_diff < 50:
        current_circle_positions[min_id]["x"] = circle['x']
        current_circle_positions[min_id]["y"] = circle['y']
        return min_id
    else: # create new circle
        new_id = len(current_circle_positions)
        current_circle_positions.append({
            "circle_id" : new_id,
            "x" : circle['x'],
            "y" : circle['y']
            })
        return new_id

def add_circle_ids(array):
    for circle in array:
        circle.update({'circle_id': find_closest_circle_id(circle)})
    return array

def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
    return cv.LUT(image, table)

def adjust_image(img):
    img = cv.medianBlur(img,5)
    return img

def detect_circles(img):
    circles = cv.HoughCircles(
        img,                # 画像
        cv.HOUGH_GRADIENT,  # method
        1,                  # dp
        10,                 # minDist (circle間の最小距離)
        param1=50,          # param1
        param2=10,          # 大きいほど真円に近い円しか検出されない
        minRadius=0,       # 最小半径
        maxRadius=120        # 最大半径
    )
    result = []

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0]:
            result.append([circle[0], circle[1]])

    result = remove_duplicates(result)
    return result

def remove_duplicates(circles):
    result = []
    for c in circles:
        duplicate_count = sum( (abs(r[0] - c[0]) + abs(r[1] - c[1]) < 50) for r in result)
        if duplicate_count == 0:
            result.append(c)
    return result

def remove_scarce_circles(array):
    result = []
    seq = [circle['circle_id'] for circle in array]
    most_common_3 = collections.Counter(seq).most_common(3) # [(circle_id, count), ...]
    common_ids = [i[0] for i in most_common_3]

    for circle in array:
        if circle['circle_id'] in common_ids:
            result.append(circle)
    result = sorted(result, key=lambda k: k['circle_id'])
    return result, common_ids

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
    call('convert {}original/??0?.png -evaluate-sequence median {}background.png'.format(dir_path, dir_path), shell=True)
    background = cv.imread('{}background.png'.format(dir_path))
    return background

def write_csv(array, dir_path, new_id, common_ids):
    print_clear('writing to csv')
    csv_name = '_'.join([str(new_id), str(new_id + 1), str(new_id + 2)])
    f = open(dir_path + csv_name + '.csv', 'w', newline='')
    for common in common_ids:
        for circle in array: # circle = {'circle_id': id, 'photo:num': n, 'x': x, 'y': y}
            if circle['circle_id'] == common:
                csv_array = [circle['photo_num'], new_id, circle['x'], circle['y']]
                f.write(','.join(str(i) for i in csv_array) + '\n')
        new_id += 1
    f.close()

def print_coverage(array, new_id, filename):
    f = open('/Users/yusukemorita/brownian_motion/coverage.csv','a')
    seq = [circle['circle_id'] for circle in array]
    common_ids = collections.Counter(seq).most_common(3) # [(circle_id, count), ...]
    f.write(file_name + '\n')
    for common in common_ids:
        photo_nums = [x['photo_num'] for x in array if x['circle_id'] == common[0]]
        range_ = max(photo_nums) - min(photo_nums)
        percent = 100 * common[1] / range_
        print('circle_id: {}, coverage: {}%'.format(new_id, percent))
        f.write('id: {}, {}%\n'.format(new_id, percent))
        new_id += 1
    f.close()

main()
