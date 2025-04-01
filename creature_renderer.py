import pygame
import numpy as np
from typing import Dict, Tuple

class CreatureRenderer:
    def __init__(self):
        self.max_width = 30
        self.max_height = 20
        
    def _create_body_surface(self, width: int, height: int, color: Tuple[int, int, int]) -> pygame.Surface:
        """Erstellt die Grundform des Körpers mit mehr Details und Textur"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Dunklerer Rand für mehr Kontrast
        border_color = tuple(max(0, c - 60) for c in color)
        # Hellere Highlights für 3D-Effekt
        highlight_color = tuple(min(255, c + 40) for c in color)
        
        # Hauptkörper (oval)
        pygame.draw.ellipse(surface, border_color, (0, 0, width, height))
        pygame.draw.ellipse(surface, color, (2, 2, width-4, height-4))
        
        # Highlight für 3D-Effekt (oben links)
        highlight_rect = pygame.Rect(width * 0.2, height * 0.2, width * 0.3, height * 0.3)
        pygame.draw.ellipse(surface, highlight_color, highlight_rect)
        
        # Muster/Textur hinzufügen
        pattern_color = tuple(max(0, c - 30) for c in color)
        num_patterns = max(3, int(width / 10))
        for i in range(num_patterns):
            pattern_x = width * (0.2 + 0.6 * i / num_patterns)
            pattern_height = height * 0.4
            pattern_rect = pygame.Rect(pattern_x, height * 0.3, width * 0.1, pattern_height)
            pygame.draw.ellipse(surface, pattern_color, pattern_rect)
        
        return surface
    
    def _add_eyes(self, surface: pygame.Surface, dna: Dict, energy_percentage: float) -> None:
        """Fügt Augen basierend auf DNA hinzu"""
        width, height = surface.get_size()
        eye_size = max(3, int(width * 0.15))
        eye_count = max(1, min(4, int(dna['eye_count'])))
        
        # Hellere, leuchtendere Augen basierend auf Energie
        glow_factor = 0.5 + energy_percentage * 0.5  # Mindestens 50% Leuchtkraft
        eye_color = (
            min(255, int((220 + dna['sensor_range'] * 35) * glow_factor)),
            min(255, int((220 + dna['sensor_range'] * 35) * glow_factor)),
            0
        )
        
        # Augen gleichmäßig verteilen
        for i in range(eye_count):
            x = width * 0.7  # Augen im vorderen Drittel
            y = height * (0.3 + (0.4 * i / max(1, eye_count - 1)))  # Vertikal verteilen
            
            # Äußerer Kreis (Kontrast)
            pygame.draw.circle(surface, (20, 20, 20), (int(x), int(y)), eye_size + 1)
            # Auge
            pygame.draw.circle(surface, eye_color, (int(x), int(y)), eye_size)
            # Pupille (größer bei weniger Energie)
            pupil_size = max(2, int(eye_size * (0.5 + (1 - energy_percentage) * 0.3)))
            pygame.draw.circle(surface, (0, 0, 0), (int(x), int(y)), pupil_size)
            # Glanzpunkt (heller bei mehr Energie)
            highlight_size = max(1, int(eye_size * 0.25 * energy_percentage))
            highlight_color = (int(255 * energy_percentage), int(255 * energy_percentage), int(255 * energy_percentage))
            pygame.draw.circle(surface, highlight_color, (int(x-1), int(y-1)), highlight_size)
    
    def _add_spikes(self, surface: pygame.Surface, dna: Dict) -> None:
        """Fügt Stacheln oder Auswüchse basierend auf DNA hinzu"""
        width, height = surface.get_size()
        spike_count = max(3, int(10 * dna['spike_factor']))
        spike_length = max(3, int(height * 0.3 * dna['spike_length']))
        
        # Kontrastreichere Stachelfarbe
        base_color = (
            min(255, int(180 + dna['health'] * 75)),
            min(255, int(50 + dna['energy_efficiency'] * 105)),
            min(255, int(50 + dna['speed'] * 105))
        )
        # Dunklere Spitzen für Kontrast
        tip_color = tuple(max(0, c - 80) for c in base_color)
        
        # Stacheln rund um den Körper verteilen
        for i in range(spike_count):
            angle = (2 * np.pi * i) / spike_count
            base_x = width * 0.5 + np.cos(angle) * width * 0.4
            base_y = height * 0.5 + np.sin(angle) * height * 0.4
            tip_x = base_x + np.cos(angle) * spike_length
            tip_y = base_y + np.sin(angle) * spike_length
            
            # Breiter Stachel mit Basis-Farbe
            pygame.draw.line(surface, base_color, 
                           (int(base_x), int(base_y)), 
                           (int(tip_x), int(tip_y)), 
                           max(2, int(spike_length * 0.4)))
            
            # Dunklere Spitze für Kontrast
            pygame.draw.line(surface, tip_color,
                           (int(base_x + np.cos(angle) * spike_length * 0.6), 
                            int(base_y + np.sin(angle) * spike_length * 0.6)),
                           (int(tip_x), int(tip_y)),
                           max(2, int(spike_length * 0.3)))
    
    def _add_movement_organs(self, surface: pygame.Surface, dna: Dict, energy_percentage: float) -> None:
        """Fügt Bewegungsorgane (Flossen/Beine) basierend auf DNA hinzu"""
        width, height = surface.get_size()
        organ_count = max(2, int(4 * dna['movement_organ_count']))
        organ_size = max(3, int(height * 0.2 * dna['movement_organ_size']))
        
        # Kontrastreichere Organfarbe basierend auf Energie
        energy_factor = 0.6 + energy_percentage * 0.4  # Mindestens 60% Farbintensität
        base_color = (
            min(255, int((150 + dna['speed'] * 105) * energy_factor)),
            min(255, int((150 + dna['speed'] * 105) * energy_factor)),
            min(255, int((50 + dna['speed'] * 155) * energy_factor))
        )
        # Dunklerer Rand für Kontrast
        border_color = tuple(max(0, c - 60) for c in base_color)
        
        # Bewegungsorgane an den Seiten verteilen mit Animation basierend auf Energie
        animation_offset = np.sin(pygame.time.get_ticks() * 0.01 * energy_percentage) * organ_size * 0.2
        
        for i in range(organ_count):
            y = height * (0.3 + (0.4 * i / max(1, organ_count - 1)))
            
            # Position mit Animation
            y_offset = y + animation_offset * (1 if i % 2 == 0 else -1)
            
            # Linke Seite
            pygame.draw.ellipse(surface, border_color,
                              (0, y_offset - organ_size//2, organ_size * 1.5, organ_size))
            pygame.draw.ellipse(surface, base_color,
                              (1, y_offset - organ_size//2 + 1, organ_size * 1.5 - 2, organ_size - 2))
            
            # Rechte Seite
            pygame.draw.ellipse(surface, border_color,
                              (width - organ_size * 1.5, y_offset - organ_size//2, organ_size * 1.5, organ_size))
            pygame.draw.ellipse(surface, base_color,
                              (width - organ_size * 1.5 + 1, y_offset - organ_size//2 + 1, 
                               organ_size * 1.5 - 2, organ_size - 2))
    
    def render_creature(self, dna: Dict, health_percentage: float = 1.0, energy_percentage: float = 1.0) -> pygame.Surface:
        """Erstellt eine Kreatur basierend auf ihrer DNA und aktuellem Zustand"""
        # Größe basierend auf DNA
        width = int(self.max_width * dna['size'])
        height = int(self.max_height * dna['size'])
        
        # Basis-Farbwerte berechnen
        health_color = (
            min(255, int(200 + (1 - health_percentage) * 55)),  # Mehr rot bei weniger Gesundheit
            min(255, int(130 + health_percentage * 125)),
            min(255, int(130 + dna['speed'] * 125))
        )
        
        energy_factor = energy_percentage * 0.7 + 0.3  # Mindestens 30% Helligkeit
        
        # Finale Farbe basierend auf Gesundheit und Energie
        base_color = (
            int(health_color[0] * energy_factor),
            int(health_color[1] * energy_factor),
            int(health_color[2] * energy_factor)
        )
        
        # Grundkörper erstellen
        surface = self._create_body_surface(width, height, base_color)
        
        # Features mit angepasster Intensität hinzufügen
        self._add_movement_organs(surface, dna, energy_percentage)
        self._add_spikes(surface, dna)
        self._add_eyes(surface, dna, energy_percentage)
        
        return surface 