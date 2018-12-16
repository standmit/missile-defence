"""
    Missile Defence Game
    Projectile drawing and simulation module.
    
    Copyright (C) 2011-2012 Ryan Lothian.
    See LICENSE (GNU GPL version 3 or later).
"""

import pygame
from background import grad
import random
from random import uniform
import numpy
from math import sqrt

class Projectile(object):
    def __init__(self, position, velocity, radius):
        self.position = [float(x) for x in position]
        self.velocity = [float(v) for v in velocity]
        self.radius   = radius
        
    def apply_physics(self, physics):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

    def get_int_position(self):
        return [int(x) for x in self.position]


class Missile(Projectile):
    def __init__(self, position, target, velocity):
        self.draw_radius      = 4
        self.target           = target
        
        distance = (self.target[0] - position[0], self.target[1] - position[1])
        distance_total = sqrt(pow(distance[0], 2) + pow(distance[1], 2))
        horz_vel = distance[0] / distance_total * velocity
        vert_vel = distance[1] / distance_total * velocity
        
        super(Missile, self).__init__(position, (horz_vel, vert_vel), self.draw_radius)
        self.trail            = []        
        self.trail_length     = 20
        self.trail_radius     = self.draw_radius
        self.start_pos        = position
        self.exploding        = False
        self.blast_ticks_done = 0
        self.blast_radius     = 20
        self.blast_ticks      = 100
        self.colour_front     = (250, 250, 250)
        self.colour_tail      = (200, 20, 100)
        self.blast_colour_a   = (255, 255, 0)
        self.blast_colour_b   = (255, 0, 0)        
        self.invulnerable_ticks = 0
        self.cannon_fire      = False
        
    def is_garbage(self, resolution):
        if self.exploding:
            return self.blast_ticks_done > self.blast_ticks
        elif self.position[1] > (resolution[1] + self.blast_radius + 
                                 self.draw_radius): # off screen bttom
            return True
        elif self.position[0] > resolution[0] + 200 and \
             self.velocity[0] > 0: # way off right
             return True
        elif self.position[0] < -200 and \
             self.velocity[0] < 0: # way off left
             return True
        elif self.position[1] < -200 and \
             self.velocity[1] < 0: # way off top
             return True
        else:
            return False
        
    def apply_physics(self, physics, buildings):
        if self.exploding:
            self.blast_ticks_done += 1
            self.apply_explosion(buildings)
        else:           
            Projectile.apply_physics(self, physics)
            self.trail.append(list(self.position))
            if len(self.trail) > self.trail_length: self.trail.pop(0)
           
            int_pos = self.get_int_position()
            if self.invulnerable_ticks == 0:
                physics.check_collision(self)
            else:
                self.invulnerable_ticks -= 1

 
    def get_current_explosion_proportion(self):       
        proportion = self.blast_ticks_done / float(self.blast_ticks)
        return proportion
        
    def get_current_explosion_radius(self):
        proportion = self.get_current_explosion_proportion()
        if proportion > 1.0:
            proportion = 1.0  # don't explode too big on the final tick
        
        radius = self.draw_radius + (self.blast_radius - self.draw_radius) * proportion
        return radius
        
    def apply_explosion(self, buildings):        
        self.blast_ticks_done += 1
        self.radius = int(self.get_current_explosion_radius()) - 1
        buildings.destroy_circle(self.position, self.radius)
    
    def draw_marker(self, screen):
        inner_rad = 4
        outer_rad = 6
        
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (int(self.position[0]) - outer_rad, int(self.position[1]) - outer_rad),
            (int(self.position[0]) - inner_rad, int(self.position[1]) - inner_rad)
        )
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (int(self.position[0]) + outer_rad, int(self.position[1]) - outer_rad),
            (int(self.position[0]) + inner_rad, int(self.position[1]) - inner_rad)
        )
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (int(self.position[0]) + outer_rad, int(self.position[1]) + outer_rad),
            (int(self.position[0]) + inner_rad, int(self.position[1]) + inner_rad)
        )
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (int(self.position[0]) - outer_rad, int(self.position[1]) + outer_rad),
            (int(self.position[0]) - inner_rad, int(self.position[1]) + inner_rad)
        )
       
    def draw(self, screen):
        pygame.draw.line(screen, (110, 110, 110), self.start_pos, self.position)
            
        prev_pos = None
        i        = 0
        for t_i in range(0, len(self.trail) - self.draw_radius + 1):
            pos = self.trail[t_i]
            i += 1
            int_pos = [int(x) for x in pos]                
            if prev_pos is not None:
                pygame.draw.line(screen, grad(self.colour_tail,
                                              self.colour_front, 
                                              i / float(len(self.trail))),
                                 int_pos, prev_pos,
                                 int((i * self.trail_radius) / len(self.trail)))
            prev_pos = int_pos
        
        pygame.draw.circle(screen, self.colour_front, self.get_int_position(), int(2))
        
        if not self.exploding:
            self.draw_marker(screen)
        
        if self.exploding:
            pygame.draw.circle(screen,
                               grad(self.blast_colour_a,
                                    self.blast_colour_b,
                                    self.get_current_explosion_proportion()),
                               self.get_int_position(),
                               int(self.get_current_explosion_radius()))

