import numpy as np
import cv2

FILE_PATH = 'inj_80_1002001.png'
#FILE_PATH = '40053.jpg'
#FILE_PATH = 'cam_angle_test_10000_hight.cih000046.png'
THRESHOLD = 63     # 閾値
THRESHOLD_MAX = 255  # 最大閾値
INJECTER_POINT = [42,265]


#カラー画像を読み込んでグレースケール値に変換。
img=cv2.imread(FILE_PATH)
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
print('解像度' , img.shape)
#thresholdを使って二値化。
ret,thresh = cv2.threshold(gray,THRESHOLD,THRESHOLD_MAX,cv2.THRESH_BINARY)

#輪郭を検出。
contours,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# １つずつの輪郭面積を出力
max_id, max_area = -1, 0
for i in range(len(contours)):
    #each_contour = img.copy()
    print('ID', i, 'Area', cv2.contourArea(contours[i]))
    #each_contour = cv2.drawContours(each_contour, contours, i, (0,255,0), 2)
    #cv2.imshow('result' + str(i) + '.png', each_contour)
    cnt = contours[i]
    area = cv2.contourArea(cnt)
    # 最大の輪郭を見つける
    if area > max_area:
        max_area = area
        max_id = i
cnt = contours[max_id]
max_x = cnt[...,0].max()                # 最右ピクセル
min_x = cnt[...,0].min()                # 最左ピクセル
max_y = cnt[...,1].max()                # 最下ピクセル
min_y = cnt[...,1].min()                # 最上ピクセル
width = max_x - min_x                   # 横幅
height = max_y - min_y                  # 縦幅
spray_d = max_y - INJECTER_POINT[0]     # 噴霧到達距離

print('最大輪郭面積',cv2.contourArea(contours[max_id]))
print('最左ピクセル' , min_x , '最右ピクセル' , max_x)
print('最上ピクセル' , min_y , '最下ピクセル' , max_y)
print('横幅' , width)
print('縦幅' , height)
print('噴霧到達距離' , spray_d)

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

#キー入力で全画像消去
cv2.waitKey(0)
cv2.destroyAllWindows()