import cv2
import numpy as np

## Reading an image
image = cv2.imread("qr_r.jpg", cv2.IMREAD_UNCHANGED)

## New width and height to resize the image
width = 512
height = 512

## Resizing the image
try:
    resized_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
except Exception as e:
    print(str(e))

## Displaying the image 
#cv2.imshow("Resized image", resized_image)
cv2.imwrite("qr_resize.jpg", resized_image)
cv2.waitKey(0)
cv2.destroyAllWindows()