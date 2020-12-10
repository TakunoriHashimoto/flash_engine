import cv2
import numpy as np
import matplotlib.pyplot as plt

FILE_PATH = '4030.jpg'
#FILE_PATH = 'dist_20_4_000098.png'
#FILE_PATH = 'cam_angle_test_10000_hight.cih000046.png'

# グレーで画像の読み込み
img = cv2.imread(FILE_PATH,0)
print("解像度", img[:,0]) # (30*40)


# 平均輝度の取得
brightness = cv2.mean(img)
print(brightness[0])

# ヒストグラムの取得
img_hist_cv = cv2.calcHist([img], [0], mask=None, histSize=[256], ranges=[0, 256])

# ヒストグラムの表示
plt.plot(img_hist_cv)
plt.show()


"""
minmum y max y
"""