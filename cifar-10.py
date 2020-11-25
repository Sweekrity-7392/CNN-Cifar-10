import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
np.random.seed(2)

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import itertools

from keras.utils.np_utils import to_categorical # convert to one-hot-encoding
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D
from keras.optimizers import RMSprop
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ReduceLROnPlateau

sns.set(style='white', context='notebook', palette='deep')

#Load data
from keras.datasets import cifar10
(X_train, Y_train), (X_test, Y_test) = cifar10.load_data()

#extract and plot data
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
fig = plt.figure(figsize=(8,3))
for i in range(len(class_names)):
    ax = fig.add_subplot(2, 5, 1 + i, xticks=[])
    idx = np.where(Y_train[:]==i)[0]
    features_idx = X_train[idx,::]
    img_num = np.random.randint(features_idx.shape[0])
    im = features_idx[img_num,::]
    ax.set_title(class_names[i])
    # im = np.transpose(features_idx[img_num,::], (1, 2, 0))
    plt.imshow(im)
plt.show()

#plot labels to check if dataset is homogenous or biased
sns.displot(Y_train)
plt.show()

# normalization
X_train = X_train/30.0
X_test = X_test/30.0

#encode labels to one hot vectors (ex : 2 -> [0,0,1,0,0,0,0,0,0,0])
Y_train = to_categorical(Y_train, num_classes=10)

#split data into train and validation
random_seed = 2
X_train, X_val, Y_train, Y_val = train_test_split(X_train, Y_train, test_size = 0.2, random_state = random_seed)

#plot an example
# g = plt.imshow(X_train[30500][:,:,:])
# plt.show()

## CNN model
# Set the CNN model
# my CNN architechture is In -> [[Conv2D->relu]*2 -> MaxPool2D -> Dropout]*2 -> Flatten -> Dense -> Dropout -> Out
#model = 1
model = Sequential()
model.add(Conv2D(filters = 32, kernel_size = (5,5),padding = 'Same', activation ='relu', input_shape = (32, 32, 3)))
model.add(Conv2D(filters = 32, kernel_size = (5,5),padding = 'Same', activation ='relu'))
# model.add(MaxPool2D(pool_size=(2,2)))
model.add(Dropout(0.25))
# model.add(Conv2D(filters = 64, kernel_size = (5,5),padding = 'Same', activation ='relu'))
model.add(Conv2D(filters = 64, kernel_size = (3,3),padding = 'Same', activation ='relu'))
model.add(Conv2D(filters = 64, kernel_size = (3,3),padding = 'Same', activation ='relu'))
# model.add(MaxPool2D(pool_size=(2,2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(256, activation = "relu"))
model.add(Dropout(0.5))
model.add(Dense(10, activation = "softmax"))

#model = 2
model1 = Sequential()
model1.add(Conv2D(filters = 32, kernel_size = (3,3),padding = 'Same', activation ='relu', input_shape = (32, 32, 3)))
model1.add(Conv2D(filters = 32, kernel_size = (3,3),padding = 'Same', activation ='relu'))
model1.add(MaxPool2D(pool_size=(2,2)))
model1.add(Dropout(0.25))
model1.add(Conv2D(filters = 64, kernel_size = (3,3),padding = 'Same', activation ='relu'))
model1.add(Conv2D(filters = 64, kernel_size = (3,3),padding = 'Same', activation ='relu'))
model1.add(MaxPool2D(pool_size=(2,2)))
model1.add(Dropout(0.25))
model1.add(Flatten())
model1.add(Dense(512, activation = "relu"))
model1.add(Dropout(0.5))
model1.add(Dense(10, activation = "softmax"))

#optimizer and annealer
# Define the optimizer
optimizer = RMSprop(lr=0.0001, rho=0.9, epsilon=1e-08, decay=0.0)

#compile the model
model.compile(optimizer = optimizer, loss = "categorical_crossentropy", metrics=["accuracy"])
model1.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"])

# Set a learning rate annealer - to modulate LR
learning_rate_reduction = ReduceLROnPlateau(monitor='val_acc', patience=3, verbose=1, factor=0.5, min_lr=0.00001)

epochs = 100
batch_size = 90

epochs1 = 100
batch_size1 = 32

#data augmentation
# Without data augmentation i obtained an accuracy of 0.98114
# history = model.fit(X_train, Y_train, batch_size = batch_size, epochs = epochs, validation_data = (X_val, Y_val),
#                     verbose = 2),

# With data augmentation to prevent overfitting (accuracy 0.99286)
datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=10,  # randomly rotate images in the range (degrees, 0 to 180)
        zoom_range = 0.1, # Randomly zoom image
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=False,  # randomly flip images
        vertical_flip=False)  # randomly flip images
datagen.fit(X_train)

history = model.fit_generator(datagen.flow(X_train, Y_train, batch_size=batch_size), epochs = epochs,
                              validation_data = (X_val, Y_val), verbose = 2,
                              steps_per_epoch=X_train.shape[0] // batch_size, callbacks=[learning_rate_reduction])
history1 = model1.fit_generator(datagen.flow(X_train, Y_train, batch_size=batch_size1), epochs = epochs1,
                              validation_data = (X_val, Y_val), verbose = 2,
                              steps_per_epoch=X_train.shape[0] // batch_size1, callbacks=[learning_rate_reduction])

# Plot the loss and accuracy curves for training and validation
fig, ax = plt.subplots(2, 1)
ax[0].plot(history.history['loss'], color='b', label="Training loss-model1")
ax[0].plot(history1.history['loss'], color='o', label="Training loss-model2")
ax[0].plot(history.history['val_loss'], color='r', label="validation loss-model1",axes =ax[0])
ax[0].plot(history1.history['val_loss'], color='g', label="validation loss-model2",axes =ax[0])
legend = ax[0].legend(loc='best', shadow=True)

ax[1].plot(history.history['accuracy'], color='b', label="Training accuracy-model1")
ax[1].plot(history1.history['accuracy'], color='o', label="Training accuracy-model2")
ax[1].plot(history.history['val_accuracy'], color='r',label="Validation accuracy-model1")
ax[1].plot(history1.history['val_accuracy'], color='g',label="Validation accuracy-model2")
legend = ax[1].legend(loc='best', shadow=True)
plt.show()

# # Look at confusion matrix
# def plot_confusion_matrix(cm, classes,
#                           normalize=True,
#                           title='Confusion matrix',
#                           cmap=plt.cm.Blues):
#     """
#     This function prints and plots the confusion matrix.
#     Normalization can be applied by setting `normalize=True`.
#     """
#     plt.imshow(cm, interpolation='nearest', cmap=cmap)
#     plt.title(title)
#     plt.colorbar()
#     tick_marks = np.arange(len(classes))
#     plt.xticks(tick_marks, classes, rotation=45)
#     plt.yticks(tick_marks, classes)
#
#     if normalize:
#         cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
#
#     thresh = cm.max() / 2.
#     for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
#         plt.text(j, i, cm[i, j],
#                  horizontalalignment="center",
#                  color="white" if cm[i, j] > thresh else "black")
#
#     plt.tight_layout()
#     plt.ylabel('True label')
#     plt.xlabel('Predicted label')
#
# # Predict the values from the validation dataset
# Y_pred = model.predict(X_val)
# # Convert predictions classes to one hot vectors
# Y_pred_classes = np.argmax(Y_pred,axis = 1)
# # Convert validation observations to one hot vectors
# Y_true = np.argmax(Y_val, axis = 1)
# # compute the confusion matrix
# confusion_mtx = confusion_matrix(Y_true, Y_pred_classes)
# # plot the confusion matrix
# plot_confusion_matrix(confusion_mtx, class_names)
# plt.show()
#
# # Display some error results
#
# # Errors are difference between predicted labels and true labels
# errors = (Y_pred_classes - Y_true != 0)
#
# Y_pred_classes_errors = Y_pred_classes[errors]
# Y_pred_errors = Y_pred[errors]
# Y_true_errors = Y_true[errors]
# X_val_errors = X_val[errors]
#
# def display_errors(errors_index,img_errors,pred_errors, obs_errors):
#     """ This function shows 6 images with their predicted and real labels"""
#     n = 0
#     nrows = 2
#     ncols = 3
#     fig, ax = plt.subplots(nrows,ncols,sharex=True,sharey=True)
#     for row in range(nrows):
#         for col in range(ncols):
#             error = errors_index[n]
#             ax[row,col].imshow((img_errors[error]).reshape((28,28)))
#             ax[row,col].set_title("Predicted label :{}\nTrue label :{}".format(pred_errors[error],obs_errors[error]))
#             n += 1
#
# # Probabilities of the wrong predicted numbers
# Y_pred_errors_prob = np.max(Y_pred_errors,axis = 1)
#
# # Predicted probabilities of the true values in the error set
# true_prob_errors = np.diagonal(np.take(Y_pred_errors, Y_true_errors, axis=1))
#
# # Difference between the probability of the predicted label and the true label
# delta_pred_true_errors = Y_pred_errors_prob - true_prob_errors
#
# # Sorted list of the delta prob errors
# sorted_dela_errors = np.argsort(delta_pred_true_errors)
#
# # Top 6 errors
# most_important_errors = sorted_dela_errors[-6:]
#
# # Show the top 6 errors
# display_errors(most_important_errors, X_val_errors, Y_pred_classes_errors, Y_true_errors)
# plt.show()
#
# # predict results
# results = model.predict(test)
#
# # select the indix with the maximum probability
# results = np.argmax(results,axis = 1)
#
# results = pd.Series(results,name="Label")