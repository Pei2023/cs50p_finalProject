# Write Stories with Pillow
### ***Video Demo:***
1. How to execute the program: https://youtu.be/1H264J1rJT0?si=SFr60hnnw8h7CNSS
## Description:

&nbsp;&nbsp;&nbsp;&nbsp;The goal of this project is to generate a little story by merging the four uploaded images and the text description for each image. The procedure includes:
1. Specify four images file while executing the python file.
2. Get the minimum width and minimum height among the four images, and set them as the unified width and the unified height.
3. Set the font size. To make sure the ratio of the image size and the font size is sustained, the ratio of imagesize^2 / fontsize^2 is 593.4.
4. Prompt user to input description text for each image (the word number is examined here).
5. Prompr user to input the name of new created image (only alphabet, number and underscore are allowed).
6. Create description region with transparent black objects, and add the input texts from step 4 on each description object.
7. Unifiy inage size: crop the images into the unified size beased on the min width and the min height from step 2.
8. Combine photo and description region for each image.
9. Connect four image objects, consisting of description region and photo.
10. Save the new image as .jpg file.


<img src="docs\\flow.jpg" alt="drawing" align=1200/>
The flow to make a little story:
(1) User specify four images when executing the program. (2) Get the minimum width and minimum height among the four images, and set it as the unified width and the unified height. The size of the description area is also unified here: the width is the same as the unified width of photos and the height is one fifth of the unified height of photos. (3) The photos are cropped to the unified width and unified height, and the description region is generated with a transparent black image objct and the texts that user inputted. (4) Combine the photo and description region for each image object. (5)Connect all the image objects together to generate a new image.


### ***Make sure the font size propotional to the image size***
To make sure the font size won't be too small when the size of the uploaded image is too large, we need to set the size of font and the size of image in propotion. The ration between image area and font area is set 593.4. \
Calculate the font size: $\sqrt{(unifiedImageWidth * unifiedImageHeight) / 593.4}$


### ***Documentation***
1. [Check the ***functions*** inside this module](docs/_build/html/project.html)
2. [Check ***unit test*** inside this module](docs/_build/html/test_project.html)


