import pymunk
import pygame
import numpy as np
from PyLife.creature import Entity
from PyLife.creature_renderer import CreatureRenderer
from PyLife.world_food import Food
from PyLife.world_waste import Waste
from PyLife.creature_dna import DNA
from PyLife.neural_network import NeuralNetwork
import random

class Simulation:
    def __init__(self, width, height):
        """Initialisiert die Simulation"""
        self.width = width
        self.height = height
        
        self.entities = []
        self.food = []
        self.waste = []  # Liste für Abfall
        self.generation = 1
        self.time = 0
        self.population_size = 20  # Standardgröße der Population
        
        # Ausgewählte Entity
        self.selected_entity = None
        
        # Creature Renderer für die Entities
        self.creature_renderer = CreatureRenderer()
        
        # Zufallsgenerator für konsistente Ergebnisse
        self.rng = np.random.RandomState(42)
        
        # Physik-Engine Setup
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # Keine Schwerkraft in Top-Down
        
        # Wände erstellen
        self._create_walls()
        
        self.zoom = 1.0  # Zoom-Level
        self.camera_offset = (0, 0)  # Kamera-Offset für Panning
        
    def reset_camera(self):
        """Setzt die Kamera-Einstellungen auf die Standardwerte zurück"""
        self.zoom = 1.0
        self.camera_offset = [0, 0]

    def handle_click(self, pos, button=1):
        """Behandelt Mausklicks"""
        # Mittlere Maustaste (2) setzt die Kamera zurück
        if button == 2:  # Mausrad-Klick
            self.reset_camera()
            return
            
        # Mausposition an Zoom und Offset anpassen
        adjusted_x = (pos[0] - self.camera_offset[0]) / self.zoom
        adjusted_y = (pos[1] - self.camera_offset[1]) / self.zoom
        
        # Prüfe Kollision mit Entities
        for entity in self.entities:
            entity_pos = entity.body.position
            distance = ((adjusted_x - entity_pos.x) ** 2 + 
                       (adjusted_y - entity_pos.y) ** 2) ** 0.5
            
            if distance <= entity.radius:
                self.selected_entity = entity
                return
        
        # Wenn keine Entity getroffen wurde, Auswahl aufheben
        self.selected_entity = None
    
    def _create_walls(self):
        """Erstellt die Wände der Simulationsumgebung"""
        wall_thickness = 20
        walls = [
            [(0, 0), (self.width, 0)],  # Oben
            [(0, self.height), (self.width, self.height)],  # Unten
            [(0, 0), (0, self.height)],  # Links
            [(self.width, 0), (self.width, self.height)]  # Rechts
        ]
        
        for wall in walls:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (0, 0)
            shape = pymunk.Segment(body, wall[0], wall[1], wall_thickness)
            shape.friction = 0.7
            shape.elasticity = 0.5
            self.space.add(body, shape)
    
    def spawn_entity(self, x=None, y=None, dna=None):
        """Erstellt eine neue Entity an der angegebenen Position"""
        if x is None:
            x = np.random.uniform(0, self.width)
        if y is None:
            y = np.random.uniform(0, self.height)
            
        entity = Entity(self.space, x, y, dna, self)
        self.entities.append(entity)
    
    def spawn_food(self, x=None, y=None):
        """Spawnt Nahrung in der Umgebung"""
        if x is None:
            x = np.random.randint(20, self.width - 20)
        if y is None:
            y = np.random.randint(20, self.height - 20)
        
        food = Food(self.space, x, y)
        self.food.append(food)
    
    def spawn_waste(self, x, y, size, quality):
        """Spawnt Abfall in der Umgebung"""
        # Stelle sicher, dass die Position innerhalb der Grenzen ist
        x = max(20, min(self.width - 20, x))
        y = max(20, min(self.height - 20, y))
        
        waste = Waste(self.space, x, y, size, quality)
        self.waste.append(waste)
    
    def update(self, dt):
        """Aktualisiert die Simulation"""
        # Aktualisiere die Physik-Engine
        self.space.step(dt)
        
        # Aktualisiere alle Entities
        for entity in self.entities[:]:  # Kopie der Liste für sichere Iteration
            entity.update(dt)
            
            # Prüfe auf Nahrungsaufnahme
            for food in self.food[:]:  # Kopie der Liste für sichere Iteration
                if (entity.body.position - food.body.position).length < entity.radius + food.radius:
                    if entity.eat_food(food):
                        self.space.remove(food.body, food.shape)
                        self.food.remove(food)
            
            # Prüfe auf Waste-Generierung
            waste_list = entity.get_waste_to_create()
            for waste_size, waste_quality in waste_list:
                self.spawn_waste(entity.body.position.x, entity.body.position.y,
                               waste_size, waste_quality)
            
            # Entferne tote Entities
            if entity.health <= 0 or entity.energy <= 0:
                self.space.remove(entity.body, entity.shape)
                self.entities.remove(entity)
                continue
        
        # Aktualisiere Waste
        for waste in self.waste[:]:
            waste.update(dt)
            if waste.is_depleted():
                self.space.remove(waste.body, waste.shape)
                self.waste.remove(waste)
    
    def handle_zoom(self, zoom_value, mouse_pos):
        """Verarbeitet Zoom-Ereignisse"""
        old_zoom = self.zoom
        # Zoom-Wert anpassen (positiv = reinzoomen, negativ = rauszoomen)
        if zoom_value > 0:
            self.zoom = min(4.0, self.zoom * 1.1)
        else:
            self.zoom = max(0.25, self.zoom / 1.1)
            
        # Zoom um den Mauszeiger zentrieren
        if old_zoom != self.zoom:
            # Berechne die Differenz der Zoom-Level
            zoom_factor = self.zoom / old_zoom
            
            # Berechne den Offset basierend auf der Mausposition
            mouse_x, mouse_y = mouse_pos
            self.camera_offset = (
                mouse_x - (mouse_x - self.camera_offset[0]) * zoom_factor,
                mouse_y - (mouse_y - self.camera_offset[1]) * zoom_factor
            )

    def draw(self, surface, debug_mode=False):
        """Zeichnet die Simulation"""
        # Temporäre Surface für die Simulation erstellen
        temp_surface = pygame.Surface((self.width, self.height))
        temp_surface.fill((240, 240, 245))  # Hintergrundfarbe
        
        # Entities zeichnen
        for entity in self.entities:
            # Debug-Informationen nur für die ausgewählte Entity anzeigen (Performance-Optimierung)
            is_selected = entity == self.selected_entity
            entity.draw(temp_surface, debug_mode and is_selected)
        
        # Nahrung zeichnen
        for food in self.food:
            food.draw(temp_surface)
            
        # Abfall zeichnen
        for waste in self.waste:
            waste.draw(temp_surface)
            
        # Ausgewählte Entity hervorheben
        if self.selected_entity:
            self.selected_entity.draw_highlight(temp_surface)
        
        # Bei aktivem Debug-Modus Info anzeigen
        if debug_mode:
            small_font = pygame.font.Font(None, 20)
            debug_text = small_font.render("Debug Mode", True, (255, 50, 50))
            temp_surface.blit(debug_text, (10, 10))
        
        # Skalierte und verschobene Version auf die Hauptsurface zeichnen
        scaled_surface = pygame.transform.scale(temp_surface, 
                                             (int(self.width * self.zoom), 
                                              int(self.height * self.zoom)))
        surface.blit(scaled_surface, 
                    (self.camera_offset[0], self.camera_offset[1]))
    
    def next_generation(self) -> None:
        """Erstellt die nächste Generation von Kreaturen"""
        # Sortiere Kreaturen nach Fitness
        self.entities.sort(key=lambda x: x.fitness, reverse=True)
        
        # Behalte die besten 20% für die nächste Generation
        survivors_count = max(2, int(len(self.entities) * 0.2))
        survivors = self.entities[:survivors_count]
        
        # Erstelle neue Generation
        new_generation = []
        
        # Füge Überlebende hinzu
        new_generation.extend(survivors)
        
        # Fülle den Rest mit Nachkommen auf
        while len(new_generation) < self.population_size:
            # Wähle zufällige Eltern aus den Überlebenden
            parent = random.choice(survivors)
            
            # Erstelle Kind mit mutierter DNA
            child_dna = parent.dna.copy()
            mutation_rate = parent.dna['reproduction']['mutation_rate']  # Korrekte Kategorie
            child_dna.mutate(mutation_rate)
            
            # Erstelle neue Kreatur mit der mutierten DNA
            child = Entity(
                self.space,
                x=random.uniform(0, self.width),
                y=random.uniform(0, self.height),
                dna=child_dna,
                simulation=self
            )
            new_generation.append(child)
        
        # Aktualisiere die Population
        self.entities = new_generation
        self.generation += 1 