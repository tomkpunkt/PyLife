import pymunk
import pygame
import numpy as np
from entity import Entity
from creature_renderer import CreatureRenderer

class Simulation:
    def __init__(self, width, height):
        """Initialisiert die Simulation"""
        self.width = width
        self.height = height
        
        self.entities = []
        self.food = []
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
        
    def handle_click(self, pos):
        """Behandelt Mausklicks und selektiert Entities"""
        # Prüfen ob eine Entity angeklickt wurde
        clicked_entity = None
        for entity in self.entities:
            # Distanz zwischen Klickposition und Entity berechnen
            dx = entity.body.position.x - pos[0]
            dy = entity.body.position.y - pos[1]
            distance = np.sqrt(dx*dx + dy*dy)
            
            # Wenn Klick innerhalb des Entity-Radius
            if distance <= entity.radius:
                clicked_entity = entity
                break
        
        # Wenn eine Entity gefunden wurde
        if clicked_entity:
            if self.selected_entity == clicked_entity:
                # Gleiche Entity nochmal geklickt -> Auswahl aufheben
                self.selected_entity = None
            else:
                # Neue Entity ausgewählt
                self.selected_entity = clicked_entity
        else:
            # Klick außerhalb -> Auswahl aufheben
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
        """Spawnt eine neue Entity"""
        if x is None:
            x = np.random.randint(50, self.width - 50)
        if y is None:
            y = np.random.randint(50, self.height - 50)
            
        entity = Entity(self.space, x, y, dna)
        self.entities.append(entity)
    
    def spawn_food(self, x=None, y=None):
        """Spawnt Nahrung in der Umgebung"""
        if x is None:
            x = np.random.randint(20, self.width - 20)
        if y is None:
            y = np.random.randint(20, self.height - 20)
            
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (x, y)
        shape = pymunk.Circle(body, 5)
        shape.sensor = True  # Macht die Nahrung zu einem Sensor
        self.space.add(body, shape)
        self.food.append((body, shape))
    
    def update(self, dt):
        """Aktualisiert die Simulation"""
        # Physik-Engine aktualisieren
        self.space.step(dt)
        
        # Entities aktualisieren
        for entity in self.entities[:]:
            if not entity.update(dt):
                self.entities.remove(entity)
                self.space.remove(entity.body, entity.shape)
                if entity == self.selected_entity:
                    self.selected_entity = None
        
        # Kollisionserkennung zwischen Entities und Nahrung
        for entity in self.entities:
            for food_body, food_shape in self.food[:]:
                if self._check_collision(entity.shape, food_shape):
                    # Entity bekommt Energie
                    entity.eat_food(20)
                    # Nahrung entfernen
                    self.space.remove(food_body, food_shape)
                    self.food.remove((food_body, food_shape))
                    # Neue Nahrung spawnen
                    self.spawn_food()
    
    def _check_collision(self, shape1, shape2):
        """Überprüft Kollision zwischen zwei Shapes"""
        return shape1.shapes_collide(shape2).points
    
    def draw(self, surface):
        """Zeichnet die Simulation auf die angegebene Surface"""
        # Nahrung zeichnen
        for food_body, _ in self.food:
            pos = food_body.position
            pygame.draw.circle(surface, (255, 0, 0), 
                             (int(pos.x), int(pos.y)), 5)
        
        # Entities zeichnen
        for entity in self.entities:
            entity.draw(surface)
            # Ausgewählte Entity hervorheben
            if entity == self.selected_entity:
                pos = entity.body.position
                pygame.draw.circle(surface, (0, 255, 255), 
                                 (int(pos.x), int(pos.y)), 
                                 int(entity.radius + 2), 2)
    
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