import numpy as np
import pymunk
import pygame
from neural_network import NeuralNetwork
from creature_renderer import CreatureRenderer
from brain import Brain

class Entity:
    # Statischer CreatureRenderer für alle Entities
    renderer = CreatureRenderer()
    
    def __init__(self, space, x, y, dna=None):
        """Initialisiert eine neue Entity"""
        # DNA und Eigenschaften
        self.dna = dna if dna is not None else self._generate_dna()
        
        # Basis-Radius basierend auf DNA
        self.radius = 20 * self.dna['size']
        self.mass = 1.0 * self.dna['size']
        
        # Physik-Body erstellen
        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = (x, y)
        
        # Shape erstellen
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = 0.7
        self.shape.elasticity = 0.5
        
        # Zur Physik-Engine hinzufügen
        space.add(self.body, self.shape)
        
        # Weitere Eigenschaften anwenden
        self._apply_dna()
        
        # Status-Variablen
        self.energy = self.max_energy
        self.health = self.max_health
        self.hunger = 0
        self.age = 0
        self.distance_traveled = 0
        self.food_eaten = 0
        self.children = 0
        self.reproduction_cooldown = 0
        self.digestion_cooldown = 0
        self.digesting_food = []
        
        # Bewegungsparameter
        self.base_speed = 100 * self.dna['speed']
        self.turn_rate = 2.0  # Drehgeschwindigkeit in Radiant pro Sekunde
        self.movement_timer = 0
        self.direction_change_time = np.random.uniform(1, 3)  # Zeit bis zur Richtungsänderung
        self.current_direction = np.random.uniform(-1, 1)  # Aktuelle Drehrichtung
        
        # Kreatur-Textur erstellen
        self.texture = self.renderer.render_creature(self.dna)
        self.texture_rect = self.texture.get_rect()
        
        # Neuronales Netzwerk initialisieren
        self.brain = Brain(input_size=8, hidden_size=16, output_size=2)
    
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
            'movement_organ_size': np.random.uniform(0.8, 1.2),
            # Neue Mund-Eigenschaften
            'mouth_size': np.random.uniform(0.6, 1.4),  # Größe des Mundes
            'teeth_count': np.random.uniform(0, 1),     # 0 = keine Zähne (Verschlingen), 1 = viele Zähne (Zerkleinern)
            'digestion_efficiency': np.random.uniform(0.8, 1.2)  # Effizienz der Verdauung
        }
    
    def _apply_dna(self):
        """Wendet die DNA auf die Entity an"""
        # Bewegungsparameter aktualisieren
        self.base_speed = 100 * self.dna['speed']
        self.turn_rate = 2.0  # Drehgeschwindigkeit in Radiant pro Sekunde
        self.movement_timer = 0
        self.direction_change_time = np.random.uniform(1, 3)  # Zeit bis zur Richtungsänderung
        self.current_direction = np.random.uniform(-1, 1)  # Aktuelle Drehrichtung
        
        # Grundlegende Attribute aktualisieren
        self.max_age = 3000  # Maximale Lebensdauer erhöht
        self.max_health = 100 * self.dna['health']
        self.max_energy = 100
        self.max_hunger = 100
        self.speed = 100 * self.dna['speed']
        self.energy_efficiency = self.dna['energy_efficiency']
        self.sensor_range = 100 * self.dna['sensor_range']
        
        # Verdauungssystem aktualisieren
        self.digesting_food = []  # Liste von (Energie, Restzeit, Qualität) Tupeln
        self.digestion_cooldown = 0  # Cooldown zwischen Mahlzeiten
        
        # Fortpflanzungsattribute aktualisieren
        self.reproduction_cooldown = 0
        self.reproduction_cost = 30  # Reduziert
        
        # Kreatur-Textur aktualisieren
        self.texture = self.renderer.render_creature(self.dna)
        self.texture_rect = self.texture.get_rect()
    
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
    
    def get_brain_inputs(self):
        """Sammelt alle Inputs für das neuronale Netz"""
        # Normalisierte Inputs zwischen -1 und 1
        inputs = np.zeros(8)
        
        # 1. Energie-Level (0 = leer, 1 = voll)
        inputs[0] = (self.energy / self.max_energy) * 2 - 1
        
        # 2. Hunger-Level (0 = satt, 1 = hungrig)
        inputs[1] = (self.hunger / self.max_hunger) * 2 - 1
        
        # 3. Gesundheit (0 = tot, 1 = volle Gesundheit)
        inputs[2] = (self.health / self.max_health) * 2 - 1
        
        # 4. Alter (0 = jung, 1 = alt)
        max_age = 1000  # Maximales Alter
        inputs[3] = (self.age / max_age) * 2 - 1
        
        # 5. Nahrung in der Nähe (Abstand zum nächsten Futter)
        nearest_food_dist = float('inf')
        nearest_food_dir = 0
        for food in self.simulation.food:
            dx = food.body.position.x - self.body.position.x
            dy = food.body.position.y - self.body.position.y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < nearest_food_dist:
                nearest_food_dist = dist
                nearest_food_dir = np.arctan2(dy, dx) / np.pi  # -1 bis 1
        
        # 5-6. Abstand und Richtung zur nächsten Nahrung
        inputs[4] = 1 - min(1, nearest_food_dist / 500) * 2  # Abstand (500 = Sichtweite)
        inputs[5] = nearest_food_dir  # Richtung (-1 bis 1)
        
        # 7-8. Aktuelle Bewegungsrichtung und -geschwindigkeit
        velocity = (self.body.velocity.x**2 + self.body.velocity.y**2) ** 0.5
        direction = np.arctan2(self.body.velocity.y, self.body.velocity.x) / np.pi
        inputs[6] = direction  # -1 bis 1
        inputs[7] = min(1, velocity / self.speed) * 2 - 1  # Normalisierte Geschwindigkeit
        
        return inputs.reshape(1, -1)  # Reshape für das neuronale Netz
    
    def apply_brain_outputs(self, outputs):
        """Wendet die Ausgaben des neuronalen Netzes an"""
        # Ausgaben sind:
        # 1. Bewegungsrichtung (-1 bis 1, wird zu Winkel -pi bis pi)
        # 2. Geschwindigkeit (0 bis 1, wird mit max_speed multipliziert)
        
        direction = outputs[0, 0] * np.pi  # Umwandlung in Winkel
        speed = (outputs[0, 1] + 1) / 2 * self.speed  # Umwandlung in Geschwindigkeit
        
        # Bewegungsvektor berechnen
        force_x = np.cos(direction) * speed
        force_y = np.sin(direction) * speed
        
        # Kraft auf die Entity anwenden
        self.body.apply_force_at_local_point((force_x, force_y), (0, 0))
    
    def update(self, dt):
        """Aktualisiert den Zustand der Entity"""
        # Gehirn-Update
        inputs = self.get_brain_inputs()
        outputs = self.brain.forward(inputs)
        self.apply_brain_outputs(outputs)
        
        # Bewegung aktualisieren
        self.move(dt)
        
        # Alter erhöhen
        self.age += 1
        
        # Basisverbrauch basierend auf Körpergröße
        base_consumption = 0.08 * dt * self.dna['size']  # Größere Kreaturen verbrauchen mehr Energie
        
        # Aktivitätsbasierter Verbrauch
        velocity_factor = np.linalg.norm(self.body.velocity) / self.base_speed
        movement_consumption = 0.1 * dt * (1 / self.energy_efficiency) * velocity_factor * self.dna['size']
        
        # Verdauungsenergie (wenn aktiv am Verdauen)
        digestion_factor = len(self.digesting_food) * 0.02 * dt
        
        # Erhöhter Energieverbrauch bei maximalem Hunger
        hunger_factor = 1.0
        if self.hunger >= self.max_hunger:
            hunger_factor = 2.0  # Doppelter Energieverbrauch bei maximalem Hunger
        
        # Gesamtenergieverbrauch
        total_consumption = (base_consumption + movement_consumption + digestion_factor) * hunger_factor
        self.energy = max(0, self.energy - total_consumption)
        
        # Hunger basierend auf Aktivität und Größe erhöhen
        hunger_increase = (0.15 * dt * self.dna['size']  # Basisanstieg nach Größe (von 0.1 auf 0.15)
                         + 0.225 * dt * velocity_factor   # Bewegungsabhängiger Anstieg (von 0.15 auf 0.225)
                         + 0.075 * dt * len(self.digesting_food))  # Verdauungsabhängiger Anstieg (von 0.05 auf 0.075)
        self.hunger = min(self.max_hunger, self.hunger + hunger_increase)
        
        # Verdauung verarbeiten
        if self.digestion_cooldown > 0:
            self.digestion_cooldown -= 1
        
        waste_to_create = []
        for food in self.digesting_food[:]:  # Kopie der Liste für sichere Modifikation
            if food['ticks_remaining'] > 0:
                # Energie aus der Verdauung gewinnen
                self.energy = min(self.max_energy, self.energy + food['energy_per_tick'])
                self.hunger = max(0, self.hunger - (food['energy_per_tick'] * 0.5))
                food['ticks_remaining'] -= 1
            else:
                # Verdauung abgeschlossen, Abfall erzeugen
                waste_to_create.append((food['waste_size'], food['quality']))
                self.digesting_food.remove(food)
        
        # Abfall erzeugen
        for waste_size, quality in waste_to_create:
            # Position leicht versetzt von der Entity
            angle = self.body.angle + np.pi  # Hinter der Entity
            offset = 20 * waste_size
            waste_x = self.body.position.x + np.cos(angle) * offset
            waste_y = self.body.position.y + np.sin(angle) * offset
            # Hier müssen wir später die Waste-Klasse erstellen und den Abfall spawnen
        
        # Gesundheit reduzieren wenn Energie auf 0
        if self.energy <= 0:
            self.health -= 0.5 * dt  # Gesundheit nimmt ab wenn keine Energie mehr vorhanden
            if self.health <= 0:
                self.health = 0
                return False  # Entity stirbt
        
        # Fortpflanzungs-Cooldown aktualisieren
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
            
        return True
    
    def eat_food(self, food):
        """Entity isst Nahrung"""
        if self.digestion_cooldown > 0:
            return False  # Noch am Verdauen
            
        # Prüfen ob die Nahrung in den Mund passt
        if food.size > self.dna['mouth_size'] * 1.5:
            return False  # Nahrung zu groß
            
        # Nahrung verarbeiten
        processing_time = 1.0  # Basiszeit für Verdauung
        energy_efficiency = 1.0  # Basiseffizienz
        
        if self.dna['teeth_count'] > 0.5:  # Hat Zähne zum Zerkleinern
            # Zerkleinern dauert länger, gibt aber mehr Energie
            processing_time = 2.0
            energy_efficiency = 1.2
        else:
            # Verschlingen ist schneller, aber weniger effizient
            processing_time = 0.5
            energy_efficiency = 0.8
            
        # Verdauungszeit basierend auf Qualität und Größe
        digestion_time = processing_time * food.size * (0.8 + food.quality * 0.4)
        
        # Energie, die über Zeit freigesetzt wird
        total_energy = food.energy_value * energy_efficiency * self.dna['digestion_efficiency']
        
        # Zur Verdauungsliste hinzufügen
        self.digesting_food.append({
            'energy_per_tick': total_energy / (digestion_time * 60),  # Energie pro Tick
            'ticks_remaining': int(digestion_time * 60),  # Verdauungszeit in Ticks
            'quality': food.quality,
            'size': food.size,
            'waste_size': food.size * 0.3  # 30% der Größe wird zu Abfall
        })
        
        # Verdauungs-Cooldown setzen
        self.digestion_cooldown = 30  # Kurze Pause zwischen Mahlzeiten
        
        self.food_eaten += 1
        return True
    
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
        # Textur basierend auf aktuellem Zustand aktualisieren
        self.texture = self.renderer.render_creature(
            self.dna,
            health_percentage=self.health / self.max_health,
            energy_percentage=self.energy / self.max_energy
        )
        
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
        # Textur basierend auf aktuellem Zustand aktualisieren
        preview_texture = self.renderer.render_creature(
            self.dna,
            health_percentage=self.health / self.max_health,
            energy_percentage=self.energy / self.max_energy
        )
        
        # Skalierungsfaktor berechnen
        scale = min(
            (surface.get_width() - 20) / preview_texture.get_width(),
            (surface.get_height() - 20) / preview_texture.get_height()
        ) * 0.8  # 80% der verfügbaren Größe
        
        # Textur skalieren
        scaled_width = int(preview_texture.get_width() * scale)
        scaled_height = int(preview_texture.get_height() * scale)
        scaled_texture = pygame.transform.scale(preview_texture, (scaled_width, scaled_height))
        
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

    def get_waste_to_create(self):
        """Gibt eine Liste von (Größe, Qualität) Tupeln für zu erzeugenden Abfall zurück"""
        waste_list = []
        for food in self.digesting_food[:]:
            if food['ticks_remaining'] <= 0:
                waste_list.append((food['waste_size'], food['quality']))
                self.digesting_food.remove(food)
        return waste_list 

    def draw_highlight(self, surface):
        """Zeichnet einen Hervorhebungsring um die Entity"""
        pos = self.body.position
        pygame.draw.circle(surface, (0, 255, 255), 
                         (int(pos.x), int(pos.y)), 
                         int(self.radius + 2), 2) 