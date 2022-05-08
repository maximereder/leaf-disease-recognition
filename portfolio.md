# leaf-disease-recognition

This project aims to study **necrosis** and **pycnidia** on a leaf. It is led by a PHD student in **biology**. My goal is to help her in the processing of her images.
Following this analysis, we generate a dataset. This dataset will also be the subject of an in-depth study. This project is therefore the first step of her **thesis**.

![With pycnidias](Report/pycnidias_drawn.webp)

Definitions : 
* **Necrosis** : Death of tissue through injury or disease, especially in a localized area. Such an area is usually *brown* or *black*.

![hand pycnidias](Report/hand_necrosis.webp)

* **Pycnidia** : A pycnidia is a type of **asexual reproductive structure** found in fungi of the order *Sphaeropsidales* (class *Coelomycetes*) and *lichens* whose fungal component belongs to this order. The pycnidia is a spore-like concept of certain imperfect fungi (ascomycetes), usually globose or obpiriform in appearance (in the shape of a bottle or an inverted pear). Inside, very small asexual spores are formed, called *conidia* or *pycnidias*.

![hand pycnidias](Report/hand_pycnidia.webp)

The dataset is composed about **1600 images** and each leaf is composed of **4 portions** of leaves.

Original image : 

![original](Report/Ber_Bob_2_Bob_2.jpg)

Here is how we proceed our analysis : 
- We determine all the leaves on the image which is necessary for our *result.csv* file.
- We analyse all cropped leaves. On each leaf, we detect each *necrosis area*, which are necrotic areas of the leaf. Depending on the leaf, each necrosis may have a different color. To solve this problem, we use different `masks`. (See [Analysis](#Analysis))
- Then, we detect the pycnidias. The areas calculated previously are very useful, because they allow to **check** if a pycnidia is coherent: if a pycnidia belongs to a *necrotic area* then it is a **true pycnidia**. (See [Analysis](#Analysis))
- Finally, we create *result.csv* which is composed : 
    * Columns from csv from PHD (columns containing researcher input data)
    * Name,
    * Leaf area in px and cm,
    * Number of necrosis areas,
    * Total area of necrosis areas in px and cm,
    * Number of pycnidia,
    * Total area of pycnidia areas in px and cm.

## Analysis

Function : `get_image_informations(directory, img, file_name, dpi, save)`

Arguments : 
- `directory`: main directory of analysis.
- `img`: TIF file to analyze.
- `dpi`: Number of pixels created on a one-inch area.
- `save`: save all images (cropped and analysed). `True` or `False`. 

### Necrosis treatment

Library used: [Tensorflow](https://www.tensorflow.org/).

We annotate 300 images to solve this problem. 

![img_vierge](Report/img_vierge.webp)

![img_annotated](Report/img_annotated.webp)


A simple U-Net model is used to recognize necroses on a leaf.

```
Model: "sequential"
_________________________________________________________________
 Layer (type)                Output Shape              Param #   
=================================================================
 conv1 (Conv2D)              (None, 292, 3062, 32)     7808      
                                                                 
 elu (ELU)                   (None, 292, 3062, 32)     0         
                                                                 
 Tconv2 (Conv2DTranspose)    (None, 300, 3070, 1)      2593      
                                                                 
=================================================================
Total params: 10,401
Trainable params: 10,401
Non-trainable params: 0
_________________________________________________________________

```

The model will predict 'mask' that represent necrosis : 

![img_vierge](Report/leaf_in.webp)

After predicting the mask, we apply these rules :
```py
for cnt in cnts_necrosis_full:
  area = cv2.contourArea(cnt)
  if area > 300:
    perimeter = cv2.arcLength(cnt, True)
    ratio = round(perimeter / area, 3)
    if ratio < 0.9:
      cv2.drawContours(image, cnt, -1, (0, 255, 0), 2)
      necrosis_area += area
      necrosis_number+=1
```

![img_vierge](Report/leaf_out.webp)

### Pycnidias 

Library used: [SciPy](https://scipy.org/).

One of our problematic is to detect leaf pycnidias which are technically small black dots. However, colors of *small black spores* are differents according to leaf background. We can't solve this just by color. 

The common point between these spors is the **shape**. They can be assimilated to *small circles*.

That's why, we use **convolution kernel**.

![Convolution](Report/convolution.gif)

Example : 

![Without pycnidias](Report/without_pycnidias_drawn.webp)

After detecting the suspected pycnidia, we sort them according to some rules : 
```py
for pycnidias in leaf:
  if pycnidia is in necresis area: 
    if pycnidia color belong to authorized colors:
      # drawing pycnidia
      pycnidia_area += area
      pycnidia_number += 1
```

![With pycnidias](Report/pycnidias_drawn.webp)