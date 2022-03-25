import os
import sys
import cv2, csv
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.signal import convolve2d

'''

AUTHOR: Maxime REDER
MAIL: maximereder@live.fr
Web site: https://maximereder.fr/

DO NOT DISTRIBUTE 

'''

def get_image_informations(directory, img, file_name, dpi, save):
    image = cv2.imread(img)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    leaf_area = 0
    necrosis_area = 0
    necrosis_number = 0
    pycnidia_area = 0
    pycnidia_number = 0

    low_leaf = np.array([0, 35, 65])
    high_leaf = np.array([255, 255, 255])
    mask_leaf = cv2.inRange(hsv, low_leaf, high_leaf)
    cnts_leaf, h_leaf = cv2.findContours(mask_leaf, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    for cnt in cnts_leaf:
        area = cv2.contourArea(cnt)
        leaf_area += area

    '''
    
    NECROSIS TREATMENT
    
    '''

    low_yellow_necrosis = np.array([169, 85, 28])
    high_yellow_necrosis = np.array([240, 170, 135])
    mask_yellow_necrosis = cv2.inRange(rgb, low_yellow_necrosis, high_yellow_necrosis)

    low_green_necrosis = np.array([90, 103, 70])
    high_green_necrosis = np.array([141, 141, 115])
    mask_green_necrosis = cv2.inRange(rgb, low_green_necrosis, high_green_necrosis)

    low_soi_necrosis = np.array([111, 93, 35])
    high_soi_necrosis = np.array([176, 142, 103])
    mask_soi_necrosis = cv2.inRange(rgb, low_soi_necrosis, high_soi_necrosis)

    mask_merged = mask_yellow_necrosis + mask_green_necrosis + mask_soi_necrosis
    cnts, h = cv2.findContours(mask_merged, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    cnts_necrosis = []
    for cnt in cnts:
        area = cv2.contourArea(cnt)
        if area > 1000:
            perimeter = cv2.arcLength(cnt, True)
            ratio = round(perimeter / area, 3)
            if ratio < 0.25:
                cnts_necrosis.append(cnt)
                necrosis_number += 1
                necrosis_area += area
                cv2.drawContours(image, cnt, -1, (0, 255, 0), 2)

    '''
    
    CONVOLUTION 
    
    '''

    F = np.array([[1, 0, -1]] * 3)
    conv1 = convolve2d(gray, F)
    conv2 = np.uint8(conv1 > 20) * 255

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 4))
    erode = cv2.erode(conv2, kernel)
    opening = cv2.morphologyEx(erode, cv2.MORPH_OPEN, kernel)

    th, threshed = cv2.threshold(erode - opening, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    cnts_pycnides = cv2.findContours(threshed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]

    grains = [np.int0(cv2.boxPoints(cv2.minAreaRect(cnts_pycnides[i]))) for i in range(1, len(cnts_pycnides), 1)]
    centroids = [(grains[i][2][1] - (grains[i][2][1] - grains[i][0][1]) // 2,
                  grains[i][2][0] - (grains[i][2][0] - grains[i][0][0]) // 2) for i in range(1, len(grains), 1)]
    colors = [image[centroids[i]] for i in range(1, len(centroids), 1)]

    if len(cnts_pycnides) > 0:
        for i in range(0, len(cnts_pycnides)-3, 1):
            current_contour = [int(n) for n in cnts_pycnides[i][0][0]]
            area = cv2.contourArea(cnts_pycnides[i])
            in_necrosis_area = False

            for y in range(len(cnts_necrosis)):
                if cv2.pointPolygonTest(cnts_necrosis[y], current_contour, False) == 1:
                    in_necrosis_area = True

            if in_necrosis_area:
                b = colors[i][0]
                g = colors[i][1]
                r = colors[i][2]
                if r < 190 and g < 160 and b < 130:
                    cv2.drawContours(image, cnts_pycnides[i], -1, (0, 0, 255), 4)
                    pycnidia_area += area
                    pycnidia_number += 1

    if save:
        cv2.imwrite(os.path.join(directory, 'artifacts', 'OUT', file_name) + '.tif', image)

    px_len=(2.54/dpi)**2

    # OLD: 0.00002916
    row = []
    row.append(file_name)
    row.append(leaf_area)
    row.append(round(leaf_area * px_len, 2))
    row.append(necrosis_number)
    row.append(necrosis_area)
    row.append(round(necrosis_area * px_len, 2))
    row.append(pycnidia_number)
    row.append(pycnidia_area)
    row.append(round(pycnidia_area * px_len, 4))

    return row

def crop_image(directory):
    end = len([f for f in os.listdir(os.path.join(directory))
             if f.endswith('.tif') and os.path.isfile(os.path.join(os.path.join(directory), f))])

    pbar = tqdm(total=end, desc="Crop", bar_format="{l_bar}{bar:20}{r_bar}{bar:-10b}")
    for file in os.listdir(os.path.join(directory)):
        if file.endswith('.tif'):
            image = cv2.imread(os.path.join(directory, file))
            if image is not None:
                hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

                min_area = 50000
                leaf_area = 0

                low_green = np.array([0, 35, 65])
                high_green = np.array([255, 255, 255])
                mask_leaf = cv2.inRange(hsv, low_green, high_green)
                cnts_leaf, h_leaf = cv2.findContours(mask_leaf, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

                z = 0
                for contour in cnts_leaf:
                    area = cv2.contourArea(contour)
                    if area > min_area:
                        z+=1

                i = 0
                for contour in cnts_leaf:
                    area = cv2.contourArea(contour)
                    if area > min_area:
                        leaf_area += area
                        i+=1
                        x, y, w, h = cv2.boundingRect(contour)
                        cropped = image[y:y + h, x:x + w]
                        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), 1)
                        cv2.imwrite(os.path.join(directory, 'artifacts', 'CROPPED', file.split('.')[0]) + '__{}.tif'.format(str(i)), cropped)
                pbar.update(1)
            else:
                print("Cannot read properly : ", file)
                pbar.update(1)
    pbar.close()


def create_final_result(directory, reactivip, result):
    react_data = pd.read_csv(reactivip, sep=';', encoding="ISO-8859-1")
    result_data = pd.read_csv(result)

    pbar = tqdm(total=result_data.shape[0], desc="Add lines to csv", bar_format="{l_bar}{bar:20}{r_bar}{bar:-10b}", position=0)
    with open(os.path.join(directory, 'result.csv'), 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = []
        header.append('leaf')
        for e in react_data.head().columns:
            header.append(str(e).strip())
        header = header + ['leaf_area_px', 'leaf_area_cm', 'necrosis_number', 'necrosis_area_px', 'necrosis_area_cm', 'pycnidia_number', 'pycnidia_area_px', 'pycnidia_area_cm']
        writer.writerow(header)

        rows = []
        for r_row in react_data.iterrows():
            for l_row in result_data.iterrows():
                if r_row[1][0].split('__')[0] == l_row[1][0].split('__')[0]:
                    row = []
                    row.append(l_row[1][0])
                    for i in range(0, react_data.columns.size, 1):
                        row.append(r_row[1][i])
                    for i in range(1, 9, 1):
                        row.append(l_row[1][i])
                    rows.append(row)
                    pbar.update(1)

        for i in range(0, len(rows), 1):
            writer.writerow(rows[len(rows)-1-i])
        pbar.close()
        print('\033[92m'+"Done!")


def start_analysis(directory, reactivip, result, dpi, save):
    print("Start Process")
    if not os.path.exists(os.path.join(directory, 'artifacts')):
        os.mkdir(os.path.join(directory, 'artifacts'))
    if not os.path.exists(os.path.join(directory, 'artifacts', 'CROPPED')):
        os.mkdir(os.path.join(directory, 'artifacts', 'CROPPED'))
    if not os.path.exists(os.path.join(directory, 'artifacts', 'OUT')) and save:
        os.mkdir(os.path.join(directory, 'artifacts', 'OUT'))

    crop_image(directory)

    total = len(os.listdir(os.path.join(directory, 'artifacts', 'CROPPED')))
    pbar = tqdm(total=total, desc="Analyze", bar_format="{l_bar}{bar:20}{r_bar}{bar:-10b}", position=0)
    with open(result, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        rows = []
        i=0

        for file in os.listdir(os.path.join(directory, 'artifacts', 'CROPPED')):
            i+=1
            row = get_image_informations(directory, os.path.join(directory, 'artifacts', 'CROPPED', file), file.split('.')[0], dpi, save)
            pbar.update(1)
            rows.append(row)
        pbar.close()

        for i in range(0, len(rows), 1):
            writer.writerow(rows[len(rows)-1-i])
    create_final_result(directory, reactivip, result)

start_analysis('/Users/maximereder/Desktop/problematique/', '/Users/maximereder/Desktop/problematique/LM1_all__input.csv', '/Users/maximereder/Desktop/problematique/result.csv', 1200, True)

#start_analysis(os.getcwd(), os.path.join(os.getcwd(), sys.argv[1]), os.path.join(os.getcwd(), sys.argv[2]), 1200, os.path.join(os.getcwd(),sys.argv[3]))