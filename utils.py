import math

import pygame
from OpenGL.raw.GL.VERSION.GL_1_0 import glRasterPos2i, glDrawPixels
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_RGBA, GL_UNSIGNED_BYTE


def drawText(x, y, rgba_color, bg_color, textString):
    font = pygame.font.Font(None, 30)
    textSurface = font.render(textString, True, rgba_color, bg_color)
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos2i(x, y)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)


def box_collision(box1_x, box1_y, box1_w, box1_h, box2_x, box2_y, box2_w, box2_h):
    box1_x = box1_x - box1_w
    box1_y = box1_y + box1_h
    box1_w = box1_w*2
    box1_h = box1_h*2
    box2_x = box2_x - box2_w
    box2_y = box2_y + box2_h
    box2_w = box2_w*2
    box2_h = box2_h*2
    return ((box1_x < box2_x + box2_w)
            and (box1_x + box1_w > box2_x)
            and (box1_y < box2_y + box2_h)
            and (box1_y + box1_h > box2_y))


def circle_collision(circle1_pos, circle1_radius, circle2_pos, circle2_radius, impact_vector):
    dx = circle2_pos[0] - circle1_pos[0]
    dy = circle2_pos[1] - circle1_pos[1]
    radius = circle1_radius + circle2_radius
    pyth = ((dx*dx) + (dy*dy))
    collision = (pyth < (radius*radius))
    #WARNING: Dont Try to improve this code without reading the comments in car_circle_collision and understanding the consequences!!!
    if collision:
        impact_vector.append(dx)
        impact_vector.append(dy)
        impact_vector.append((radius - math.sqrt(pyth))/radius)
    return collision


def rotate_2d_vector(vector, angle):
    cs = math.cos(math.pi*angle/180)
    sn = math.sin(math.pi*angle/180)
    x = vector[0]
    y = vector[1]
    return [x*cs-y*sn, x*sn+y*cs]


def car_circle_collision(car1, car2, impact_vector=[], car1_x_offset=0, car1_y_offset=0):
    car1_rear_circle = ( car1.rear_circle[0]+car1.horizontal_position+car1_x_offset, car1.rear_circle[1] + car1.vertical_position+car1_y_offset)
    car1_front_circle = ( car1.front_circle[0]+car1.horizontal_position+car1_x_offset, car1.front_circle[1] + car1.vertical_position+car1_y_offset)
    car2_rear_circle = ( car2.rear_circle[0]+car2.horizontal_position, car2.rear_circle[1] + car2.vertical_position)
    car2_front_circle =  ( car2.front_circle[0]+car2.horizontal_position, car2.vehicle.front_circle[1] + car2.vertical_position)
    # Apparently the "or" goes on even if one of the operands is already known to be True! That messes up the impact vector
    # WARNING: Dont Try to improve this code without reading the previous line and understanding the consequences!!!
    if circle_collision(car1_rear_circle, car1.radius, car2_rear_circle, car2.radius, impact_vector):
        return True
    if circle_collision(car1_rear_circle, car1.radius, car2_front_circle, car2.radius, impact_vector):
        return True
    if circle_collision(car1_front_circle, car1.radius, car2_rear_circle, car2.radius, impact_vector):
        return True
    if circle_collision(car1_front_circle, car1.radius, car2_front_circle, car2.radius, impact_vector):
        return True
    return False


def draw_rectangle(w, h, texture, alpha=1):
    pass

#    glEnable(GL_TEXTURE_2D)
#    glBindTexture(GL_TEXTURE_2D, texture)
#    glMaterialfv(GL_FRONT, GL_AMBIENT, (1, 1, 1, alpha))
#    glMaterialfv(GL_FRONT, GL_DIFFUSE, (1, 1, 1, alpha))
#    glMaterialfv(GL_FRONT, GL_SPECULAR, (1, 1, 1, alpha))
#    glMaterialfv(GL_FRONT, GL_EMISSION, (0.5, 0.5, 0.5, alpha))
#    glMaterialfv(GL_FRONT, GL_SHININESS, 0)
#
#    glBegin(GL_TRIANGLES)
#    glNormal3f(0,0, 1)
#    glTexCoord2f(0, 1)
#    glVertex3f(0, 0, 0)
#    glNormal3f(0, 0, 1)
#    glTexCoord2f(1, 1)
#    glVertex3f(w, 0, 0)
#    glNormal3f(0, 0, 1)
#    glTexCoord2f(0, 0)
#    glVertex3f(0,h,0)
#
#    glNormal3f(0,0, 1)
#    glTexCoord2f(1, 1)
#    glVertex3f(w, 0, 0)
#    glNormal3f(0, 0, 1)
#    glTexCoord2f(0, 0)
#    glVertex3f(0, h, 0)
#    glNormal3f(0, 0, 1)
#    glTexCoord2f(1, 0)
#    glVertex3f(w, h, 0)
#    glEnd()
#
#    glDisable(GL_TEXTURE_2D)


def draw_3d_rectangle(w, h, texture, alpha=1):
    pass

#   glEnable(GL_TEXTURE_2D)
#   glBindTexture(GL_TEXTURE_2D, texture)
#   glMaterialfv(GL_FRONT, GL_AMBIENT, (1, 1, 1, alpha))
#   glMaterialfv(GL_FRONT, GL_DIFFUSE, (1, 1, 1, alpha))
#   glMaterialfv(GL_FRONT, GL_SPECULAR, (1, 1, 1, alpha))
#   glMaterialfv(GL_FRONT, GL_EMISSION, (0.5, 0.5, 0.5, alpha))
#   glMaterialfv(GL_FRONT, GL_SHININESS, 0.0)
#
#    glBegin(GL_TRIANGLES)
#   glNormal3f(0,1, 0)
#   glTexCoord2f(0, 1)
#   glVertex3f(-h/2, 0, -w/2)
#   #glNormal3f(0, 1, 0)
#   glTexCoord2f(1, 1)
#   glVertex3f(-h/2, 0, w/2)
#   glNormal3f(0, 1, 0)
#   glTexCoord2f(0, 0)
#   glVertex3f(h/2, 0, -w/2)
#
#    glNormal3f(0,1, 0)
#    glTexCoord2f(1, 1)
#    glVertex3f(-h/2, 0, w/2)
#    glNormal3f(0, 1, 0)
#    glTexCoord2f(0, 0)
#    glVertex3f(h/2, 0, -w/2)
#    glNormal3f(0, 1, 0)
#    glTexCoord2f(1, 0)
#    glVertex3f(h/2, 0, w/2)
#    glEnd()
#
#    glDisable(GL_TEXTURE_2D)
