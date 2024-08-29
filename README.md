## Sayid's Summer of Code 2024 (SSoC 2024)

A project-based initiative to learn C, re-learn Git, software development in automotive engineering, and upskilling in general.

I plan to build my own "simulation" system using Python for the user interface, simulation controller, and dynamics model. A program written in C then serves as
the "controller" of the dynamics. Since this project is quite close to my domain expertise, I am comfortable and excited with the problem so that I can prioritize
the C, Python, and software development aspect more. 

The main idea is to develop a C-based controller that roughly imitates how a controller works in a real vehicle.
The dynamics are governed by a separate Python-based script (well because I am much more familiar with Python so debugging the dynamics part will be much easier).
Then a simulation controller with Python will handle the "tick-tock" of the simulation time and the UDP communication between the dynamics and the controller. A separate Python-based script will
serve as the user interface that receives real-time input from the user.


### Usage
Compile the udpserver.c and run main.py. I haven't done any "streamlining" on this part yet and only tested on Linux.

### Architecture #1
The initial plan of the architecture is as follow:
![architecture_1](https://github.com/saachdm/cpsil/assets/20472912/8bbfb99a-9004-4646-ac2d-73cc85113730)

On the C-side, sensor readings and input to the dynamic system will use a "publisher-subscriber" method towards the C server. The user in the C-side then can focus on processing the "subscribed" values and "publishing" the processed values without worrying about the "backend" side of the C. The entire C loop will run everytime the C server receives a message from the Python server.

### Update 25-06-2024
The minimum viable product is ready and it should be able to "capture" the important features. The plotter is still a simple matplotlib update mechanism, models are still limited to longitudinal, and lots of things to explore on the C side. Next development will focus on a more robust and modular model, adding driveline model, as well as implementing a rudimentary "bicycle" model for lateral motion.

### Update 29-08-2024
![Screenshot from 2024-08-29 16-28-47](https://github.com/user-attachments/assets/fabffe32-7525-42c3-8b31-cf0d2dfdd21a)

It's been a while. The dynamic model now include front-rear wheel model for load transfer consideration, gearbox, road inclination, rev limit, and fuel consumption estimate based on a rudimentary engine map from a coursework I did. A very simple speed-based automatic gear control is also implemented on the C-side. The lateral model is still on hold because I am still having "fun" with the longitudinal model :). The GUI is now nicer with dearpygui. However, there is a massive performance issue and this will be my main objective now. Lateral model will be published along with a live "2D" map GUI and support for live user input. The dynamic model is still very-very "simple" and not deep/detailed enough. The resources needed to improve the model is quite big while the gain is not that much for this purpose. That's the reason why the model development seemed to expand "laterally".
