import pymunk
import pygame
import numpy as np
from PyLife.neural_network import NeuralNetwork
from PyLife.brain import Brain
from PyLife.creature_dna import DNA
from PyLife.creature_renderer import CreatureRenderer
import random
import math

class Entity:
    # Statischer CreatureRenderer für alle Entities
    renderer = CreatureRenderer()
    
    def __init__(self, space, x, y, dna=None, simulation=None):
        """Initialisiert eine neue Entity"""
        self.space = space
        self.simulation = simulation  # Referenz zur Simulation hinzugefügt
        
        # DNA initialisieren oder kopieren
        if dna is None:
            self.dna = DNA()
        else:
            self.dna = dna
        
        # Physikalische Eigenschaften
        base_radius = 15
        self.radius = base_radius * (0.75 + 0.5 * self.dna['physical']['size'])  # ±25% Varianz vom Base-Radius
        self.mass = self.radius * 2
        
        # Pymunk-Körper erstellen
        self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius))
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = 0.7
        self.shape.elasticity = 0.5
        self.space.add(self.body, self.shape)
        
        # Renderer für die Vorschau
        self.renderer = CreatureRenderer()
        
        # Neuronales Netzwerk initialisieren
        self.brain = Brain(input_size=8, hidden_size=16, output_size=2)  # 8 Inputs, 16 versteckte Neuronen, 2 Outputs
        
        # Basis-Eigenschaften
        self.base_speed = 100 * self.dna['movement']['movement_forward_organ_size']  # Geschwindigkeit basierend auf DNA
        self.max_health = 100 * self.dna['physical']['health']
        self.max_energy = 100 * self.dna['feeding']['metabolism']
        self.max_hunger = 100
        
        # Aktuelle Werte
        self.health = self.max_health
        self.energy = self.max_energy
        self.hunger = 0
        self.age = 0
        self.food_eaten = 0
        self.children = 0
        self.distance_traveled = 0
        
        # Verdauungssystem
        self.digesting_food = []
        self.digestion_rate = 0.1 * self.dna['feeding']['metabolism']  # Verdauungsrate basierend auf DNA
        
        # Fortpflanzung
        self.reproduction_cost = 50  # Energiekosten für Fortpflanzung
        self.reproduction_cooldown = 0  # Abklingzeit für Fortpflanzung
        
        # Sensoren
        self.sensor_range = 150 * self.dna['sensors']['sensor_range']  # Sensorreichweite basierend auf DNA
        
        # Bewegung
        self.movement_target = None
        self.last_position = self.body.position
        
        # Zufallsgenerator für konsistente Ergebnisse
        self.rng = np.random.RandomState()
        
        # Wende die DNA an (initialisiert max_health, max_energy, etc.)
        self._apply_dna()
        
        # Initialisiere Grundwerte
        self.energy = self.max_energy * 0.8  # Starte mit 80% Energie
        self.health = min(self.max_health, 100)  # Starte mit maximal 100 Gesundheit
        self.hunger = 0
        self.max_hunger = 100
        self.age = 0
        self.food_eaten = 0
        self.children = 0
        self.distance_traveled = 0
        self.digesting_food = []
        
        # Status-Variablen
        self.reproduction_cooldown = 0
        self.digestion_cooldown = 0
        self.movement_timer = 0
        self.direction_change_time = np.random.uniform(1, 3)  # Zeit bis zur Richtungsänderung
        self.current_direction = np.random.uniform(-1, 1)  # Aktuelle Drehrichtung
        
        # Kreatur-Textur erstellen
        self.texture = self.renderer.render_creature(self.dna.to_dict())
        self.texture_rect = self.texture.get_rect()
    
    def _generate_dna(self):
        """Generiert zufällige DNA"""
        return {
            'size': random.uniform(0.0, 1.0),
            'speed': random.uniform(0.0, 1.0),
            'sense_range': random.uniform(0.0, 1.0),
            'mouth_size': random.uniform(0.0, 1.0),
            'digestion': random.uniform(0.0, 1.0),
            'metabolism': random.uniform(0.0, 1.0),
            'mutation_rate': random.uniform(0.0, 1.0),
            'aggression': random.uniform(0.0, 1.0),
            'reproduction': random.uniform(0.0, 1.0),
            'health': random.uniform(0.0, 1.0),
            # Neue DNA-Werte für den CreatureRenderer
            'eye_count': random.uniform(0.0, 1.0),
            'sensor_range': random.uniform(0.0, 1.0),
            'spike_factor': random.uniform(0.0, 1.0),
            'spike_length': random.uniform(0.0, 1.0),
            'movement_organ_count': random.uniform(0.0, 1.0),
            'movement_organ_size': random.uniform(0.0, 1.0),
            'energy_efficiency': random.uniform(0.0, 1.0)
        }
    
    def _apply_dna(self):
        """Wendet die DNA-Werte auf die Entity an"""
        # Basis-Eigenschaften
        self.base_speed = 100 + self.dna['movement']['movement_forward_organ_size'] * 150  # Basis-Geschwindigkeit
        self.max_health = 100 + self.dna['physical']['health'] * 100  # Maximale Gesundheit
        self.max_energy = 100 + self.dna['feeding']['metabolism'] * 100  # Maximale Energie
        
        # Aktuelle Werte auf Maximum setzen
        self.health = self.max_health
        self.energy = self.max_energy
        self.hunger = 0
        
        # Verdauungssystem
        self.digestion_rate = 0.1 + self.dna['feeding']['metabolism'] * 0.2  # Verdauungsrate
        
        # Sensoren
        self.sensor_range = 150 + self.dna['sensors']['sensor_range'] * 100  # Sensorreichweite
        
        # Fortpflanzung
        self.reproduction_cost = 50 + self.dna['reproduction']['reproduction'] * 25  # Energiekosten für Fortpflanzung
        
        # Status zurücksetzen
        self.age = 0
        self.food_eaten = 0
        self.children = 0
        self.distance_traveled = 0
        self.digesting_food = []
        
        # Renderer für die Vorschau
        self.renderer = CreatureRenderer()
        
        # Neuronales Netzwerk initialisieren
        self.brain = Brain(input_size=8, hidden_size=16, output_size=2)  # 8 Inputs, 16 versteckte Neuronen, 2 Outputs
        
        # Sinne und Interaktion
        self.turn_rate = 2.0 + self.dna['movement']['movement_forward_organ_size'] * 2.0  # Wendegeschwindigkeit
        self.mouth_size = 5 + self.dna['feeding']['mouth_size'] * 15  # Mundgröße
        
        # Stoffwechsel und Verdauung
        self.digestion_efficiency = 0.3 + self.dna['feeding']['digestion'] * 0.7  # Verdauungseffizienz
        self.metabolism_rate = 0.3 + self.dna['feeding']['metabolism'] * 0.7  # Stoffwechselrate
        
        # Verhalten
        self.aggression = self.dna['offense']['aggression']  # Aggressivität
        self.reproduction_rate = self.dna['reproduction']['reproduction']  # Reproduktionsrate
        
        # Größe und Masse neu berechnen
        base_radius = 20
        size_factor = self.dna['physical']['size']
        self.radius = base_radius * (0.75 + 0.5 * size_factor)  # ±25% Varianz vom Base-Radius
        self.mass = self.radius * (0.4 + 0.2 * size_factor)  # Masse proportional zur Größe
        
        # Physikalischen Körper aktualisieren
        if hasattr(self, 'body'):
            self.body.mass = self.mass
            # Trägheitsmoment aktualisieren
            self.body.moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        
        # Verdauungssystem aktualisieren
        self.digestion_cooldown = max(10, 30 - self.dna['feeding']['digestion'] * 20)
        
        # Fortpflanzung
        self.reproduction_cooldown = max(20, 60 - self.dna['reproduction']['reproduction'] * 40)
        self.reproduction_cost = 20 + self.dna['physical']['size'] * 20  # Größere Kreaturen brauchen mehr Energie
        
        # Kreatur-Textur aktualisieren
        self.texture = self.renderer.render_creature(self.dna.to_dict())
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
        inputs[7] = min(1, velocity / self.base_speed) * 2 - 1  # Normalisierte Geschwindigkeit
        
        return inputs.reshape(1, -1)  # Reshape für das neuronale Netz
    
    def apply_brain_outputs(self, outputs):
        """Wendet die Ausgaben des neuronalen Netzes an"""
        # Ausgaben sind:
        # 1. Bewegungsrichtung (-1 bis 1, wird zu Winkel -pi bis pi)
        # 2. Geschwindigkeit (0 bis 1, wird mit max_speed multipliziert)
        
        direction = outputs[0, 0] * np.pi  # Umwandlung in Winkel
        speed = (outputs[0, 1] + 1) / 2 * self.base_speed  # Umwandlung in Geschwindigkeit
        
        # Bewegungsvektor berechnen
        force_x = np.cos(direction) * speed
        force_y = np.sin(direction) * speed
        
        # Kraft auf die Entity anwenden
        self.body.apply_force_at_local_point((force_x, force_y), (0, 0))
    
    def update(self, dt):
        """Aktualisiert den Zustand der Entity"""
        # Alter erhöhen
        self.age += dt
        
        # Position für Bewegungsberechnung speichern
        old_position = self.body.position
        
        # Neuronales Netzwerk aktualisieren
        self._update_brain(dt)
        
        # Bewegung basierend auf Netzwerk-Output
        self._apply_movement(dt)
        
        # Zurückgelegte Distanz berechnen
        self.distance_traveled += (self.body.position - old_position).length
        
        # Energie und Gesundheit aktualisieren
        self._update_energy(dt)
        self._update_health(dt)
        
        # Verdauungssystem aktualisieren
        self._update_digestion(dt)
        
        # Hormone aktualisieren
        self._update_hormones(dt)
        
        # Cooldowns reduzieren
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= dt
    
    def eat_food(self, food):
        """Versucht Nahrung zu essen"""
        if food.size <= self.mouth_size:
            self.digesting_food.append({
                'food': {
                    'size': food.size,
                    'quality': food.quality,
                    'energy': food.energy_value
                },
                'ticks_remaining': int(food.size * 60)  # Größere Nahrung braucht länger
            })
            return True
        return False
    
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
    
    def draw(self, screen, debug_mode=False):
        """Zeichnet die Entity auf den Bildschirm"""
        # Textur basierend auf aktuellem Zustand aktualisieren
        self.texture = self.renderer.render_creature(
            self.dna.to_dict(),
            health_percentage=self.health / self.max_health,
            energy_percentage=self.energy / self.max_energy
        )
        
        # Position aus der Physik-Engine holen
        pos = self.body.position
        angle = self.body.angle
        
        # Debug-Informationen zuerst zeichnen (unter der Kreatur)
        if debug_mode:
            # Sensor-Reichweite (kompletter Kreis)
            pygame.draw.circle(
                screen, 
                (100, 100, 255),  # Hellblau
                (int(pos.x), int(pos.y)), 
                int(self.sensor_range),
                1  # Nur Umriss
            )
            
            # Visuelle Reichweite (etwas kleiner als Sensor-Reichweite)
            visual_range = self.sensor_range * 0.8
            pygame.draw.circle(
                screen, 
                (100, 255, 100),  # Hellgrün
                (int(pos.x), int(pos.y)), 
                int(visual_range),
                1  # Nur Umriss
            )
            
            # Visueller Kegel (Sichtbereich)
            cone_angle = np.pi / 2  # 90 Grad Sichtwinkel
            cone_start = angle - cone_angle / 2
            cone_end = angle + cone_angle / 2
            
            # Punkte für den Kreisausschnitt (Sichtkegel)
            arc_points = [(pos.x, pos.y)]  # Startpunkt im Zentrum
            
            # Anzahl der Punkte für den Bogen
            num_points = 20
            for i in range(num_points + 1):
                # Winkel zwischen cone_start und cone_end
                current_angle = cone_start + (cone_end - cone_start) * (i / num_points)
                x = pos.x + np.cos(current_angle) * visual_range
                y = pos.y + np.sin(current_angle) * visual_range
                arc_points.append((x, y))
            
            arc_points.append((pos.x, pos.y))  # Zurück zum Zentrum
            
            # Zeichne den gefüllten Sichtkegel mit Transparenz
            if len(arc_points) > 2:
                # Für Transparenz: Erstelle eine temporäre Surface
                temp_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                pygame.draw.polygon(
                    temp_surface,
                    (255, 255, 0, 30),  # Gelb, sehr transparent
                    arc_points
                )
                screen.blit(temp_surface, (0, 0))
                
            # Linien zur Visualisierung der Sichtkegelgrenzen
            pygame.draw.line(
                screen,
                (255, 150, 0),  # Orange
                (pos.x, pos.y),
                (pos.x + np.cos(cone_start) * visual_range, pos.y + np.sin(cone_start) * visual_range),
                1
            )
            pygame.draw.line(
                screen,
                (255, 150, 0),  # Orange
                (pos.x, pos.y),
                (pos.x + np.cos(cone_end) * visual_range, pos.y + np.sin(cone_end) * visual_range),
                1
            )
            
            # Blickrichtung
            direction_length = visual_range * 0.4
            pygame.draw.line(
                screen,
                (255, 0, 0),  # Rot
                (pos.x, pos.y),
                (pos.x + np.cos(angle) * direction_length, pos.y + np.sin(angle) * direction_length),
                2
            )
        
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

        # Debug-Informationen anzeigen (über der Kreatur)
        if debug_mode:
            small_font = pygame.font.Font(None, 14)
            
            # ID anzeigen
            id_text = small_font.render(f"#{id(self) % 1000}", True, (0, 0, 0))
            screen.blit(id_text, (pos[0], pos[1] - 30))
            
            # Neuronale Netzwerk-Outputs visualisieren
            if hasattr(self, 'brain_output'):
                # Bewegungswerte visualisieren
                forward = self.brain_output[0][0]  # Vorwärts/Rückwärts (-1 bis 1)
                turn = self.brain_output[0][1]     # Links/Rechts (-1 bis 1)
                
                # Pfeillänge
                arrow_length = self.radius * 1.5
                
                # Basisposition für den Pfeil
                arrow_base_x = pos[0] + rotated_rect.width/2
                arrow_base_y = pos[1] + rotated_rect.height/2
                
                # Zielposition des Pfeils
                target_angle = angle + turn * 0.5  # Aktuelle Richtung + Drehung
                arrow_tip_x = arrow_base_x + np.cos(target_angle) * arrow_length * forward
                arrow_tip_y = arrow_base_y + np.sin(target_angle) * arrow_length * forward
                
                # Pfeil zeichnen
                pygame.draw.line(screen, (250, 100, 100), 
                               (arrow_base_x, arrow_base_y), 
                               (arrow_tip_x, arrow_tip_y), 2)
                
                # Pfeilspitze
                head_size = 5
                pygame.draw.circle(screen, (250, 100, 100), 
                                (int(arrow_tip_x), int(arrow_tip_y)), 
                                head_size)
                
                # Kraft anzeigen
                force_text = small_font.render(f"F:{forward:.1f} T:{turn:.1f}", True, (0, 0, 0))
                screen.blit(force_text, (pos[0], pos[1] + rotated_rect.height + 2))

    def draw_preview(self, surface, debug_mode=False):
        """Zeichnet eine große Vorschau der Entity"""
        # Textur basierend auf aktuellem Zustand aktualisieren
        preview_texture = self.renderer.render_creature(
            self.dna.to_dict(),
            health_percentage=self.health / self.max_health,
            energy_percentage=self.energy / self.max_energy
        )
        
        # Hintergrund füllen
        surface.fill((240, 240, 245))  # Hellgrauer Hintergrund
        
        # Skalierungsfaktor berechnen - nutze mehr vom verfügbaren Platz
        scale = min(
            (surface.get_width() * 0.8) / preview_texture.get_width(),
            (surface.get_height() * 0.8) / preview_texture.get_height()
        )
        
        # Textur skalieren
        scaled_width = int(preview_texture.get_width() * scale)
        scaled_height = int(preview_texture.get_height() * scale)
        scaled_texture = pygame.transform.scale(preview_texture, (scaled_width, scaled_height))
        
        # Position für die Kreatur (zentriert)
        creature_x = (surface.get_width() - scaled_width) // 2
        creature_y = (surface.get_height() - scaled_height) // 2
        
        # Textur zeichnen
        surface.blit(scaled_texture, (creature_x, creature_y))
        
        # Schriftart für die Überschrift
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 18)
        
        # Name/ID der Kreatur oben anzeigen
        title = font.render(f"Kreatur #{id(self) % 1000}", True, (0, 0, 0))
        title_rect = title.get_rect(center=(surface.get_width()//2, 15))
        surface.blit(title, title_rect)
        
        # Debug-Informationen anzeigen
        if debug_mode:
            # Debug-Überschrift
            debug_title = font.render("Debug Info", True, (180, 30, 30))
            surface.blit(debug_title, (10, creature_y + scaled_height + 10))
            
            # Neuronale Netz-Visualisierung
            if hasattr(self, 'brain'):
                # Größeres Rechteck für das neuronale Netzwerk
                nn_rect = pygame.Rect(
                    surface.get_width() - 200,  # Weiter links
                    creature_y + scaled_height + 10,
                    180,  # Breiter
                    160   # Höher
                )
                
                # Weißer Hintergrund mit Rahmen
                pygame.draw.rect(surface, (255, 255, 255), nn_rect)
                pygame.draw.rect(surface, (180, 180, 200), nn_rect, 1)
                
                # Überschrift für das neuronale Netz
                nn_title = small_font.render("Neural Network", True, (50, 50, 70))
                surface.blit(nn_title, (nn_rect.centerx - nn_title.get_width()//2, nn_rect.y + 5))
                
                # Kompakte Version des Netzwerks zeichnen
                network_rect = pygame.Rect(
                    nn_rect.x + 10,
                    nn_rect.y + 25,
                    nn_rect.width - 20,
                    nn_rect.height - 35
                )
                self.brain.draw_compact(surface, network_rect)
                
                # Ausgabewerte des Netzwerks anzeigen
                if hasattr(self, 'brain_output'):
                    forward = self.brain_output[0][0]
                    turn = self.brain_output[0][1]
                    output_text = small_font.render(
                        f"Forward: {forward:+.2f}  Turn: {turn:+.2f}",
                        True, (50, 50, 70)
                    )
                    surface.blit(output_text, (nn_rect.x + 10, nn_rect.bottom - 20))
            
            # Statistiken anzeigen
            stats_y = creature_y + scaled_height + 35
            stats = [
                f"Gesundheit: {self.health:.1f}/{self.max_health:.1f}",
                f"Energie: {self.energy:.1f}/{self.max_energy:.1f}",
                f"Hunger: {self.hunger:.1f}/{self.max_hunger:.1f}",
                f"Alter: {self.age:.1f}",
                f"Nahrung: {self.food_eaten}",
                f"Nachkommen: {self.children}",
                f"Fitness: {self.fitness:.2f}"
            ]
            
            for stat in stats:
                text = small_font.render(stat, True, (50, 50, 70))
                surface.blit(text, (15, stats_y))
                stats_y += 20

    def get_waste_to_create(self):
        """Gibt eine Liste von (Größe, Qualität) Tupeln für zu erzeugenden Abfall zurück"""
        waste_list = []
        for food in self.digesting_food[:]:
            if food['ticks_remaining'] <= 0:
                waste_list.append((food['food']['size'], food['food']['quality']))
                self.digesting_food.remove(food)
        return waste_list 

    def draw_highlight(self, surface):
        """Zeichnet einen Hervorhebungsring um die Entity"""
        pos = self.body.position
        pygame.draw.circle(surface, (0, 255, 255), 
                         (int(pos.x), int(pos.y)), 
                         int(self.radius + 2), 2) 

    def _update_brain(self, dt):
        """Aktualisiert das neuronale Netzwerk"""
        # Eingabewerte vorbereiten
        inputs = np.array([
            self.energy / self.max_energy,  # Energielevel
            self.health / self.max_health,  # Gesundheitslevel
            self.hunger / self.max_hunger,  # Hungerlevel
            len(self.digesting_food) / 5,  # Verdauungsaktivität
            self.reproduction_cooldown / 60,  # Fortpflanzungsbereitschaft
            self.age / 1000,  # Alter
            self.aggression,  # Aggressivität
            self.reproduction_rate  # Reproduktionsrate
        ]).reshape(1, -1)
        
        # Netzwerk ausführen
        self.brain_output = self.brain.forward(inputs)
    
    def _apply_movement(self, dt):
        """Wendet die vom Gehirn berechnete Bewegung an"""
        # Bewegungsrichtung aus Netzwerk-Output
        forward = self.brain_output[0][0]  # Vorwärts/Rückwärts (-1 bis 1)
        turn = self.brain_output[0][1]     # Links/Rechts (-1 bis 1)
        
        # Aktuelle Richtung und Position
        angle = self.body.angle
        position = self.body.position
        
        # Geschwindigkeit basierend auf Energie und DNA
        speed = self.base_speed * (self.energy / self.max_energy)
        
        # Neue Position berechnen
        dx = np.cos(angle) * forward * speed * dt
        dy = np.sin(angle) * forward * speed * dt
        
        # Position aktualisieren
        self.body.position = (position.x + dx, position.y + dy)
        
        # Drehung anwenden
        self.body.angle += turn * self.turn_rate * dt
    
    def _update_energy(self, dt):
        """Aktualisiert den Energiehaushalt"""
        # Basisverbrauch basierend auf Körpergröße
        base_consumption = 0.08 * dt * self.dna['physical']['size']
        
        # Aktivitätsbasierter Verbrauch
        velocity = np.linalg.norm(self.body.velocity)
        velocity_factor = velocity / self.base_speed
        movement_consumption = 0.1 * dt * velocity_factor * self.dna['physical']['size']
        
        # Verdauungsenergie
        digestion_consumption = len(self.digesting_food) * 0.02 * dt
        
        # Hungermodifikator
        hunger_factor = 1.0 + (self.hunger / self.max_hunger)
        
        # Gesamtverbrauch
        total_consumption = (base_consumption + movement_consumption + digestion_consumption) * hunger_factor
        
        # Energie reduzieren
        self.energy = max(0, self.energy - total_consumption)
        
        # Hunger erhöhen
        hunger_increase = (0.15 * dt * self.dna['physical']['size'] +  # Basisanstieg
                         0.225 * dt * velocity_factor)                 # Bewegungsabhängiger Anstieg
        self.hunger = min(self.max_hunger, self.hunger + hunger_increase)
    
    def _update_health(self, dt):
        """Aktualisiert den Gesundheitszustand"""
        if self.energy <= 0:
            # Gesundheit nimmt ab wenn keine Energie vorhanden
            self.health -= 0.5 * dt
            self.health = max(0, self.health)
    
    def _update_digestion(self, dt):
        """Aktualisiert das Verdauungssystem"""
        waste_to_create = []
        
        # Verdauung verarbeiten
        for food in self.digesting_food[:]:
            if food['ticks_remaining'] > 0:
                # Energie aus der Verdauung gewinnen
                energy_gain = food['food']['energy'] * self.digestion_efficiency * dt
                self.energy = min(self.max_energy, self.energy + energy_gain)
                
                # Hunger reduzieren
                hunger_reduction = energy_gain * 0.5
                self.hunger = max(0, self.hunger - hunger_reduction)
                
                # Verbleibende Zeit reduzieren
                food['ticks_remaining'] -= dt
            else:
                # Verdauung abgeschlossen, Abfall erzeugen
                waste_size = food['food']['size'] * (1 - self.digestion_efficiency)
                waste_quality = food['food']['quality'] * 0.5
                waste_to_create.append((waste_size, waste_quality))
                self.digesting_food.remove(food)
        
        return waste_to_create
    
    def get_nearby_entities(self):
        """Findet alle Entities in Sensorreichweite"""
        if not self.simulation:
            return []
            
        nearby = []
        for entity in self.simulation.entities:
            if entity != self:
                distance = (entity.body.position - self.body.position).length
                if distance <= self.sensor_range:
                    nearby.append(entity)
        return nearby
    
    def _update_hormones(self, dt):
        """Aktualisiert die Hormoneffekte"""
        # Adrenalin (bei niedriger Gesundheit)
        if self.health < self.max_health * 0.3:
            self.base_speed *= (1 + self.dna['physical']['adrenaline'] * 0.5)
            self.sensor_range *= (1 + self.dna['sensors']['sensor_range'] * 0.3)
        
        # Testosteron (bei hoher Energie)
        if self.energy > self.max_energy * 0.7:
            self.aggression *= (1 + self.dna['offense']['aggression'] * 0.4)
        
        # Insulin (bei hohem Hunger)
        if self.hunger > self.max_hunger * 0.7:
            self.digestion_efficiency *= (1 + self.dna['feeding']['digestion'] * 0.3)
        
        # Melatonin (bei niedriger Energie)
        if self.energy < self.max_energy * 0.3:
            self.metabolism_rate *= (1 - self.dna['feeding']['metabolism'] * 0.2)
        
        # Oxytocin (in Gruppen)
        if len(self.get_nearby_entities()) > 2:
            self.aggression *= (1 - self.dna['offense']['aggression'] * 0.3)
            self.reproduction_rate *= (1 + self.dna['reproduction']['reproduction'] * 0.2)

    @property
    def fitness(self) -> float:
        """Berechnet die Fitness der Kreatur basierend auf verschiedenen Faktoren"""
        # Basis-Fitness
        base_fitness = 1.0
        
        # Gesundheit und Energie (0-1 normalisiert)
        health_factor = self.health / self.max_health
        energy_factor = self.energy / self.max_energy
        
        # Alter und Erfahrung
        age_factor = min(1.0, self.age / 100.0)  # Normalisiert auf 100 Zeiteinheiten
        food_factor = min(1.0, self.food_eaten / 10.0)  # Normalisiert auf 10 Nahrungseinheiten
        
        # Bewegung und Aktivität
        movement_factor = min(1.0, self.distance_traveled / 1000.0)  # Normalisiert auf 1000 Einheiten
        
        # Fortpflanzung
        reproduction_factor = min(1.0, self.children / 3.0)  # Normalisiert auf 3 Nachkommen
        
        # Gewichtung der Faktoren
        weights = {
            'health': 1.5,    # Gesundheit ist sehr wichtig
            'energy': 1.2,    # Energie ist wichtig
            'age': 0.8,      # Alter zeigt Überlebensfähigkeit
            'food': 1.0,     # Nahrungsaufnahme ist wichtig
            'movement': 0.5,  # Bewegung zeigt Aktivität
            'reproduction': 1.3  # Fortpflanzung ist wichtig für Evolution
        }
        
        # Gewichtete Summe aller Faktoren
        fitness = base_fitness + (
            health_factor * weights['health'] +
            energy_factor * weights['energy'] +
            age_factor * weights['age'] +
            food_factor * weights['food'] +
            movement_factor * weights['movement'] +
            reproduction_factor * weights['reproduction']
        )
        
        return max(0.0, fitness)  # Fitness kann nicht negativ sein