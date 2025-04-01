import pygame
import pymunk
import numpy as np

class Food:
    def __init__(self, space, x, y):
        # Zufällige Größe und Qualität
        self.size = np.random.uniform(0.5, 2.0)  # 0.5x bis 2x normale Größe
        self.quality = np.random.uniform(0.8, 1.5)  # 0.8x bis 1.5x normale Energie
        
        # Physikalische Eigenschaften
        self.radius = 5 * self.size  # Basis-Radius für Kollision
        self.mass = 0.1 * self.size
        
        # Energie-Wert basierend auf Größe und Qualität
        self.energy_value = 30 * self.size * self.quality
        
        # Physik-Body erstellen
        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment, pymunk.Body.STATIC)
        self.body.position = x, y
        
        # Shape erstellen
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = 0.5
        self.shape.elasticity = 0.3
        
        # Zur Physik-Engine hinzufügen
        space.add(self.body, self.shape)
        
        # Farbe basierend auf Qualität (Grüntöne)
        base_green = min(255, int(100 + self.quality * 100))  # Basis-Grün
        self.color = (
            min(255, int(40 + self.quality * 30)),  # Etwas Rot für Wärme
            base_green,  # Hauptsächlich Grün
            min(255, int(40 + self.quality * 20))   # Etwas Blau für Tiefe
        )
        
        # Glühen-Effekt für hohe Qualität (grünlich)
        self.glow_radius = int(self.radius * (1 + self.quality * 0.3))
        self.glow_color = (
            min(255, self.color[0] + 20),
            min(255, self.color[1] + 40),  # Stärkeres Grün im Glühen
            min(255, self.color[2] + 20),
            100  # Alpha für Transparenz
        )
    
    def draw(self, screen):
        """Zeichnet das Nahrungsstück mit Qualitätseffekten"""
        pos = self.body.position
        
        # Glühen für hochwertige Nahrung
        if self.quality > 1.0:
            glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, self.glow_color, 
                             (self.glow_radius, self.glow_radius), 
                             self.glow_radius)
            screen.blit(glow_surface, 
                       (int(pos.x - self.glow_radius), 
                        int(pos.y - self.glow_radius)))
        
        # Hauptkörper der Nahrung
        pygame.draw.circle(screen, self.color, 
                         (int(pos.x), int(pos.y)), 
                         int(self.radius))
        
        # Highlight für 3D-Effekt
        highlight_pos = (int(pos.x - self.radius * 0.3), 
                        int(pos.y - self.radius * 0.3))
        highlight_radius = int(self.radius * 0.4)
        highlight_color = (
            min(255, self.color[0] + 40),
            min(255, self.color[1] + 40),
            min(255, self.color[2] + 40)
        )
        pygame.draw.circle(screen, highlight_color, 
                         highlight_pos, highlight_radius)
        
        # Qualitätsmarkierung (kleine Punkte für hochwertige Nahrung)
        if self.quality > 1.2:
            dots = int(3 + (self.quality - 1.2) * 5)  # 3-8 Punkte je nach Qualität
            for i in range(dots):
                angle = (2 * np.pi * i) / dots
                dot_x = pos.x + np.cos(angle) * (self.radius * 0.6)
                dot_y = pos.y + np.sin(angle) * (self.radius * 0.6)
                pygame.draw.circle(screen, (255, 255, 255), 
                                 (int(dot_x), int(dot_y)), 
                                 int(self.radius * 0.15)) 