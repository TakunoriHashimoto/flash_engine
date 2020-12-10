# -*- coding: utf-8 -*-

import datetime
import pathlib
import openpyxl as px
import cv2
import os
import numpy as np

now = datetime.datetime.now()   # 現在時刻取得

# 変数
INPUT_PHOTO_PATH = "20201203\inj_80\\1"
EXCEL_FILE_NAME = INPUT_PHOTO_PATH + "_data_" + now.strftime("%Y%m%d_%H%M%S") + ".xlsx"
INJECTER_POINT = [42,265]
FPS = 20000
THRESHOLD = 63          # 閾値
THRESHOLD_MAX = 255     # 最大閾値
MINIMUM_AREA = 15       # この数値以下の輪郭面積は除去する

A1 = "画像名"
B1 = "時間(s)"
C1 = "平均輝度"
D1 = "最大輪郭面積"
E1 = "横幅(pixel)"
F1 = "縦幅(pixel)"
G1 = "噴霧到達距離(pixel)"
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

f_name = list(photo_path.glob('*.png'))         # 画像ファイル取得

for f in f_name:
    photo_count += 1
    img = cv2.imread(os.path.join(INPUT_PHOTO_PATH , f.name),0)     # グレーで画像の読み込み
    brightness = cv2.mean(img)                                      # 平均輝度の取得
    print("="*3,"ファイル名",f.name,"="*3)
    print("平均輝度",brightness[0])
    
    # 輪郭面積
    ret,thresh = cv2.threshold(img,THRESHOLD,THRESHOLD_MAX,cv2.THRESH_BINARY)
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

    if max_area < 8000:
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
        max_x = cnt[...,0].max()    # 最右ピクセル
        min_x = cnt[...,0].min()    # 最左ピクセル
        max_y = cnt[...,1].max()    # 最下ピクセル
        min_y = cnt[...,1].min()    # 最上ピクセル
        width = max_x - min_x       # 横幅
        height = max_y - min_y      # 縦幅
        spray_d = max_y - INJECTER_POINT[0]     # 噴霧到達距離

    print('最大輪郭面積', max_contour_area)
    print('最左ピクセル' , min_x , '最右ピクセル' , max_x)
    print('最上ピクセル' , min_y , '最下ピクセル' , max_y)
    print('横幅', width)
    print('縦幅', height)
    print('噴霧到達距離', spray_d)

    # セルに記入
    sheet['A' + str(photo_count)] = f.name
    sheet['B' + str(photo_count)] = 1/FPS*(photo_count-1)
    sheet['C' + str(photo_count)] = brightness[0]
    sheet['D' + str(photo_count)] = max_contour_area
    sheet['E' + str(photo_count)] = width
    sheet['F' + str(photo_count)] = height
    sheet['G' + str(photo_count)] = spray_d

# 名前を付けて保存
wb.save(EXCEL_FILE_NAME)

#キー入力で全画像消去
cv2.waitKey(0)
cv2.destroyAllWindows()
