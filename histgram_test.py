import utils
import cv2
import matplotlib.pyplot as plt

#FILE_PATH = 'dist_20_4_000098.png'
FILE_PATH = 'cam_angle_test_10000_hight.cih000046.png'

img, gray, ret, thresh = utils.get_img_single(FILE_PATH)
brightness = utils.calc_brightness(gray)
print(brightness[0])

# ヒストグラムの取得
img_hist_cv = cv2.calcHist([img], [0], mask=None, histSize=[256], ranges=[0, 256])

# ヒストグラムの表示
plt.plot(img_hist_cv)
plt.show()