
# leaf-disease-recognition

This project aims to study **necrosis** and **pycnidia** on a leaf. It is led by a PHD student in **biology**. My goal is to help him in the processing of his images.
Following this analysis, we generate a dataset. This dataset will also be the subject of an in-depth study. This project is therefore the first step of his **thesis**.

Definitions : 
* Necrosis : Death of tissue through injury or disease, especially in a localized area. Such an area is usually brown or black.
* pycnidia : A pycnidia is a type of asexual reproductive structure found in fungi of the order Sphaeropsidales (class Coelomycetes) and lichens whose fungal component belongs to this order. The pycnidia is a spore-like concept of certain imperfect fungi (ascomycetes), usually globose or obpiriform in appearance (in the shape of a bottle or an inverted pear). Inside, very small asexual spores are formed, called conidia or picnospores.

The PHD student sends me the images to be analyzed in TIF form. Currently I use for my algorithm a dataset of **193 scans**. The dataset will be composed of about 800 images each composed of 4 portions of leaves.

Original image : 

Image

At the moment of this analysis, I am using OpenCV in order to detect all areas. 

Here are the main stages of image analysis : 
1. Convert image to HSV format.
2. Detect leaf contours : 
  * range  : [0, 35, 65] to [255, 255, 255].
  *  area > 50000px
4. Detect safe area : 
  * range : [40, 60, 30] to [170, 255, 255].
  * area > 1000px
6. Detect necrosis area : 
  * range : [10, 100, 100] to [18, 255, 255].
  * area > 300px
8. Detect pycnidias : 
  * range : [0, 0, 0] to [72, 99, 139].
  * area < 100px
