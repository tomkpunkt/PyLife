import pygame
import pymunk
import numpy as np

class Waste:
    def __init__(self, space, x, y, size, quality):
        """Initialisiert ein Abfall-Objekt"""
        self.size = size  # Größe des Abfalls
        self.quality = quality  # Ursprüngliche Qualität der Nahrung
        self.age = 0  # Alter des Abfalls
        self.decay_time = int(300 * size)  # Zeit bis zum Verschwinden
        
        # Physikalische Eigenschaften
        self.radius = 3 * size  # Basis-Radius für Kollision
        self.mass = 0.05 * size
        
        # Physik-Body erstellen
        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment, pymunk.Body.STATIC)
        self.body.position = x, y
        
        # Shape erstellen
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = 0.3
        self.shape.elasticity = 0.1
        
        # Zur Physik-Engine hinzufügen
        space.add(self.body, self.shape)
        
        # Farbe (Brauntöne)
        brown_variation = np.random.uniform(-20, 20)
        self.color = (
            min(255, max(0, int(139 + brown_variation))),  # Basis: Braun
            min(255, max(0, int(69 + brown_variation))),
            min(255, max(0, int(19 + brown_variation)))
        )
    
    def update(self, dt):
        """Aktualisiert den Zustand des Abfalls"""
        self.age += 1
        
        # Abfall verschwindet nach einiger Zeit
        if self.age >= self.decay_time:
            return False
        return True
    
    def is_depleted(self):
        """Prüft, ob der Abfall verschwunden ist"""
        return self.age >= self.decay_time
    
    def draw(self, screen):
        """Zeichnet den Abfall"""
        pos = self.body.position
        
        # Hauptkörper des Abfalls
        pygame.draw.circle(screen, self.color,
                         (int(pos.x), int(pos.y)),
                         int(self.radius))
        
        # Textur/Muster für mehr Detail
        pattern_color = (
            max(0, self.color[0] - 20),
            max(0, self.color[1] - 20),
            max(0, self.color[2] - 20)
        )
        
        # Zufällige Punkte für Textur
        for _ in range(int(self.radius * 2)):
            angle = np.random.uniform(0, 2 * np.pi)
            r = np.random.uniform(0, self.radius * 0.8)
            x = pos.x + np.cos(angle) * r
            y = pos.y + np.sin(angle) * r
            pygame.draw.circle(screen, pattern_color,
                             (int(x), int(y)),
                             max(1, int(self.radius * 0.1))) 