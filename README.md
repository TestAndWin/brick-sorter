# brick-sorter
Machine to sort bricks using machine learning. A Raspiberry PI is used to control the individual motors and to take the images. The images are then sent to another computer, which uses the ML model to make a prediction of what type of brick it is. The sorter is operated via an HTML interface.

More details and a video of the brick sorter can be found [here](https://testandwin.net/software-development/brick-sorter/).

# Flow
- Place bricks in the feeder by the conveyor belt.
- Belt moves bricks to a vibrating plate.
- Vibrating plate tries to get the bricks into a sequence
- To get only one brick on the plate, a Gate opens for a very short time and then closes it again the gate (in a loop).
- If a brick is detected on the tilt plate, a image is taken and the belt, plate and gate are stopped.
- Brick image is sent to a server.
- Server uses the learned model and tries to determine the brick type and returns the type. The server stores also the image in the images directory.
- Depending on the brick type the hub is moved to the corresponding slot.
- Tilt plate is tilted briefly so that the bricks slides on the hub and then into a slot.
- Belt, plate and gate are started again.

# Model
The model is based on VGG16 with an own top layer.

## Data
The images to calculate the model have been taken with the brick sorter. They are stored in the data directory, all images of one type in a separate directory, e.g. 1x1 or 2x4. 

## Creating a model
To calculate a new model as h5 file run the following command in the ```model``` directory

> ```python3 model.py -reread```

# Running Brick Sorter
## Predict Server
In the ```model``` directory call

> ```python3 predict_server.py```

## Sorter
In the ```sorter``` directory call

> ```python3 sorter_server.py```

The address of the predict server must be configured in ```sorter_server.py```.

## HTML Interface
HTML Overview page on ```<sorter server>:5000``` to start transpart and detection. It shows also the latest image with the prediction.
