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
game_speed = 5
last_time = time.time()


# graphics related variables
isDay = False

road_width = 400
road_length = 4500

element_offset = 0

tree_offset = 0

# car stats
# car_x, car_y, car_z = 


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
        camera_position = (cam_x, cam_y, cam_z)

    if key == GLUT_KEY_DOWN:
        cam_z = max(cam_z - step, 50)
        camera_position = (cam_x, cam_y, cam_z)

def mouseListener():
    pass


def keyboardListener(key, x, y):
    global sky_color, isDay
    
    if key == b'n' or key == b'N': #day and night shifter
        isDay = not isDay


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

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, window_width, window_height)

    setupCamera()

    # game graphics
    draw_sky()
    draw_road()
    draw_border()

    glutSwapBuffers()

def animate():
    global element_offset, game_speed, last_time

    current_time = time.time()
    dt = current_time - last_time   # seconds elapsed since last frame
    last_time = current_time
    element_offset -= game_speed * dt * 100

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