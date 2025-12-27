from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

fovY = 90

window_width, window_height = 1000, 800

# camera variables

camera_position = (0, 4000, 150)

fpp_mode = False

# game stats
life_remaining = 5
game_score = 0      # per obstacle = 5 points 
bullet_count = 0
nitro_count = 0
game_speed = 10
last_time = time.time()


# graphics related variables
isDay = True

road_width = 400
road_length = 4500

element_offset = 0

tree_offset = 0

# car stats
car_x, car_y, car_z = 0, 3700, 16
car_rotation = 0

# ramp variables
ramp_positions = {}

# ramp_positions = {
#     id1 :(x, y, z),
#     id2 :(x, y, z),
# }

ramp_spawn_delay = 15
last_ramp_time = time.time()


ramp_length = 200
ramp_width = 200
ramp_angle = -45

def specialKeyboardListener(key, x, y):
    global camera_position
    cam_x, cam_y, cam_z = camera_position
    step = 10

    if key == GLUT_KEY_LEFT:
        cam_x = min(cam_x + step, 200)
        camera_position = (cam_x, cam_y, cam_z)
    
    
    if key == GLUT_KEY_RIGHT:
        cam_x = max(cam_x - step, -200)
        camera_position = (cam_x, cam_y, cam_z)
    
    if key == GLUT_KEY_UP:
        cam_z = min(cam_z + step, 300)
        cam_y = min(cam_y + 5, 4075)
        camera_position = (cam_x, cam_y, cam_z)

    if key == GLUT_KEY_DOWN:
        cam_z = max(cam_z - step, 50)
        cam_y = max(cam_y - 5, 4000)
        camera_position = (cam_x, cam_y, cam_z)

def mouseListener():
    pass

def keyboardListener(key, x, y):
    global sky_color, road_width, isDay, car_x, car_y, car_z, ramp_positions
    
    if key == b'n' or key == b'N': #day and night shifter
        isDay = not isDay

    if key == b'a' or key == b'A':
        car_x = min(car_x+10, road_width-50)

    if key == b'd' or key == b'D':
        car_x = max(car_x-10, -road_width+50)

    if key == b'x' or key == b'X':
        print(ramp_positions)
    
def setupCamera():
    global camera_position, window_width, window_height, fpp_mode

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(fovY, window_width / window_height, 0.1, 6000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if fpp_mode:
        pass
    else:
        cam_x, cam_y, cam_z = camera_position

        gluLookAt(cam_x,cam_y,cam_z,
                  0, 0, 0,
                  0, 0, 1)

def draw_sky():
    if isDay:
        glClearColor(0.5, 0.8, 0.9, 1.0)
    else:
        glClearColor(0.1, 0.1, 0.15, 1.0)

def draw_trees(tree_x):
    global road_width, road_length, element_offset

    # trees in left border
    gap = 500
    x = tree_x
    common_tree_y_term = road_length - gap - element_offset
    z = 2
    
    while common_tree_y_term > -road_length:
        if -road_length < common_tree_y_term < road_length:
            glPushMatrix()

            glTranslatef(x, common_tree_y_term, z)

            # Trunk
            trunk_height = 40
            glColor3f(0.55, 0.27, 0.07)  # brown
            quad = gluNewQuadric()
            gluCylinder(quad, 12, 8, trunk_height, 32, 32)  # quadric, baseRadius, topRadius, height, slices, stacks

            glTranslatef(0, 0, trunk_height)

            # Tree cones
            glColor3f(0, 0.3, 0)  
            for i in range(3):
                if i == 2: #top cone 
                    gluCylinder(quad, 25, 0, trunk_height/1.2, 32, 32)  # cone
                    glTranslatef(0, 0, trunk_height/2)
                else:
                    gluCylinder(quad, 25, 5, trunk_height, 32, 32)  # cone
                    glTranslatef(0, 0, trunk_height/2)

            glPopMatrix()
            
        common_tree_y_term -= gap

def draw_border():
    glPushMatrix()
    glColor3f(0.2, 0.7, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(road_width+200, road_length, -2)
    glVertex3f(road_width+200, -road_length, -2)
    glVertex3f(-road_width-200, -road_length, -2)
    glVertex3f(-road_width-200, road_length, -2)
    glEnd()

    # left trees
    draw_trees(road_width + 100)

    # right trees
    draw_trees(-road_width - 100)

    glPopMatrix()

def draw_road():
    global element_offset, road_length, element_offset 
    glPushMatrix()

    # road
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(road_width, road_length, 0)
    glVertex3f(road_width, -road_length, 0)
    glVertex3f(-road_width, -road_length, 0)
    glVertex3f(-road_width, road_length, 0)
    glEnd()


    # Lane dividers
    glColor3f(1, 1, 1)

    divider_width = 10
    divider_height = 200
    gap = 150
    z = 1

    common_y = road_length - gap - element_offset   #150 further from screen
    while common_y > -road_length:
        if  -road_length < common_y < road_length:
            glBegin(GL_QUADS)
            glVertex3f(-divider_width, common_y,z) # 1
            glVertex3f(-divider_width, common_y - divider_height,z) # 2
            glVertex3f(divider_width, common_y - divider_height,z) # 3
            glVertex3f(divider_width, common_y,z) # 4
            glEnd()

        common_y -= divider_height + gap


    glPopMatrix()

def draw_ramp():
    global road_length, ramp_length, ramp_width, ramp_angle, ramp_positions

    for ramp_id in list(ramp_positions.keys()):
        ramp_x, ramp_y, ramp_z = ramp_positions[ramp_id]

        if -road_length < ramp_y < road_length:
            glPushMatrix()

            glTranslatef(ramp_x, ramp_y, ramp_z)
            glRotatef(ramp_angle, 1, 0, 0)

            glColor3f(0.1, 0.1, 0.1)

            glBegin(GL_QUADS)
            glVertex3f(-(ramp_width/2), 0, 0)
            glVertex3f((ramp_width/2), 0, 0)
            glVertex3f((ramp_width/2), -ramp_length, 0)
            glVertex3f(-(ramp_width/2), -ramp_length, 0)
            glEnd()

            glPopMatrix()
        else:
            ramp_positions.pop(ramp_id)
            

def draw_car():
    global car_x, car_y, car_z, car_rotation

    glPushMatrix()

    glTranslatef(car_x, car_y + 50, car_z)
    glRotatef(car_rotation, 1, 0, 0)
    glTranslatef(-car_x, -(car_y + 50), -car_z)

    # wheels  
    glColor3f(0.1, 0.1, 0.1)
    quad = gluNewQuadric()
    
    for i in range(4):
        glPushMatrix()
        
        if i == 0:
            glTranslatef(car_x + 30, car_y, car_z)
            glRotatef(90, 0, 1, 0)
        elif i == 1:
            glTranslatef(car_x - 30, car_y, car_z)
            glRotatef(-90, 0, 1, 0)
        elif i == 2:
            glTranslatef(car_x + 30, car_y+100, car_z)
            glRotatef(90, 0, 1, 0)
        else:
            glTranslatef(car_x - 30, car_y+100, car_z)
            glRotatef(-90, 0, 1, 0)

        gluCylinder(quad, 12, 12, 20, 32, 32)  # quadric, baseRadius, topRadius, height, slices, stacks   
        glPopMatrix()

    
    # body
    glColor3f(0.7, 0.7, 0.7)

    glPushMatrix()
    glTranslatef(car_x, car_y-15, car_z + 12*2)

    glBegin(GL_QUADS)


    Y_LEN = 130
    # bottom
    glVertex3f(-50, 0, -15)
    glVertex3f( 50, 0, -15)
    glVertex3f( 50, Y_LEN, -15)
    glVertex3f(-50, Y_LEN, -15)

    # top
    glVertex3f(-50, 0, 15)
    glVertex3f( 50, 0, 15)
    glVertex3f( 50, Y_LEN, 15)
    glVertex3f(-50, Y_LEN, 15)

    # front
    glVertex3f(-50, Y_LEN, -15)
    glVertex3f( 50, Y_LEN, -15)
    glVertex3f( 50, Y_LEN, 15)
    glVertex3f(-50, Y_LEN, 15)

    # back
    glVertex3f(-50, 0, -15)
    glVertex3f( 50, 0, -15)
    glVertex3f( 50, 0, 15)
    glVertex3f(-50, 0, 15)

    # left
    glVertex3f(-50, 0, -15)
    glVertex3f(-50, Y_LEN, -15)
    glVertex3f(-50, Y_LEN, 15)
    glVertex3f(-50, 0, 15)

    # right
    glVertex3f(50, 0, -15)
    glVertex3f(50, Y_LEN, -15)
    glVertex3f(50, Y_LEN, 15)
    glVertex3f(50, 0, 15)

    glEnd()
    glPopMatrix()


    glPopMatrix()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, window_width, window_height)

    setupCamera()

    # game graphics
    draw_sky()
    draw_road()
    draw_border()
    draw_ramp()
    draw_car()

    glutSwapBuffers()

def animate():
    # all scenario animations
    global element_offset, game_speed, last_time, ramp_positions, last_ramp_time, ramp_spawn_delay

    current_time = time.time()
    dt = current_time - last_time   # seconds elapsed since last frame
    last_time = current_time
    element_offset -= game_speed * dt * 100


    # ramp position animations
    for id, positions in ramp_positions.items():
        ramp_x, ramp_y, ramp_z = positions
        ramp_y += game_speed * dt * 100
        ramp_positions[id] = (ramp_x, ramp_y, ramp_z)

    if current_time - last_ramp_time >= ramp_spawn_delay:
        new_x = random.randint(-200, 200)  # random x position
        new_y = 0                       
        new_z = 2

        ramp_id = max(ramp_positions.keys(), default=0) + 1
        ramp_positions[ramp_id] = (new_x, new_y, new_z)
        last_ramp_time = current_time

    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)

    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(300,100)
    glutCreateWindow(b"Noob Driver")
    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)

    glutIdleFunc(animate)

    glutSpecialFunc(specialKeyboardListener)
    glutMouseFunc(mouseListener)
    glutKeyboardFunc(keyboardListener)


    glutMainLoop()


if __name__ == "__main__":
    main()