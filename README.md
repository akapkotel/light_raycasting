# Visibility/light raycasting algorithm

Visibility/light-raycasting algorithm python implementation inspired by: https://www.redblobgames.com/articles/visibility/

It is a simple window-mode presentation of algorithm. It opens arcade window to draw some poligons (obstacles for light or 
visibility) and user can move position of "light" source.

It could be easily changed into the FOV script, by diminishing value of arc_angle attribute in the Light class (curently it
is 360 degrees to simulate point-source of light, eg. lightbulb hanging from the ceiling).

Installation, running and use instructions:

1. Download or clone this repository.
2. Setup new virtual environment with Python 3.6.
3. Install requirements with pip install -r requirements.txt
4. Run main.py in any IDE, e.g. PyCharm, or in Terminal.
5. In main.py in section "#debug variables" you can change value of TIMER boolean to False if you want disable measuring execution time (default is True), and SHOW_RAYS to True if you want see how many raycasts are drawn each frame (default is False).
6. Size and shape of obstacles could be modified by changing OBSTACLE_EDGES variable value: 3 makes triangles, 4 squares, 5 pentagons etc. Variable OBSTACLE_EDGE_SIZE controlls not only size of obstacles, but also distances between them.

For exampole. if you set edges to 3, and size to 150 you will get 4 triangles:
![Triangles](https://github.com/akapkotel/light_raycasting/blob/master/visibility_algorithm_demo_3.png)

Setting edges to 6 and size to 50 would produce:
![Hexagons](https://github.com/akapkotel/light_raycasting/blob/master/visibility_algorithm_demo_2.png)

7. You can change LIGHTS_COUNT variable to add additional sources of light/FOV shadows effect (although I did not implement alpha transparency so rathar than shadows, you have sharp color-change). Beware of lights number, since it is computation-heavy.
8. You can randomize colors of each light to better see that there are many, distinct FOV polygons drawn. Set RANDOM_COLORS to True to get random colors, otherwise a visibility/light polygon would by rgb(192, 192, 192).

With random lights colors and 8 lights:
![Random colors](https://github.com/akapkotel/light_raycasting/blob/master/random_colors_2.png)

It requires more optimizations:

1. For now it works only for static obstacles - positions of polygons vertices are calculated once at the start. Dynamic   updates of obsatcles-corners would cost a lot of computing power which is already entirely consumed by raycasting.
2. It requires the enclosed FOV (it must treat screen edges as outermost 'walls' encapsulating the scene)
3. It does not scale-up: with 9 squared-obstacles on the screen it calculates all raycasts for 1 origin in 0.0029 to 0.0105 second, which gives 95-345 FPS. With more obstacles and lights, framerate falls quickly. But I made some progress, by getting rid of shapely library calls with simplier math calculations.
4. To change it to FOV-simulation, you need to add half-arcs of visible space which would connect raycasts andings. For now,
   visibility-polygon is cut straightly. Unless your visibility range is larger than screen size, you will get glitches.
5. Maybe some work could be done with multithreading or multiprocessing, but I did not work it out yet.
6. Unfortunatelly, my algorithm suffers for the same problems which Amit Patel from Red Blob Games blog reports: robustness      problems which causes generation of some invalid, falsely-dark triangles. I was only able to get rid of small part of        them. I suppose, there is no easy way to fix this, and I can only send you to the same source about this problem, that   Amit reccomends: https://github.com/mikolalysenko/robust-arithmetic-notes
7. Maybe I shgould use another algorithm - triangle-expanding algorithm described in the PDF file added to this repository.

To be done:

1. Optimizations listed above.
2. Add option to move position of obstacles when app is running.
3. Replacing single-colored "lit" polygon with gradient to simulate diminishing power of light. It could force me to replace arcade library with something else, since arcade does not allow draw gradient-polygons in real-time.
4. Adding this project to my Django blog (when it is also finished).

If anyone has ideas how to make this algorithm better (faster), please, notice me, fork and make pull-requests.

Changelog:

1. Added FPS-counter drawn on the screen for user convenience.
2. Added option to randmize light/visibility polygons colors.

----

Rafał "Akapkotel" Trąbski

