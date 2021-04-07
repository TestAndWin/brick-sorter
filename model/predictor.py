import numpy as np
from PIL import Image
from keras.applications.vgg16 import preprocess_input, VGG16
from keras.models import load_model
import cv2
import time

class Predictor:
    def __init__(self):
        self.mapping = np.load("mapping.npy")
        self.vgg16_model = VGG16(include_top=False, input_shape=(224, 224, 3))
        self.model = load_model("bricks_01.h5")


    def predict(self, image):
        print("Predict")
        start_time = time.time()
        # Resize expects float as type
        image = image.reshape(image.shape).astype('float32')
        if image.shape[0] != 224:
            image = cv2.resize(image, dsize=(224, 224), interpolation=cv2.INTER_LANCZOS4)
        image = image.reshape(1, 224, 224, 3)
        image = preprocess_input(image)
        # interim result in shape (1,7,7,512) which is expected from our modell
        X_after_vgg = self.vgg16_model.predict(image)
        predicts = self.model.predict(X_after_vgg)

        print(">>> %s <<<" % (self.mapping[np.argmax(predicts)]))
        i = 0
        distr = ""
        for p in predicts[0]:
            s = "%s - %f" % (self.mapping[i], p*100)
            print(s)
            distr = distr + "<br>" + s
            i += 1

        print("--- %s seconds ---" % (time.time() - start_time))
        return {"index": str(np.argmax(predicts)), "name": self.mapping[np.argmax(predicts)], "distribution": distr }


def main():
    p = Predictor()
    image = cv2.imread("../data/1x3/image_1617376347184.jpg")
    print(image.shape)
    print(p.predict(image))


if __name__ == "__main__":
    main()
