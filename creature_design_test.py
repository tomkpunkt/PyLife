import pygame
import sys
from PyLife.creature_dna import DNA
from PyLife.creature import Entity
import numpy as np
import pymunk

class Slider:
    def __init__(self, x, y, width, height, min_val=0.0, max_val=1.0, initial_val=0.5, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.bar_rect = pygame.Rect(x, y + height//3, width, height//3)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.active = False
        self.handle_radius = height//2
        
    def draw(self, screen):
        # Zeichne Slider-Balken
        pygame.draw.rect(screen, (60, 60, 60), self.bar_rect)
        
        # Zeichne Slider-Handle
        handle_x = self.rect.x + (self.rect.width - self.handle_radius*2) * ((self.value - self.min_val) / (self.max_val - self.min_val))
        handle_pos = (int(handle_x + self.handle_radius), self.rect.centery)
        pygame.draw.circle(screen, (120, 120, 120), handle_pos, self.handle_radius)
        
        # Zeichne Label und Wert
        font = pygame.font.Font(None, 24)
        label_surface = font.render(f"{self.label}: {self.value:.2f}", True, (200, 200, 200))
        screen.blit(label_surface, (self.rect.x, self.rect.y - 20))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False
            
        elif event.type == pygame.MOUSEMOTION and self.active:
            relative_x = min(max(event.pos[0] - self.rect.x, 0), self.rect.width)
            self.value = self.min_val + (self.max_val - self.min_val) * (relative_x / self.rect.width)
            self.value = min(max(self.value, self.min_val), self.max_val)

class CreatureDesignTest:
    def __init__(self, width=1024, height=768):
        """Initialisiert das Testfenster"""
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Creature Design Test")
        
        self.clock = pygame.time.Clock()
        
        # Zoom und Position
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = None
        
        # Slider erstellen
        self.sliders = {
            'zoom': Slider(20, height - 300, 200, 20, 0.5, 5.0, 1.0, "Zoom"),
            'eye_size': Slider(20, height - 260, 200, 20, 0.0, 1.0, 0.8, "Eye Size"),
            'mouth_size': Slider(20, height - 220, 200, 20, 0.0, 1.0, 0.5, "Mouth Size"),
            'mouth_teeth': Slider(20, height - 180, 200, 20, 0.0, 1.0, 0.5, "Teeth Size"),
            'forward_size': Slider(20, height - 140, 200, 20, 0.0, 1.0, 0.5, "Tail Size"),
            'side_count': Slider(20, height - 100, 200, 20, 0.0, 1.0, 0.5, "Side Fin Count"),
            'side_size': Slider(20, height - 60, 200, 20, 0.0, 1.0, 0.5, "Side Fin Size"),
            
            'energy': Slider(240, height - 140, 200, 20, 0.0, 1.0, 1.0, "Energy"),
            'health': Slider(240, height - 100, 200, 20, 0.0, 1.0, 1.0, "Health"),
        }
        
        # Dummy Space für die Entity
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        
        # Test-Entity erstellen
        self.test_entity = None
        self._create_test_entity()
        
    def _create_test_entity(self):
        """Erstellt eine Test-Entity mit den aktuellen Slider-Werten"""
        # Alte Entity entfernen wenn vorhanden
        if self.test_entity and hasattr(self.test_entity, 'body'):
            self.space.remove(self.test_entity.body, self.test_entity.shape)
        
        # DNA mit aktuellen Slider-Werten erstellen
        dna = DNA()
        dna.values['sensors']['eye_size'] = self.sliders['eye_size'].value
        dna.values['feeding']['mouth_size'] = self.sliders['mouth_size'].value
        dna.values['feeding']['mouth_teeth'] = self.sliders['mouth_teeth'].value
        dna.values['movement']['movement_forward_organ_size'] = self.sliders['forward_size'].value
        dna.values['movement']['movement_side_organ_count'] = self.sliders['side_count'].value
        dna.values['movement']['movement_side_organ_size'] = self.sliders['side_size'].value
        
        # Neue Entity erstellen
        self.test_entity = Entity(self.space, self.width//2, self.height//2, dna)
        
    def run(self):
        """Hauptschleife"""
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Prüfe, ob der Klick außerhalb der Slider-Bereiche ist
                    click_on_slider = False
                    for slider in self.sliders.values():
                        if slider.rect.collidepoint(event.pos):
                            click_on_slider = True
                            break
                    
                    if event.button == 1 and not click_on_slider:  # Linke Maustaste und nicht auf Slider
                        self.dragging = True
                        self.last_mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Linke Maustaste
                        self.dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]
                        self.offset_x += dx
                        self.offset_y += dy
                        self.last_mouse_pos = event.pos
                
                # Slider Events
                for slider in self.sliders.values():
                    slider.handle_event(event)
                    
                # Bei Slider-Änderungen Entity neu erstellen
                if any(slider.active for slider in self.sliders.values()):
                    self._create_test_entity()
            
            # Update Zoom
            self.zoom = self.sliders['zoom'].value
            
            # Rendering
            self.screen.fill((20, 20, 30))  # Dunkler Hintergrund
            
            # Temporäre Surface für die Entity
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Entity zeichnen
            if self.test_entity:
                # Energie und Gesundheit aktualisieren
                self.test_entity.energy = self.sliders['energy'].value * self.test_entity.max_energy
                self.test_entity.health = self.sliders['health'].value * self.test_entity.max_health
                
                # Entity auf temporärer Surface zeichnen
                self.test_entity.draw(temp_surface, True)  # Debug-Modus aktiviert
                
                # Surface skalieren
                scaled_size = (
                    int(self.width * self.zoom),
                    int(self.height * self.zoom)
                )
                scaled_surface = pygame.transform.scale(temp_surface, scaled_size)
                
                # Zentriert mit Offset zeichnen
                self.screen.blit(scaled_surface, 
                    (self.offset_x - (scaled_size[0] - self.width) // 2,
                     self.offset_y - (scaled_size[1] - self.height) // 2))
            
            # Slider zeichnen (immer an fester Position)
            for slider in self.sliders.values():
                slider.draw(self.screen)
            
            # Hilfetext (immer an fester Position)
            font = pygame.font.Font(None, 24)
            help_text = "Linke Maustaste: Ansicht verschieben (außerhalb der Slider)"
            text_surface = font.render(help_text, True, (200, 200, 200))
            self.screen.blit(text_surface, (20, 20))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    test = CreatureDesignTest()
    test.run() 