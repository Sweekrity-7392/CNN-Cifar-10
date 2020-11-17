# CNN-Cifar-10

## Files and folder
-------------------

### plots
This folder contains all the obtained plots

### .gitignore
contains extensions to be ignored
   
### cifar-10.py
This is python script that:
* loads the cifar-10 data set, 50000 images
* splits data into training and test - 40,000 images are randomly chosen as training set and 10,000 images as
   test set
* defines model to be applied to classify images into one of the categories as follows: airplanes, cars, birds, 
   cats, deer, dogs, frogs, horses, ships, and trucks
* applied model to the augmented dataset and computes the loss and accuracy of training, validation and test sets. Also 
   returns confusion matrix. 
   
## Model used
-------------
Convolutional neural networks(CNN) is used to classify images into 10 different categories. 
The model is explained in detail in the following diagram:
![CNN model](https://user-images.githubusercontent.com/55786474/99361220-dca8db00-28d9-11eb-94ae-813e13e344e9.png)

## Results
----------
60% accuracy obtained by running batch of 90 for 100 epochs. Confusion matrix and plot for accuracy and loss are saved in the folder, Plots. 
