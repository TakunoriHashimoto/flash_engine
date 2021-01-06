# -*- coding: utf-8 -*-

import utils
import datetime
import cv2
import os
import numpy as np

now = datetime.datetime.now()   # 現在時刻取得


# 変数
INPUT_PHOTO_PATH = "20201109\dist_20\dist_20_4\Photo"
EXCEL_FILE_NAME = INPUT_PHOTO_PATH + "_data_" + now.strftime("%Y%m%d_%H%M%S") + ".xlsx"
INJECTER_POINT = [517,444]
FPS = 20000
MASK_RANGE_LIST = [400, 600, 400, 600]
THRESHOLD = 63              # 閾値
THRESHOLD_MAX = 255         # 最大閾値
START_PHOTO_COUNT = 20      # 処理開始インデックス
IMG_NUMBER = 5              # 処理する枚数
ANGLE_LINE = 480            # 噴霧角度計算用

wb, sheet = utils.create_excel(
    A1 = "画像名",
    B1 = "時間(s)",
    C1 = "平均輝度",
    D1 = "平均輝度(mask)",
    E1 = "最大輪郭面積",
    F1 = "最大輪郭面積(mask)",
    G1 = "横幅(pixel)",
    H1 = "縦幅(pixel)",
    I1 = "噴霧到達距離(pixel)",
    J1 = "噴霧角度(°)"
)

f_name = utils.get_img(INPUT_PHOTO_PATH, START_PHOTO_COUNT, IMG_NUMBER)
photo_count = 1     # カウンターの定義


# mask画像作成
mask = np.zeros((1024, 1024), dtype = np.uint8)    # 0で初期化（ゼロ埋め）
mask[MASK_RANGE_LIST[0] : MASK_RANGE_LIST[1], MASK_RANGE_LIST[2] : MASK_RANGE_LIST[3]] = 255    # mask[yの範囲,xの範囲]=白

for f in f_name:
    photo_count += 1
    img, gray, ret, thresh = utils.get_img_single(os.path.join(INPUT_PHOTO_PATH , f.name), THRESHOLD, THRESHOLD_MAX)
    masked_img = cv2.bitwise_and(gray,gray,mask = mask)               # マスク画像合成
    brightness = utils.calc_brightness(gray)                                      # 平均輝度の取得
    mask_brightness = utils.calc_brightness(masked_img)

    print("="*3,"ファイル名",f.name,"="*3)
    print("平均輝度",brightness[0])
    print("平均輝度(mask)",mask_brightness[0])
    
    # 輪郭面積
    contours, hierarchy, max_area, max_id = utils.get_contour(thresh)
    # 噴霧角計算
    max_contour_area, width, height, spray_d = utils.calc_spray_d(contours, max_id, INJECTER_POINT)
    # mask輪郭面積#############################################
    mask_ret,mask_thresh = cv2.threshold(masked_img,THRESHOLD,THRESHOLD_MAX,cv2.THRESH_BINARY)
    mask_contours, mask_hierarchy, mask_max_area, mask_max_id = utils.get_contour(mask_thresh)
    mask_cnt = mask_contours[mask_max_id]
    max_mask_contour_area = cv2.contourArea(mask_cnt)

    # 噴霧角算出################################################
    spray_mask = np.zeros(gray.shape[:2], dtype = np.uint8)    # 0で初期化（ゼロ埋め）
    spray_mask[:ANGLE_LINE, ] = 255                        # mask[yの範囲,xの範囲]=白
    msk_img = cv2.bitwise_and(gray,gray,mask = spray_mask)   # ビット単位のAND処理を行いマスク画像に
    r_angle_point, l_angle_point, spray_angle = utils.calc_spray_angle(msk_img, THRESHOLD, THRESHOLD_MAX, ANGLE_LINE, INJECTER_POINT)

    print("最大輪郭面積(mask):",max_mask_contour_area,"\n")

    # セルに記入
    utils.enter_excel(
        sheet,
        photo_count,
        f,
        FPS,
        brightness,
        mask_brightness,
        max_contour_area,
        max_mask_contour_area,
        width,
        height,
        spray_d,
        spray_angle
    )

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