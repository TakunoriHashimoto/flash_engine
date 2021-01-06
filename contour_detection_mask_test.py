import cv2
import numpy as np
import matplotlib.pyplot as plt
import utils

#FILE_PATH = 'test.png'
FILE_PATH = 'cam_angle_test_10000_hight.cih000046.png'
MASK_RANGE_LIST = [400, 600, 400, 600]
THRESHOLD = 63     # 閾値
THRESHOLD_MAX = 255  # 最大閾値

# 画像読み込み
img = cv2.imread(FILE_PATH)
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
print("解像度", img.shape)
# mask画像作成
mask, masked_img = utils.create_mask(gray, MASK_RANGE_LIST)

#thresholdを使って二値化。
ret,thresh = cv2.threshold(masked_img,THRESHOLD,THRESHOLD_MAX,cv2.THRESH_BINARY)

#輪郭を検出。
contours, hierarchy, max_area, max_id = utils.get_contour(thresh)

cnt = contours[max_id]
print("最大輪郭面積",cv2.contourArea(contours[max_id]))

# 全輪郭画像の表示
all_contours=cv2.drawContours(img,contours,-1,(0,255,0),4)

#最大輪郭面積を出力
max_contour = max(contours, key = lambda x: cv2.contourArea(x))
out = np.zeros_like(img)
cv2.drawContours(out, [max_contour], -1, color=255, thickness=-1)

# 表示
cv2.imshow('binarized',thresh)
cv2.imshow('all_contours',all_contours)
cv2.imshow('out.png', out)

# ヒストグラムの取得
hist_full = cv2.calcHist([img],[0],None,[256],[0,256])  # マスクなし
hist_mask = cv2.calcHist([img],[0],mask,[256],[0,256])  # マスクあり

# グラフ整列
plt.subplot(221), plt.imshow(img, 'gray')
plt.subplot(222), plt.imshow(mask,'gray')
plt.subplot(223), plt.imshow(masked_img, 'gray')
plt.subplot(224), plt.plot(hist_full), plt.plot(hist_mask)
plt.xlim([-10,266])
plt.show()