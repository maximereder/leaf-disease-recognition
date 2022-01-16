import os
import cv2, csv
import numpy as np
from PIL import Image

def get_image_informations(directory, img, file_name, save):
    image = cv2.imread(img)
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    hsv = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)

    # LEAF AREA
    low_green = np.array([0, 35, 65])
    high_green = np.array([255, 255, 255])
    mask1 = cv2.inRange(hsv, low_green, high_green)
    cnts1, h1 = cv2.findContours(mask1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # SAFE
    low_safe = np.array([40, 60, 30])
    high_safe = np.array([170, 255, 255])
    mask2 = cv2.inRange(hsv, low_safe, high_safe)
    cnts2, h2 = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # NECROSIS
    low_orange = np.array([10, 100, 100])
    high_orange = np.array([18, 255, 255])
    mask3 = cv2.inRange(hsv, low_orange, high_orange)
    cnts3, h3 = cv2.findContours(mask3, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    low_black = np.array([0, 0, 0])
    high_black = np.array([72, 99, 139])
    mask4 = cv2.inRange(hsv, low_black, high_black)
    cnts4, h4 = cv2.findContours(mask4, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    min_area = 50000
    leaf_contour_viewed = []
    leaf_area = 0
    for contour in cnts1:
        area = cv2.contourArea(contour)
        leaf_area += area
        if area > min_area:
            leaf_contour_viewed.append(contour)
            cv2.drawContours(image, contour, -1, (0, 0, 255), 4)

    safe_contours = []
    necrosis_areas = []
    necrosis_number = []
    pycnides_areas = []
    pycnides_number = []
    for i in range(len(leaf_contour_viewed)):
        safe_contours.append([])
        necrosis_number.append(0)
        necrosis_areas.append(0)
        pycnides_areas.append(0)
        pycnides_number.append(0)

    min_area = 1000
    for i in range(len(h2[0])):
        current_contour = [int(n) for n in cnts2[i][0][0]]
        area = cv2.contourArea(cnts2[i])
        if area > min_area:
            for y in range(len(leaf_contour_viewed)):
                if cv2.pointPolygonTest(leaf_contour_viewed[y], current_contour, False) != -1:
                    safe_contours[y].append(cnts2[i])
                    cv2.drawContours(image, cnts2[i], -1, (200, 200, 200), 4)

    if len(cnts3) > 0:
        min_area = 300
        for i in range(len(h3[0])):
            current_contour = [int(n) for n in cnts3[i][0][0]]
            if h3[0][i][3] != -1:
                area = cv2.contourArea(cnts3[i])
                if area > min_area:
                    for y in range(len(leaf_contour_viewed)):
                        if cv2.pointPolygonTest(leaf_contour_viewed[y], current_contour, False) == 1:
                            necrosis_areas[len(leaf_contour_viewed)-1-y] += area
                            necrosis_number[len(leaf_contour_viewed)-1-y] += 1

    pycnide_contour = []
    if len(cnts4) > 0:
        max_area = 500000
        for i in range(len(h4[0])):
            current_contour = [int(n) for n in cnts4[i][0][0]]
            if h4[0][i][3] != -1:
                area = cv2.contourArea(cnts4[i])
                if area < max_area:
                    in_area = False
                    for y in range(len(leaf_contour_viewed)):
                        print(y)
                        # On itère dans chaque safe zone de chaque feuille
                        for z in range(len(safe_contours[y])):
                            if cv2.pointPolygonTest(safe_contours[y][z], current_contour, False) == 1:
                                in_area = True
                        if cv2.pointPolygonTest(leaf_contour_viewed[y], current_contour, False) == 1:
                            if not in_area:
                                cv2.drawContours(image, cnts4[i], -1, (150, 150, 255), 2)
                                pycnides_areas[len(leaf_contour_viewed)-1-y] += area
                                pycnides_number[len(leaf_contour_viewed)-1-y] += 1

    if save:
        cv2.imwrite(directory + '/Out/' + file_name + '.jpg', image)

    rows = []
    for i in range(len(leaf_contour_viewed)):
        row = []
        row.append(file_name + '__' + str(i))
        row.append(necrosis_number[i])
        row.append(necrosis_areas[i])
        row.append(pycnides_number[i])
        row.append(pycnides_areas[i])
        rows.append(row)
    return rows

def start_analysis(directory, result, save):
    if not os.path.exists(directory + '/JPG'):
        os.mkdir(directory + '/JPG')
    if not os.path.exists(directory + '/Out') and save:
        os.mkdir(directory + '/Out')
    for file in os.listdir(directory):
        if file.endswith(".tif"):
            image = Image.open(directory + '/' + file)
            image.convert("RGB").save(directory + '/JPG/' + file.split('.')[0] + '.jpg', "JPEG", quality=100)

    with open(result, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['leaf', 'necrosis_number', 'necrosis_area', 'pycnidia_number', 'pycnidia_area'])
        for file in os.listdir(directory + '/JPG'):
            rows = get_image_informations(directory, directory + '/JPG/' + file, file.split('.')[0], save)
            writer.writerows(rows)

start_analysis('/Users/maximereder/PycharmProjects/pycnide/images', '/Users/maximereder/PycharmProjects/pycnide/images/result.csv', True)