import pymunk
import pygame
import numpy as np
from entity import Entity
from creature_renderer import CreatureRenderer
from food import Food
from waste import Waste

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
            
        entity = Entity(self.space, x, y, dna)
        entity.simulation = self  # Referenz zur Simulation hinzufügen
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
        # Welt aktualisieren
        self.space.step(dt)
        
        # Entities aktualisieren
        for entity in self.entities[:]:  # Kopie der Liste für sicheres Entfernen
            if not entity.update(dt):
                # Entity ist gestorben, entferne sie
                self.space.remove(entity.body, entity.shape)
                self.entities.remove(entity)
                if self.selected_entity == entity:
                    self.selected_entity = None
        
        # Kollisionen zwischen Entities und Nahrung prüfen
        for entity in self.entities:
            for food in self.food[:]:  # Kopie der Liste für sicheres Entfernen
                if self._check_collision(entity.shape, food.shape):
                    if entity.eat_food(food):
                        self.space.remove(food.body, food.shape)
                        self.food.remove(food)
                        # Spawne neue Nahrung
                        self.spawn_food()
        
        # Abfall aktualisieren
        for waste in self.waste[:]:
            if not waste.update(dt):
                self.waste.remove(waste)
                self.space.remove(waste.body, waste.shape)
    
    def _check_collision(self, shape1, shape2):
        """Überprüft Kollision zwischen zwei Shapes"""
        return shape1.shapes_collide(shape2).points
    
    def handle_zoom(self, zoom_delta, mouse_pos):
        """Verarbeitet Zoom-Eingaben vom Mausrad"""
        # Zoom-Level anpassen (min: 0.1, max: 3.0)
        old_zoom = self.zoom
        self.zoom = max(0.1, min(3.0, self.zoom + zoom_delta * 0.1))
        
        # Wenn Zoom-Level sich geändert hat
        if self.zoom != old_zoom:
            # Mausposition relativ zum Kamera-Offset berechnen
            rel_x = (mouse_pos[0] - self.camera_offset[0]) / old_zoom
            rel_y = (mouse_pos[1] - self.camera_offset[1]) / old_zoom
            
            # Neuen Kamera-Offset berechnen, damit der Zoom um den Mauszeiger herum erfolgt
            self.camera_offset = (
                mouse_pos[0] - rel_x * self.zoom,
                mouse_pos[1] - rel_y * self.zoom
            )

    def draw(self, surface):
        """Zeichnet die Simulation"""
        # Temporäre Surface für die Simulation erstellen
        temp_surface = pygame.Surface((self.width, self.height))
        temp_surface.fill((240, 240, 245))  # Hintergrundfarbe
        
        # Entities zeichnen
        for entity in self.entities:
            entity.draw(temp_surface)
        
        # Nahrung zeichnen
        for food in self.food:
            food.draw(temp_surface)
        
        # Abfall zeichnen
        for waste in self.waste:
            waste.draw(temp_surface)
        
        # Ausgewählte Entity hervorheben
        if self.selected_entity:
            self.selected_entity.draw_highlight(temp_surface)
        
        # Skalierte und verschobene Version auf die Hauptsurface zeichnen
        scaled_surface = pygame.transform.scale(temp_surface, 
                                             (int(self.width * self.zoom), 
                                              int(self.height * self.zoom)))
        surface.blit(scaled_surface, 
                    (self.camera_offset[0], self.camera_offset[1]))
    
    def next_generation(self):
        """Erstellt die nächste Generation"""
        # Beste Entities auswählen
        survivors = sorted(self.entities, 
                         key=lambda x: x.energy + x.health, 
                         reverse=True)[:5]
        
        # Alle Entities entfernen
        for entity in self.entities:
            self.space.remove(entity.body, entity.shape)
        self.entities.clear()
        
        # Neue Generation erstellen
        for _ in range(20):  # 20 neue Entities
            if survivors:
                # Zufälligen Überlebenden auswählen
                parent = np.random.choice(survivors)
                # Neue Entity mit mutierter DNA erstellen
                mutated_dna = {
                    k: v * np.random.uniform(0.9, 1.1)
                    for k, v in parent.dna.items()
                }
                self.spawn_entity(dna=mutated_dna)
            else:
                # Wenn keine Überlebenden, zufällige Entity erstellen
                self.spawn_entity()
        
        self.generation += 1 