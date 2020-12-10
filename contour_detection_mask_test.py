import cv2
import numpy as np
import matplotlib.pyplot as plt

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
mask = np.zeros(gray.shape[:2], dtype = np.uint8)    # 0で初期化（ゼロ埋め）
mask[MASK_RANGE_LIST[0] : MASK_RANGE_LIST[1], MASK_RANGE_LIST[2] : MASK_RANGE_LIST[3]] = 255                        # mask[yの範囲,xの範囲]=白
masked_img = cv2.bitwise_and(gray,gray,mask = mask)   # ビット単位のAND処理を行いマスク画像に


#thresholdを使って二値化。
ret,thresh = cv2.threshold(masked_img,THRESHOLD,THRESHOLD_MAX,cv2.THRESH_BINARY)

#輪郭を検出。
contours,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# １つずつの輪郭面積を出力
max_id, max_area = -1, 0
for i in range(len(contours)):
    print('ID', i, 'Area', cv2.contourArea(contours[i]))
    cnt = contours[i]
    area = cv2.contourArea(cnt)
    # 最大の輪郭を見つける
    if area > max_area:
        max_area = area
        max_id = i
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