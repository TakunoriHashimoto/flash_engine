import utils
import cv2

#FILE_PATH = '40053.jpg'
#FILE_PATH = "20201109\dist_20\dist_20_4\Photo\dist_20_4_000049.png"
FILE_PATH = 'cam_angle_test_10000_hight.cih000046.png'
THRESHOLD = 63     # 閾値
THRESHOLD_MAX = 255  # 最大閾値
#INJECTER_POINT = [490,433]
#ANGLE_LINE = 560
INJECTER_POINT = [490,434]
#INJECTER_POINT = [515,444]
ANGLE_LINE = 480
MASK_RANGE_LIST = [None, ANGLE_LINE, None, None]

#カラー画像→グレースケール→二値化
img, gray, ret, thresh = utils.get_img_single(FILE_PATH, THRESHOLD, THRESHOLD_MAX)

#輪郭を検出
contours, hierarchy, max_area, max_id = utils.get_contour(thresh)

#噴霧距離計算
max_contour_area, width, height, spray_d = utils.calc_spray_d(contours, max_id, INJECTER_POINT)

# 噴霧角算出
mask, msk_img = utils.create_mask(gray, MASK_RANGE_LIST)
r_angle_point, l_angle_point, spray_angle = utils.calc_spray_angle(msk_img, THRESHOLD, THRESHOLD_MAX, ANGLE_LINE, INJECTER_POINT)

# 全輪郭画像の表示
cv2.drawContours(img, contours, -1, (147, 20, 255), 1)
cv2.drawContours(img, contours, max_id, (0, 255, 0), 3)
cv2.circle(img, tuple(r_angle_point), 4, (0, 0, 255), thickness=-1)
cv2.circle(img, tuple(l_angle_point), 4, (0, 0, 255), thickness=-1)
all_contours = cv2.circle(img, tuple(INJECTER_POINT), 4, (0, 0, 255), thickness=-1)

#最大輪郭面積を出力
#max_contour = max(contours, key = lambda x: cv2.contourArea(x))
#out = np.zeros_like(img)
#cv2.drawContours(out, [max_contour], -1, color=255, thickness=-1)

# 表示
#cv2.imshow('binarized',thresh)
cv2.imshow('all_contours',all_contours)
#cv2.imshow('out.png', out)
#cv2.imshow('mask', msk_img)
cv2.imwrite('hoge4.png', all_contours)

#キー入力で全画像消去
cv2.waitKey(0)
cv2.destroyAllWindows()