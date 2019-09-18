# light_raycasting

Visibility/light-raycasting algorithm python implementation inspired by: https://www.redblobgames.com/articles/visibility/

It is a simple window-mode presentation of algorithm. It opens arcade window to draw some poligons (obstacles for light or 
visibility) and user can move position of "light" source.

It could be easily changed into the FOV script, by diminishing value of arc_angle attribute in the Light class (curently it
is 360 degrees to simulate point-source of light, eg. lightbulb hanging from the ceiling).

Installation and running:

1. Download or clone this repository.
2. Setup new virtual environment with Python 3.6.
3. Install requirements with pip install -r requirements.txt
4. Run main.py in any IDE, e.g. PyCharm, or in Terminal.

It requires more optimizations:

1. For now it works only for static obstacles
2. It requires the enclosed FOV (it must treat screen edges as outermost 'walls' encapsulating the scene)
3. It does not scale-up: with 9 squared-obstacles on the screen it calculates all raycasts in between 0.0085s to 0.04s, 
   which means that in the worst scenario the simulation is restricted to not more that 20 FPS! I have to find way to 
   avoid calculating less rays in some scenarios (e.g. when light-source is placed at the bottom of the screen).
   I do not know how to replace shapely intersect() method with something faster, also I use arcade package for drawing, 
   maybe here is some space for optimization.
4. To change it to FOV-simulation, you need to add half-arcs of visible space which would connect raycasts andings. For now,
   visibility-polygon is cut straightly.
5. Maybe some work could be done with multithreading or multiprocessing, but I did not work it out yet.
6. Unfortunatelly, my algorithm suffers for the same problems which Amit Patel from Red Blob Games blog reports: robustness      problems which causes generation of some invalid, falsely-dark triangles. I was only able to get rid of small part of        them. I suppose, there is no easy way to fix this, and I can only send you to the same source treating about this problem,    that Amit reccomends: https://github.com/mikolalysenko/robust-arithmetic-notes

To be done:

1. Optimizations listed above.
2. Customization: changing amount and positioning of obstacles.

If anyone has ideas how to make this algorithm better (fasetr), please, notice me, fork and make pull-requests.

----

Rafał "Akapkotel" Trąbski
