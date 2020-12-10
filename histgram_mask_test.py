import cv2
import numpy as np
import matplotlib.pyplot as plt

#FILE_PATH = 'test.png'
FILE_PATH = 'cam_angle_test_10000_hight.cih000046.png'

# グレーで画像読み込み
img = cv2.imread(FILE_PATH,0)

print("解像度", img.shape)
# mask画像作成
mask = np.zeros(img.shape[:2], dtype = np.uint8)    # 0で初期化（ゼロ埋め）
mask[400:600, 400:600] = 255                        # mask[yの範囲,xの範囲]=白
masked_img = cv2.bitwise_and(img,img,mask = mask)   # ビット単位のAND処理を行いマスク画像に

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