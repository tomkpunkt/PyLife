import numpy as np
import pymunk
import pygame
from neural_network import NeuralNetwork
from creature_renderer import CreatureRenderer

class Entity:
    # Statischer CreatureRenderer für alle Entities
    renderer = CreatureRenderer()
    
    def __init__(self, space, x, y, dna=None):
        # DNA für genetische Eigenschaften
        self.dna = dna if dna is not None else self._generate_dna()
        
        # Physikalische Eigenschaften basierend auf DNA
        self.radius = 15 * self.dna['size']  # Basis-Radius für Kollision
        self.mass = 1.0 * self.dna['size']
        self.friction = 0.7
        self.elasticity = 0.5
        
        # Physik-Body erstellen
        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = x, y
        self.body.angle = np.random.uniform(0, 2 * np.pi)  # Zufällige Startrichtung
        
        # Shape erstellen
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity
        
        # Zur Physik-Engine hinzufügen
        space.add(self.body, self.shape)
        
        # Neuronales Netz
        self.brain = NeuralNetwork()
        
        # Bewegungsparameter
        self.base_speed = 100 * self.dna['speed']
        self.turn_rate = 2.0  # Drehgeschwindigkeit in Radiant pro Sekunde
        self.movement_timer = 0
        self.direction_change_time = np.random.uniform(1, 3)  # Zeit bis zur Richtungsänderung
        self.current_direction = np.random.uniform(-1, 1)  # Aktuelle Drehrichtung
        
        # Grundlegende Attribute
        self.age = 0
        self.max_age = 3000  # Maximale Lebensdauer erhöht
        self.health = 100 * self.dna['health']
        self.max_health = 100 * self.dna['health']
        self.energy = 100
        self.max_energy = 100
        self.hunger = 0
        self.max_hunger = 100
        self.speed = 100 * self.dna['speed']
        self.energy_efficiency = self.dna['energy_efficiency']
        self.sensor_range = 100 * self.dna['sensor_range']
        
        # Fortpflanzungsattribute
        self.reproduction_cooldown = 0
        self.reproduction_cost = 30  # Reduziert
        
        # Statistik
        self.food_eaten = 0
        self.children = 0
        self.distance_traveled = 0
        
        # Kreatur-Textur erstellen
        self.texture = self.renderer.render_creature(self.dna)
        self.texture_rect = self.texture.get_rect()
    
    def _generate_dna(self):
        """Generiert zufällige DNA für die Entity"""
        return {
            'size': np.random.uniform(0.8, 1.2),
            'speed': np.random.uniform(0.8, 1.2),
            'energy_efficiency': np.random.uniform(0.8, 1.2),
            'sensor_range': np.random.uniform(0.8, 1.2),
            'health': np.random.uniform(0.8, 1.2),
            'reproduction_rate': np.random.uniform(0.8, 1.2),
            # Neue visuelle DNA-Eigenschaften
            'eye_count': np.random.uniform(1, 4),
            'spike_factor': np.random.uniform(0.5, 1.5),
            'spike_length': np.random.uniform(0.5, 1.5),
            'movement_organ_count': np.random.uniform(0.5, 1.5),
            'movement_organ_size': np.random.uniform(0.8, 1.2)
        }
    
    def move(self, dt):
        """Bewegt die Entity"""
        # Timer für Richtungsänderung aktualisieren
        self.movement_timer += dt
        if self.movement_timer >= self.direction_change_time:
            self.movement_timer = 0
            self.direction_change_time = np.random.uniform(1, 3)
            self.current_direction = np.random.uniform(-1, 1)
        
        # Aktuelle Richtung ändern
        self.body.angle += self.current_direction * self.turn_rate * dt
        
        # Bewegungsvektor basierend auf Blickrichtung
        direction = pymunk.Vec2d(1, 0).rotated(self.body.angle)
        
        # Geschwindigkeit basierend auf Energie
        current_speed = self.base_speed * (self.energy / self.max_energy)
        
        # Bewegung anwenden
        self.body.velocity = direction * current_speed
        
        # Zurückgelegte Distanz aktualisieren
        self.distance_traveled += current_speed * dt
    
    def update(self, dt):
        """Aktualisiert den Zustand der Entity"""
        # Bewegung aktualisieren
        self.move(dt)
        
        # Alter erhöhen
        self.age += 1
        
        # Energie verbrauchen (abhängig von Bewegung und DNA)
        velocity_factor = np.linalg.norm(self.body.velocity) / self.base_speed
        energy_consumption = 0.05 * dt * (1 / self.energy_efficiency) * (1 + velocity_factor)  # Reduziert
        self.energy = max(0, self.energy - energy_consumption)
        
        # Hunger erhöhen
        self.hunger = min(self.max_hunger, self.hunger + 0.05 * dt)  # Reduziert
        
        # Wenn keine Energie mehr oder zu viel Hunger, Gesundheit reduzieren
        if self.energy <= 0 or self.hunger >= self.max_hunger:
            self.health -= 0.5 * dt  # Reduziert
            self.energy = 0
        
        # Wenn keine Gesundheit mehr oder zu alt, Entity entfernen
        if self.health <= 0 or self.age >= self.max_age:
            return False
            
        # Fortpflanzungs-Cooldown aktualisieren
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
            
        return True
    
    def eat_food(self, food_energy):
        """Entity isst Nahrung"""
        self.energy = min(self.max_energy, self.energy + food_energy)
        self.hunger = max(0, self.hunger - 30)  # Erhöht
        self.food_eaten += 1
        
    def can_reproduce(self):
        """Prüft, ob die Entity sich fortpflanzen kann"""
        return (self.energy >= self.reproduction_cost and 
                self.reproduction_cooldown <= 0 and 
                self.health > self.max_health * 0.7)
    
    def reproduce(self):
        """Entity pflanzt sich fort"""
        if self.can_reproduce():
            self.energy -= self.reproduction_cost
            self.reproduction_cooldown = 100
            self.children += 1
            return True
        return False
    
    def draw(self, screen):
        """Zeichnet die Entity auf den Bildschirm"""
        # Position aus der Physik-Engine holen
        pos = self.body.position
        angle = self.body.angle
        
        # Textur rotieren
        rotated_texture = pygame.transform.rotate(self.texture, -angle * 180 / np.pi)
        rotated_rect = rotated_texture.get_rect()
        
        # Position zentrieren
        pos = (int(pos.x - rotated_rect.width/2), 
               int(pos.y - rotated_rect.height/2))
        
        # Textur zeichnen
        screen.blit(rotated_texture, pos)
        
        # Statusbalken-Einstellungen
        bar_width = 40
        bar_height = 4
        bar_spacing = 6
        bar_pos = (int(pos[0] + rotated_rect.width/2 - bar_width/2), 
                  int(pos[1] - 15))
        
        def draw_status_bar(pos_y, value, max_value, color, background_color=(60, 60, 60)):
            """Zeichnet einen schönen Statusbalken"""
            # Hintergrund (dunkelgrau)
            pygame.draw.rect(screen, background_color, 
                           (bar_pos[0], pos_y, bar_width, bar_height))
            
            # Füllstand
            fill_width = int(bar_width * (value/max_value))
            if fill_width > 0:
                pygame.draw.rect(screen, color, 
                               (bar_pos[0], pos_y, fill_width, bar_height))
            
            # Rahmen
            pygame.draw.rect(screen, (40, 40, 40), 
                           (bar_pos[0], pos_y, bar_width, bar_height), 1)
        
        # Gesundheitsanzeige (Grün)
        draw_status_bar(bar_pos[1], self.health, self.max_health, 
                       (100, 200, 100))
        
        # Hungeranzeige (Orange)
        draw_status_bar(bar_pos[1] - bar_spacing, self.hunger, self.max_hunger, 
                       (230, 160, 30))
        
        # Energieanzeige (Blau)
        draw_status_bar(bar_pos[1] - bar_spacing * 2, self.energy, self.max_energy, 
                       (70, 130, 180))

    def draw_preview(self, surface):
        """Zeichnet eine große Vorschau der Entity"""
        # Skalierungsfaktor berechnen
        scale = min(
            (surface.get_width() - 20) / self.texture.get_width(),
            (surface.get_height() - 20) / self.texture.get_height()
        ) * 0.8  # 80% der verfügbaren Größe
        
        # Textur skalieren
        scaled_width = int(self.texture.get_width() * scale)
        scaled_height = int(self.texture.get_height() * scale)
        scaled_texture = pygame.transform.scale(self.texture, (scaled_width, scaled_height))
        
        # Position zentrieren
        x = (surface.get_width() - scaled_width) // 2
        y = (surface.get_height() - scaled_height) // 2
        
        # Textur zeichnen
        surface.blit(scaled_texture, (x, y))
        
        # Statusbalken-Einstellungen für die Vorschau
        bar_width = int(scaled_width * 1.2)  # 20% breiter als die Textur
        bar_height = 8
        bar_spacing = 12
        bar_x = (surface.get_width() - bar_width) // 2
        bar_y = y + scaled_height + 10
        
        def draw_preview_bar(pos_y, value, max_value, color, background_color=(60, 60, 60)):
            """Zeichnet einen großen Statusbalken für die Vorschau"""
            # Hintergrund
            pygame.draw.rect(surface, background_color, 
                           (bar_x, pos_y, bar_width, bar_height))
            
            # Füllstand
            fill_width = int(bar_width * (value/max_value))
            if fill_width > 0:
                pygame.draw.rect(surface, color, 
                               (bar_x, pos_y, fill_width, bar_height))
            
            # Rahmen
            pygame.draw.rect(surface, (40, 40, 40), 
                           (bar_x, pos_y, bar_width, bar_height), 1)
        
        # Gesundheitsanzeige (Grün)
        draw_preview_bar(bar_y, self.health, self.max_health, 
                        (100, 200, 100))
        
        # Hungeranzeige (Orange)
        draw_preview_bar(bar_y + bar_spacing, self.hunger, self.max_hunger, 
                        (230, 160, 30))
        
        # Energieanzeige (Blau)
        draw_preview_bar(bar_y + bar_spacing * 2, self.energy, self.max_energy, 
                        (70, 130, 180)) 