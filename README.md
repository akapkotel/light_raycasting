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

1. For now it works only for static obstacles - positions of polygons vertices are calculated once at the start. Dynamic   updates of obsatcles-corners would cost a lot of computing power which is already entirely consumed by raycasting.
2. It requires the enclosed FOV (it must treat screen edges as outermost 'walls' encapsulating the scene)
3. It does not scale-up: with 9 squared-obstacles on the screen it calculates all raycasts in between 0.0085s to 0.04s, 
   which means that in the worst scenario the simulation is restricted to not more that 20 FPS! I have to find way to 
   avoid calculating less rays in some scenarios (e.g. when light-source is placed at the bottom of the screen).
   I do not know how to replace shapely intersect() method with something faster, also I use arcade package for drawing, 
   maybe here is some space for optimization - a faster draw function.
4. To change it to FOV-simulation, you need to add half-arcs of visible space which would connect raycasts andings. For now,
   visibility-polygon is cut straightly.
5. Maybe some work could be done with multithreading or multiprocessing, but I did not work it out yet.
6. Unfortunatelly, my algorithm suffers for the same problems which Amit Patel from Red Blob Games blog reports: robustness      problems which causes generation of some invalid, falsely-dark triangles. I was only able to get rid of small part of        them. I suppose, there is no easy way to fix this, and I can only send you to the same source about this problem, that   Amit reccomends: https://github.com/mikolalysenko/robust-arithmetic-notes
7. Maybe I shgould use another algorithm - triangle-expanding algorithm described in the PDF file added to this repository.

To be done:

1. Optimizations listed above.
2. Customization: changing amount and positioning of obstacles.
3. Replacing single-colored "lit" polygon with gradient to simulate diminishing power of light. It could force me to replace arcade library with something else, since arcade does not allow draw gradient-polygons in real-time.
4. Adding this project to my Django blog (when it is also finished).

If anyone has ideas how to make this algorithm better (faster), please, notice me, fork and make pull-requests.

----

Rafał "Akapkotel" Trąbski
