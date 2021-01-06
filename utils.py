import datetime
import openpyxl as px
import pathlib
import cv2
import matplotlib.pyplot as plt
import numpy as np
import math

INPUT_PHOTO_PATH = "20201109\dist_20\dist_20_4\Photo"

def get_photo_path(INPUT_PHOTO_PATH):
    photo_path = pathlib.Path(INPUT_PHOTO_PATH) # pathlib型で取得
    print("OK_get_photo_path")
    return photo_path

# Excel作成
def create_excel(A1, B1, C1, D1, E1, F1, G1, H1, I1, J1):
    photo_path = get_photo_path(INPUT_PHOTO_PATH)
    wb = px.Workbook()                          # Excelファイル作成
    sheet = wb.create_sheet(title = photo_path.parts[-2])   # sheet名を実験条件名に
    sheet["A1"] = A1
    sheet["B1"] = B1
    sheet["C1"] = C1
    sheet["D1"] = D1
    sheet["E1"] = E1
    sheet["F1"] = F1
    sheet["G1"] = G1
    sheet["H1"] = H1
    sheet["I1"] = I1
    sheet["J1"] = J1
    print("OK_create_excel")
    return wb, sheet

# Excelに書き込み
def enter_excel(
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
    ):
    sheet['A' + str(photo_count)] = f.name
    sheet['B' + str(photo_count)] = 1/FPS*(photo_count-1)
    sheet['C' + str(photo_count)] = brightness[0]
    sheet['D' + str(photo_count)] = mask_brightness[0]
    sheet['E' + str(photo_count)] = max_contour_area
    sheet['F' + str(photo_count)] = max_mask_contour_area
    sheet['G' + str(photo_count)] = width
    sheet['H' + str(photo_count)] = height
    sheet['I' + str(photo_count)] = spray_d
    sheet['J' + str(photo_count)] = spray_angle

# 画像読み込み(ディレクトリ内)
def get_img(INPUT_PHOTO_PATH, START_PHOTO_COUNT = None, IMG_NUMBER = None):
    photo_path = get_photo_path(INPUT_PHOTO_PATH)
    f_name = list(photo_path.glob('*.png'))         # 画像ファイル取得
    del f_name[START_PHOTO_COUNT + IMG_NUMBER :]
    del f_name[: START_PHOTO_COUNT]
    print("OK_get_img")
    return f_name
    
# 画像座標取得
def get_coordinates(FILE_PATH):
    img = cv2.imread(FILE_PATH)
    plt.imshow(img)
    plt.show()

# 画像読み込み(一枚)_カラー画像→グレースケール→二値化
def get_img_single(FILE_PATH, THRESHOLD = 0, THRESHOLD_MAX = 0):
    img = cv2.imread(FILE_PATH)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray,THRESHOLD,THRESHOLD_MAX,cv2.THRESH_BINARY)     # 二値化処理
    print('解像度' , img.shape)
    return img, gray, ret, thresh

# マスク画像作成(四角形)
def create_mask(img, MASK_RANGE_LIST):
    mask = np.zeros(img.shape[:2], dtype = np.uint8)    # 0で初期化（ゼロ埋め）
    mask[MASK_RANGE_LIST[0] : MASK_RANGE_LIST[1], MASK_RANGE_LIST[2] : MASK_RANGE_LIST[3]] = 255    # mask[yの範囲,xの範囲]=白
    masked_img = cv2.bitwise_and(img, img, mask = mask)   # ビット単位のAND処理を行いマスク画像に
    return mask, masked_img

# 輝度計算
def calc_brightness(img):
    brightness = cv2.mean(img)
    return brightness

# 輪郭検出と最大輪郭面積の取得
def get_contour(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    max_id, max_area = -1, 0
    for i in range(len(contours)):
        #each_contour = img.copy()
        #print('ID', i, 'Area', cv2.contourArea(contours[i]))
        #each_contour = cv2.drawContours(each_contour, contours, i, (0,255,0), 2)
        #cv2.imshow('result' + str(i) + '.png', each_contour)
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        # 最大の輪郭を見つける
        if area > max_area:
            max_area = area
            max_id = i
    return contours, hierarchy, max_area, max_id

# 噴霧距離計算
def calc_spray_d(contours, max_id, INJECTER_POINT):
    cnt = contours[max_id]                  # cnt = [点の数,1,2(x,y)]
    max_contour_area = cv2.contourArea(cnt)
    max_x = cnt[:,:,0].max()                # 最右ピクセル
    min_x = cnt[:,:,0].min()                # 最左ピクセル
    max_y = cnt[:,:,1].max()                # 最下ピクセル
    min_y = cnt[:,:,1].min()                # 最上ピクセル
    #max_x_id = cnt[:,:,0].argmax()
    width = max_x - min_x                   # 横幅
    height = max_y - min_y                  # 縦幅
    spray_d = max_y - INJECTER_POINT[0]     # 噴霧到達距離

    print('最大輪郭面積', max_contour_area)
    print('最左ピクセル' , min_x , '最右ピクセル' , max_x)
    print('最上ピクセル' , min_y , '最下ピクセル' , max_y)
    print('横幅' , width)
    print('縦幅' , height)
    print('噴霧到達距離' , spray_d)
    #print('test',cnt[:,:,0].argmax())
    #print('x',max_x,'y',cnt[:,:,1][max_x_id])# xが最大の座標取得
    return max_contour_area, width, height, spray_d

# 噴霧角計算
def calc_spray_angle(img, THRESHOLD, THRESHOLD_MAX, ANGLE_LINE, INJECTER_POINT):
    ret, thresh = cv2.threshold(img, THRESHOLD, THRESHOLD_MAX, cv2.THRESH_BINARY)
    contours, hierarchy, max_area, max_id = get_contour(thresh)
    cnt = contours[max_id]                  # cnt = [点の数,1,2(x,y)]
    angle_line = np.where(cnt[:,:,1] == ANGLE_LINE - 1)
    coordinates_on_line = cnt[angle_line]# 指定軸上の座標
    max_angle_coordinates = np.where(coordinates_on_line[:,0] == max(coordinates_on_line[:,0]))
    min_angle_coordinates = np.where(coordinates_on_line[:,0] == min(coordinates_on_line[:,0]))
    r_angle_point = coordinates_on_line[max_angle_coordinates][0]
    l_angle_point = coordinates_on_line[min_angle_coordinates][0]
    spray_angle = (math.atan2(l_angle_point[1] - INJECTER_POINT[1], l_angle_point[0] - INJECTER_POINT[0]) - math.atan2(r_angle_point[1] - INJECTER_POINT[1], r_angle_point[0] - INJECTER_POINT[0])) / math.pi * 180
    print('噴霧角（右）', r_angle_point)
    print('噴霧角（左）', l_angle_point)
    print('噴霧角', spray_angle)
    return r_angle_point, l_angle_point, spray_angle

"""
#####################################################
def main():
    wb, sheet = create_excel(
        A1 = "画像名",
        B1 = "時間(s)",
        C1 = "平均輝度",
        D1 = "平均輝度(mask)",
        E1 = "最大輪郭面積",
        F1 = "最大輪郭面積(mask)",
        G1 = "横幅(pixel)",
        H1 = "縦幅(pixel)",
        I1 = "噴霧到達距離(pixel)"
    )

    f_name = get_img(INPUT_PHOTO_PATH)

    photo_count = 1
    for f in f_name:
        photo_count += 1
        enter_excel(sheet,photo_count, f)
    wb.save("test.xlsx")
    #キー入力で全画像消去
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

# 不要輪郭除去

"""