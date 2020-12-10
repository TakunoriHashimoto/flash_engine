import cv2
import matplotlib.pyplot as plt

#FILE_PATH = 'test.png'
FILE_PATH = 'inj_80_1000384.png'

img = cv2.imread(FILE_PATH)
plt.imshow(img)
plt.show()
