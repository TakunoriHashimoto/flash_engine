import utils
import cv2
import matplotlib.pyplot as plt

FILE_PATH = 'cam_angle_test_10000_hight.cih000046.png'
#FILE_PATH = 'test.png'
MASK_RANGE_LIST = [400, 600, 400, 600]


img, gray, ret, thresh = utils.get_img_single(FILE_PATH)
mask, masked_img = utils.create_mask(gray, MASK_RANGE_LIST)

# ヒストグラムの取得
hist_full = cv2.calcHist([gray],[0],None,[256],[0,256])  # マスクなし
hist_mask = cv2.calcHist([gray],[0],mask,[256],[0,256])  # マスクあり

# グラフ整列
plt.subplot(221), plt.imshow(gray, 'gray')
plt.subplot(222), plt.imshow(mask,'gray')
plt.subplot(223), plt.imshow(masked_img, 'gray')
plt.subplot(224), plt.plot(hist_full), plt.plot(hist_mask)
plt.xlim([-10,266])

plt.show()