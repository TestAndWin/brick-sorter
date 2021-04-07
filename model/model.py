import os
import numpy as np
import sys
from PIL import Image
from sklearn.utils import shuffle
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.models import Sequential
from keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout
from keras.utils import to_categorical
from keras.optimizers import Adam, Adagrad, Adadelta
from keras.callbacks import EarlyStopping


# Read all images from the directory and returns an array with each image as Numpy array
def read_images(path):
    print("Read", path)
    files = os.listdir(path)
    files = [file for file in files if file[-4:] == ".jpg"]

    images = []
    for file in files:
        try:
            image = Image.open(os.path.join(path, file))
            image = image.resize((224, 224), Image.LANCZOS)
            image = image.convert("RGB")
            image = np.asarray(image)
            images.append(image)
        except OSError:
            pass
    return images


# Build X and y
# Iterate over each directory and read the images
def get_X_and_y(directory="../data"):
    dirs = os.listdir(directory)
    dirs.sort()
    X = np.empty(shape=(0, 224, 224, 3))
    y = np.empty(shape=0)
    i = 0
    y_mapping = []
    for d in dirs:
        imgs = np.asarray(read_images(os.path.join(directory, d)))
        X = np.concatenate([X, imgs])
        y = np.concatenate([y, np.full(len(imgs), i)])
        y_mapping.append(d)
        i += 1

    # One-Hot-Encoding
    # Convert to binary class metrix, e.g. for 3 entries 1:0:0 0:1:0 0:0:1
    y = to_categorical(y)
    np.save("y.npy", y)
    np.save("mapping.npy", y_mapping)
    print("y shape", y.shape)
    return X, y


# Use VGG16 model but without the top layer, because we add our own
# and predict X data using this model. Returns the predicted X data.
def run_vgg(X):
    vgg16_model = VGG16(include_top=False, input_shape=(224, 224, 3))
    vgg16_model.trainable = False

    # Adapt to numver range witch has been used to train the VGG16 model
    X = preprocess_input(X)

    # Calculate the VGG16 model, improves performance when own model is used
    print("VGG Predict")
    X_after_vgg = vgg16_model.predict(X, verbose=1)

    np.save("X_after_vgg.npy", X_after_vgg)
    print("X Shape", X_after_vgg.shape)
    return X_after_vgg


# Create own model and compile it.
# classes = number of different bricks, coming from y
def configure_model(classes):
    model = Sequential()
    # Last step in VGG model has output shape 7,7,512
    model.add(Flatten(input_shape=(7, 7, 512)))
    model.add(Dense(256, activation="relu"))
    model.add(Dropout(0.2))
    model.add(Dense(classes, activation="softmax"))

    # acc 1.0 - val_acc 0.8229
    #model.compile(optimizer=Adadelta(lr=0.01, rho=0.95, epsilon=None, decay=0.0), loss="categorical_crossentropy", metrics=["acc"])

    # acc 1.0 - val_acc 0.8333
    model.compile(optimizer=Adadelta(lr=0.1, rho=0.95, epsilon=None, decay=0.0), loss="categorical_crossentropy", metrics=["acc"])

    # acc 1.0 - val_acc 0.802
    #model.compile(optimizer=Adadelta(lr=1, rho=0.95, epsilon=None, decay=0.0), loss="categorical_crossentropy", metrics=["acc"])

    # acc 1.0 - val_acc 0.77
    #model.compile(optimizer=Adadelta(lr=0.2, rho=0.95, epsilon=None, decay=0.0), loss="categorical_crossentropy", metrics=["acc"])

    print(model.summary())
    return model


# Train and save the model
def train_and_save_model(model, X_after_vgg, y):
    # Shuffle data, so that the images are not ordered anymore
    X_after_vgg, y = shuffle(X_after_vgg, y)
    #es_callback = EarlyStopping(monitor='val_loss', patience=5)
    model.fit(X_after_vgg, y, epochs=30, batch_size=8, validation_split=0.2, shuffle=True, callbacks=[])
    model.save("bricks_01.h5")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-reread':
        print("Read images from disk")
        X, y = get_X_and_y()
        X_after_vgg = run_vgg(X)
    else:
        print('Use stored X and y data')
        y = np.load("y.npy")
        X_after_vgg = np.load("X_after_vgg.npy")

    # y[1] the number of different bricks
    model = configure_model(y.shape[1])
    train_and_save_model(model, X_after_vgg, y)


if __name__ == "__main__":
    main()

