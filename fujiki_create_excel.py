# -*- coding: utf-8 -*-

import datetime
import pathlib
import openpyxl as px
import cv2
import os
import numpy as np
import math

now = datetime.datetime.now()   # 現在時刻取得

# 変数
INPUT_PHOTO_PATH = "20201109\dist_20\dist_20_4\Photo"
EXCEL_FILE_NAME = INPUT_PHOTO_PATH + "_data_" + now.strftime("%Y%m%d_%H%M%S") + ".xlsx"
INJECTER_POINT = [515,444]
FPS = 20000
THRESHOLD = 63          # 閾値
THRESHOLD_MAX = 255     # 最大閾値
MINIMUM_AREA = 15       # この数値以下の輪郭面積は除去する
#SPAY_HIGH = 200         # 噴霧角度計算座標（y座標入力）
ANGLE_LINE = 480

A1 = "画像名"
B1 = "時間(s)"
C1 = "平均輝度"
D1 = "最大輪郭面積"
E1 = "横幅(pixel)"
F1 = "縦幅(pixel)"
G1 = "噴霧到達距離(pixel)"
H1 = "噴霧角度(°)"
photo_count = 1     # カウンターの定義

photo_path = pathlib.Path(INPUT_PHOTO_PATH) # pathlib型で取得

wb = px.Workbook()                          # Excelファイル作成
sheet = wb.create_sheet(title = photo_path.parts[-2])   # sheet名を実験条件名に
sheet["A1"] = A1
sheet["B1"] = B1
sheet["C1"] = C1
sheet["D1"] = D1
sheet["E1"] = E1
sheet["F1"] = F1
sheet["G1"] = G1
sheet["H1"] = H1

f_name = list(photo_path.glob('*.png'))         # 画像ファイル取得

for f in f_name:
    photo_count += 1
    img = cv2.imread(os.path.join(INPUT_PHOTO_PATH , f.name))
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    brightness = cv2.mean(gray)                                      # 平均輝度の取得
    print("="*3,"ファイル名",f.name,"="*3)
    print("平均輝度",brightness[0])
    
    # 輪郭面積
    ret,thresh = cv2.threshold(gray,THRESHOLD,THRESHOLD_MAX,cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    max_id, max_area = -1, 0
    for i in range(len(contours)):
        #print('ID', i, 'Area', cv2.contourArea(contours[i]))
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        # 最大輪郭を見つける
        if area > max_area:
            max_area = area
            max_id = i
    cnt = contours[max_id]

    if max_area < 15:
        max_contour_area = 0
        max_x = 0
        min_x = 0
        max_y = 0
        min_y = 0
        width = 0
        height = 0
        spray_d = 0

    else:
        max_contour_area = cv2.contourArea(cnt)
        max_x = cnt[:,:,0].max()    # 最右ピクセル
        min_x = cnt[:,:,0].min()    # 最左ピクセル
        max_y = cnt[:,:,1].max()    # 最下ピクセル
        min_y = cnt[:,:,1].min()    # 最上ピクセル
        width = max_x - min_x       # 横幅
        height = max_y - min_y      # 縦幅
        spray_d = max_y - INJECTER_POINT[0]     # 噴霧到達距離

# 噴霧角算出
    # mask画像作成
    mask = np.zeros(gray.shape[:2], dtype = np.uint8)    # 0で初期化（ゼロ埋め）
    mask[:ANGLE_LINE, ] = 255                        # mask[yの範囲,xの範囲]=白
    msk_img = cv2.bitwise_and(gray,gray,mask = mask)   # ビット単位のAND処理を行いマスク画像に
    msk_ret,msk_thresh = cv2.threshold(msk_img,THRESHOLD,THRESHOLD_MAX,cv2.THRESH_BINARY)
    msk_contours,msk_hierarchy = cv2.findContours(msk_thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    msk_max_id, msk_max_area = -1, 0
    for msk_i in range(len(msk_contours)):
        msk_cnt = msk_contours[msk_i]
        msk_area = cv2.contourArea(msk_cnt)
        if msk_area > msk_max_area:
            msk_max_area = msk_area
            msk_max_id = msk_i
    msk_cnt = msk_contours[msk_max_id]
    angle_line = np.where(msk_cnt[:,:,1] == ANGLE_LINE - 1)
    coordinates_on_line = msk_cnt[angle_line]# 指定軸上の座標
    #計算
    max_angle_coordinates = np.where(coordinates_on_line[:,0] == max(coordinates_on_line[:,0]))
    min_angle_coordinates = np.where(coordinates_on_line[:,0] == min(coordinates_on_line[:,0]))
    r_angle_point = coordinates_on_line[max_angle_coordinates][0]
    l_angle_point = coordinates_on_line[min_angle_coordinates][0]
    spray_angle = (math.atan2(l_angle_point[1] - INJECTER_POINT[1], l_angle_point[0] - INJECTER_POINT[0]) - math.atan2(r_angle_point[1] - INJECTER_POINT[1], r_angle_point[0] - INJECTER_POINT[0])) / math.pi * 180


    print('最大輪郭面積', max_contour_area)
    print('最左ピクセル' , min_x , '最右ピクセル' , max_x)
    print('最上ピクセル' , min_y , '最下ピクセル' , max_y)
    print('横幅', width)
    print('縦幅', height)
    print('噴霧到達距離', spray_d)
    print('噴霧角（右）', r_angle_point)
    print('噴霧角（左）', l_angle_point)
    print('噴霧角', spray_angle)


    # セルに記入
    sheet['A' + str(photo_count)] = f.name
    sheet['B' + str(photo_count)] = 1/FPS*(photo_count-1)
    sheet['C' + str(photo_count)] = brightness[0]
    sheet['D' + str(photo_count)] = max_contour_area
    sheet['E' + str(photo_count)] = width
    sheet['F' + str(photo_count)] = height
    sheet['G' + str(photo_count)] = spray_d
    sheet['H' + str(photo_count)] = spray_angle

    # 処理画像保存
    cv2.drawContours(img, contours, -1, (147, 20, 255), 1)
    cv2.drawContours(img, contours, max_id, (0, 255, 0), 3)
    cv2.circle(img, tuple(r_angle_point), 4, (0, 0, 255), thickness=-1)
    cv2.circle(img, tuple(l_angle_point), 4, (0, 0, 255), thickness=-1)
    result_img = cv2.circle(img, tuple(INJECTER_POINT), 4, (0, 0, 255), thickness=-1)
    cv2.imshow('result_img', result_img)
    cv2.imwrite(os.path.join(INPUT_PHOTO_PATH, 'new_' + f.name), result_img)

# 名前を付けて保存
wb.save(EXCEL_FILE_NAME)

#キー入力で全画像消去
cv2.waitKey(0)
cv2.destroyAllWindows()
