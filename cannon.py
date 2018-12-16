"""
    Missile Defence Game
    Cannon drawing and simulation module.
    
    Copyright (C) 2011-2012 Ryan Lothian.
    See LICENSE (GNU GPL version 3 or later).
"""

from numpy import array
import pygame
from maths import normalize
import math
import projectiles

class CounterMissile(projectiles.Missile):
    def __init__(self, centre, target):
        super(CounterMissile, self).__init__(centre, target, 3.6)
        self.size_increase_remaining = 30
        
        self.draw_radius    = 2
        self.trail_length   = 8
        self.trail_radius   = 4
        self.blast_colour_a = (150, 180, 255)
        self.blast_colour_b = (255, 0, 0)
        self.radius         = 0
        self.invulnerable_ticks = 6
        self.cannon_fire    = 1
    
    def draw_marker(self, screen):
        rad = 2
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (int(self.target[0]) - rad, int(self.target[1]) - rad),
            (int(self.target[0]) + rad, int(self.target[1]) + rad)
        )
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (int(self.target[0]) + rad, int(self.target[1]) - rad),
            (int(self.target[0]) - rad, int(self.target[1]) + rad)
        )
                    
class MissileLauncher(object):
    def __init__(self, centre, game):
        self.target = array([100, -100])
        self.centre = array(centre)
        self.length = 30
        self.game = game
        self.ticks_since_firing = 0
        self.destroyed = False
                
    def apply_physics(self):    
        self.ticks_since_firing += 1    
        
        # must have support
        if not self.destroyed:
            if not self.game.buildings.get(self.centre[0], self.centre[1]):
                self.destroyed = True            
                explosion = projectiles.Missile(self.centre, (0, 0), 0.)
                explosion.exploding = True
                explosion.blast_colour_a = (100, 200, 150)
                explosion.blast_colour_b = (20, 50, 20) 
                explosion.blast_radius = self.length
                explosion.blast_ticks = 30 
                self.game.projectiles.append(explosion)
                    
    def draw(self, surface):
        if not self.destroyed:
            launcher_size = 3
            pygame.draw.line(surface,
                             (100,200,100),
                             (self.centre[0] - launcher_size, self.centre[1]),
                             (self.centre[0] + launcher_size, self.centre[1]), 
                             4)
        
    def can_fire(self):
        return self.ticks_since_firing > 8 and not self.destroyed

    def create_missile(self, target):
        new_missile = CounterMissile(self.centre, target)
                                                
        self.game.projectiles.append(new_missile)
                           
    def fire(self, target):
        if self.can_fire():            
            self.target = target
            self.ticks_since_firing = 0
            self.create_missile(target)
