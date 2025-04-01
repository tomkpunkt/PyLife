import pygame
import pymunk
import numpy as np
import random

class Food:
    def __init__(self, space, x, y, size=None, quality=None):
        """Initialisiert ein neues Nahrungsobjekt"""
        self.size = size if size is not None else random.uniform(0.2, 1.0)
        self.quality = quality if quality is not None else random.uniform(0.0, 1.0)
        
        # Physikalische Eigenschaften
        self.radius = 5 + 10 * self.size  # Radius zwischen 5 und 15
        self.mass = self.radius * 0.3  # Masse proportional zum Radius
        
        # Erstelle den physikalischen Körper
        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.7
        self.shape.friction = 0.5
        space.add(self.body, self.shape)
        
        # Energie-Wert basierend auf Größe und Qualität
        self.energy_value = self.size * 50 * self.quality  # Direkte Multiplikation
        
        # Glow-Effekt für hochwertige Nahrung
        self.glow_radius = int(self.radius * self.quality) if self.quality > 0.5 else 0
        self.glow_alpha = int(255 * self.quality) if self.quality > 0.5 else 0
        
        # Farbe basierend auf Qualität berechnen
        self._calculate_color()
    
    def _calculate_color(self):
        """Berechnet die Farbe basierend auf der Qualität"""
        # Grün-Komponente basierend auf Qualität
        green = int(255 * self.quality)
        # Minimale Rot- und Blau-Komponenten
        red = 0
        blue = 0
        self.color = (red, green, blue)
    
    @property
    def mass(self):
        """Gibt die aktuelle Masse zurück"""
        return self._mass
    
    @mass.setter
    def mass(self, value):
        """Setzt die Masse"""
        self._mass = value
        if hasattr(self, 'body'):
            self.body.mass = value
    
    @property
    def size(self):
        """Gibt die aktuelle Größe zurück"""
        return self._size
    
    @size.setter
    def size(self, value):
        """Setzt die Größe und aktualisiert abhängige Eigenschaften"""
        self._size = value
        if hasattr(self, 'radius'):
            self.radius = 5 + 10 * value
            self.mass = self.radius * 0.3
            if hasattr(self, 'quality'):
                self.energy_value = value * 50 * self.quality
                self.glow_radius = int(self.radius * self.quality) if self.quality > 0.5 else 0
                self.glow_alpha = int(255 * self.quality) if self.quality > 0.5 else 0
    
    def draw(self, surface):
        """Zeichnet das Nahrungsobjekt"""
        # Position auf dem Bildschirm
        screen_pos = (int(self.body.position.x), int(self.body.position.y))
        
        # Glow-Effekt zeichnen wenn Qualität hoch genug
        if self.quality > 0.5:
            glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, self.glow_alpha), 
                             (self.glow_radius, self.glow_radius), self.glow_radius)
            surface.blit(glow_surface, (screen_pos[0] - self.glow_radius, 
                                      screen_pos[1] - self.glow_radius))
        
        # Hauptkörper zeichnen
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)
        
        # Qualitätsindikator (innerer Kreis)
        inner_radius = max(2, self.radius * 0.3)
        pygame.draw.circle(surface, (255, 255, 255), screen_pos, inner_radius)
        
        # Highlight für 3D-Effekt
        highlight_pos = (int(screen_pos[0] - self.radius * 0.3), 
                        int(screen_pos[1] - self.radius * 0.3))
        highlight_radius = int(self.radius * 0.4)
        highlight_color = (
            min(255, self.color[0] + 40),
            min(255, self.color[1] + 40),
            min(255, self.color[2] + 40)
        )
        pygame.draw.circle(surface, highlight_color, 
                         highlight_pos, highlight_radius)
        
        # Qualitätsmarkierung (kleine Punkte für hochwertige Nahrung)
        if self.quality > 0.7:
            dots = int(3 + (self.quality - 0.7) * 5)  # 3-8 Punkte je nach Qualität
            for i in range(dots):
                angle = (2 * np.pi * i) / dots
                dot_x = screen_pos[0] + np.cos(angle) * (self.radius * 0.6)
                dot_y = screen_pos[1] + np.sin(angle) * (self.radius * 0.6)
                pygame.draw.circle(surface, (255, 255, 255), 
                                 (int(dot_x), int(dot_y)), 
                                 int(self.radius * 0.15)) 