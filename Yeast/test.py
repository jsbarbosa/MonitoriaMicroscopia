import cv2
import matplotlib.pyplot as plt

im = cv2.imread('yeast.jpg')
imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)

edges = cv2.Canny(imgray, 100, 200)
# laplacian = cv2.Laplacian(imgray, cv2.CV_64F)
#
# circles = cv2.HoughCircles(imgray, cv2.HOUGH_GRADIENT, 1, 20,
#                             param1=50, param2=30, minRadius=0, maxRadius=0)
#
#
# circles = np.uint16(np.around(circles))
# for i in circles[0,:]:
#     # draw the outer circle
#     cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
#     # draw the center of the circle
#     cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
#
# # ret, thresh = cv2.threshold(imgray, 100, 255, 0)
# # im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
# #
# # cv2.drawContours(im, contours, -1, (0,255,0), 3)
#
# # im = laplacian
# # im = edges

cv2.imshow("image", edges)
cv2.waitKey(0)
cv2.destroyAllWindows()
