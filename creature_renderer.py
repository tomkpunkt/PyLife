import pygame
import numpy as np
from typing import Dict, Tuple

# Basis-Farben
BASE_COLOR = (32, 255, 232)  # Helles Türkis
DARK_COLOR = (16, 168, 152)  # Dunkleres Türkis für Schatten
SIDE_COLOR = (50, 205, 50)  # Helles Grün
SIDE_DARK_COLOR = (34, 139, 34)  # Dunkleres Grün
BACK_COLOR = (255, 140, 0)  # Helles Orange
BACK_DARK_COLOR = (205, 103, 0)  # Dunkleres Orange

# Animation und Rendering Konstanten
WAVE_ANIMATION_SPEED = 0.005
WAVE_FREQUENCY = 0.8
WAVE_AMPLITUDE = 0.2
SIDE_FIN_SPACING = 0.2
TAIL_WIDTH_FACTOR = 0.4
SIDE_FIN_WIDTH_FACTOR = 0.15

class CreatureRenderer:
    def __init__(self):
        self.default_width = 68  # Basis-Breite
        self.default_length = 48  # Basis-Länge (größer für längliche Form)
        
    def _create_body_surface(self, width: int, height: int) -> pygame.Surface:
        """Erstellt die Grundform des Körpers als längliches Oval"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        padding = 10  # Pixel Abstand für den Rand

        # Äußeres Oval (dunklerer Rand)
        pygame.draw.ellipse(surface, DARK_COLOR, (
            padding, 
            padding, 
            width - padding * 2, 
            height - padding * 2
        ))
        pygame.draw.ellipse(surface, BASE_COLOR, (
            padding+1, 
            padding+1, 
            width - padding * 2 - 2, 
            height - padding * 2 - 2
        ))
        
        return surface.convert_alpha()
    
    def _add_mouth(self, surface: pygame.Surface, dna: Dict) -> None:
        """Fügt einen runden Mund hinzu"""
        width, height = surface.get_size()
        
        # Mundgröße basierend auf DNA (zwischen 10% und 25% der Breite)
        mouth_size = int(width * 0.7 * (0.1 + 0.1 * dna['feeding']['mouth_size']))
        teeth_size = int(width * 0.7 * (0.05 + 0.05 * dna['feeding']['mouth_teeth']))
        
        # Position (vorne/rechts)
        mouth_x = width * 0.8  # 80% von der Breite für die rechte Seite
        mouth_y = height * 0.5  # Mitte der Höhe
        
        # Äußeres Oval (dunklerer Rand)
        pygame.draw.circle(surface, DARK_COLOR, (int(mouth_x), int(mouth_y)), mouth_size + 2)
        # Zeichne den Zähne als weißer Kreis
        pygame.draw.circle(surface, (255, 255, 255), (int(mouth_x), int(mouth_y)), mouth_size)
       # Zeichne den Mund als schwarzes oval
        pygame.draw.ellipse(surface, (0, 0, 0), (mouth_x-mouth_size+teeth_size, mouth_y-mouth_size, 2*(mouth_size-teeth_size), 2*mouth_size))
    
    def _add_eyes(self, surface: pygame.Surface, dna: Dict, energy_percentage: float) -> None:
        """Fügt pixelige Augen hinzu"""
        width, height = surface.get_size()
        
        # Augengröße basierend auf DNA
        eye_size = int(5.5 * dna['sensors']['eye_size'])

        # Zwei Augen vertikal angeordnet
        eye_positions = [
            (width * 0.65, height * 0.22),
            (width * 0.65, height * 0.78)
        ]
        
        for pos in eye_positions:

            # Äußeres Oval (dunklerer Rand)
            pygame.draw.circle(surface, DARK_COLOR, (int(pos[0]), int(pos[1])), eye_size + 2)
            # Weißer Außenring
            pygame.draw.circle(surface, (255, 255, 255),(int(pos[0]), int(pos[1])), eye_size)
            # Türkisfarbene Iris
            pygame.draw.circle(surface, BASE_COLOR,(int(pos[0]), int(pos[1])), eye_size - 2)
            # Schwarze Pupille
            pupil_size = max(2, int(eye_size * 0.4))
            pygame.draw.circle(surface, (0, 0, 0),(int(pos[0]), int(pos[1])), pupil_size)
    
    def _add_forward_movement_organs(self, surface: pygame.Surface, dna: Dict, energy_percentage: float) -> None:
        """Fügt eine Schwanzflosse hinzu, die sich wellenförmig bewegt"""
        width, height = surface.get_size()
        
        # Flossengröße basierend auf DNA
        fin_size = max(4, int(width * TAIL_WIDTH_FACTOR * 
                             dna.get('movement', {}).get('movement_forward_organ_size', 0.5)))
        
        # Basis-Position der Flosse (links/hinten)
        base_x = width * 0.25
        base_y = height * 0.5
        
        # Animation
        time_offset = pygame.time.get_ticks() * WAVE_ANIMATION_SPEED
        
        # Punkte für die Flossenform berechnen
        points = []
        
        # Obere Hälfte der Flosse
        for i in range(6):
            t = i / 5.0  # 0 bis 1
            # X-Position: nach links ausbreiten
            x = base_x - (fin_size * 0.8 * t)
            # Y-Position: Wellenform nach oben
            wave = np.sin(time_offset + t * 3) * (fin_size * 0.15)
            curve = -(1 - (2*t-1)**2)  # Parabelform für die Kontur
            y = base_y + wave + (curve * fin_size * 0.5)
            points.append((int(x), int(y)))
        
        # Untere Hälfte der Flosse (gespiegelt)
        for i in range(5, -1, -1):
            t = i / 5.0
            x = base_x - (fin_size * 0.8 * t)
            wave = np.sin(time_offset + t * 3) * (fin_size * 0.15)
            curve = (1 - (2*t-1)**2)  # Gespiegelte Parabelform
            y = base_y + wave + (curve * fin_size * 0.5)
            points.append((int(x), int(y)))
        
        # Flosse zeichnen
        if len(points) >= 3:
            # Äußerer Rand (dunkel)
            pygame.draw.polygon(surface, BACK_DARK_COLOR, points)
            
            # Innere Flosse (hell) - etwas kleiner für Randeffekt
            inner_points = []
            center = (base_x, base_y)
            for point in points:
                # Punkt leicht zum Zentrum verschieben für inneren Bereich
                dx = point[0] - center[0]
                dy = point[1] - center[1]
                scale = 0.9  # Skalierungsfaktor für inneren Bereich
                inner_x = center[0] + dx * scale
                inner_y = center[1] + dy * scale
                inner_points.append((int(inner_x), int(inner_y)))
            
            pygame.draw.polygon(surface, BACK_COLOR, inner_points)

    def _add_side_movement_organs(self, surface: pygame.Surface, dna: Dict, energy_percentage: float) -> None:
        """Fügt die seitlichen Bewegungsorgane (Flossen) hinzu"""
        width, height = surface.get_size()
        
        # Flossengröße basierend auf DNA - deutlich größer
        fin_size = max(8, int(width * 0.3 * 
                           dna.get('movement', {}).get('movement_side_organ_size', 0.5)))
        
        # Positionen der Flossen (weiter außen)
        top_fin_y = height * 0.25  # Weiter nach oben
        bottom_fin_y = height * 0.75  # Weiter nach unten
        fin_x = width * 0.35  # Genau in der Mitte
        
        # Zeit für Animation
        time_offset = pygame.time.get_ticks() * 0.002
        wave = np.sin(time_offset) * fin_size * 0.2
        
        # Obere Flosse zeichnen
        top_points = []
        for i in range(5):
            t = i / 4.0  # 0 bis 1
            # Parabelförmige Kurve nach oben, stärker ausgeprägt
            x = fin_x + fin_size * t
            curve = -(1 - (2*t-1)**2) * 1.5  # Stärkere Krümmung
            y = top_fin_y + wave * (1-t) + (curve * fin_size * 0.7)  # Größere vertikale Ausdehnung
            top_points.append((int(x), int(y)))
        
        # Basis der oberen Flosse
        top_points.append((int(fin_x), int(top_fin_y)))
        
        # Untere Flosse zeichnen
        bottom_points = []
        for i in range(5):
            t = i / 4.0
            x = fin_x + fin_size * t
            curve = (1 - (2*t-1)**2) * 1.5  # Stärkere Krümmung
            y = bottom_fin_y + wave * (1-t) + (curve * fin_size * 0.7)  # Größere vertikale Ausdehnung
            bottom_points.append((int(x), int(y)))
        
        # Basis der unteren Flosse
        bottom_points.append((int(fin_x), int(bottom_fin_y)))
        
        # Flossen zeichnen
        if len(top_points) >= 3:
            # Äußerer Rand (dunkel)
            pygame.draw.polygon(surface, SIDE_DARK_COLOR, top_points)  # Grüne Farbe für Seitenflossen
            pygame.draw.polygon(surface, SIDE_DARK_COLOR, bottom_points)
            
            # Innere Flosse (hell) - etwas kleiner für Randeffekt
            def scale_points(points, center, scale=0.9):
                scaled = []
                for point in points:
                    dx = point[0] - center[0]
                    dy = point[1] - center[1]
                    scaled.append((
                        int(center[0] + dx * scale),
                        int(center[1] + dy * scale)
                    ))
                return scaled
            
            # Skalierte innere Punkte für beide Flossen
            top_inner = scale_points(top_points, (fin_x, top_fin_y))
            bottom_inner = scale_points(bottom_points, (fin_x, bottom_fin_y))
            
            # Innere Flossen zeichnen
            pygame.draw.polygon(surface, SIDE_COLOR, top_inner)  # Hellgrüne Farbe für innere Flossen
            pygame.draw.polygon(surface, SIDE_COLOR, bottom_inner)

    def _draw_bounding_box(self, surface: pygame.Surface) -> None:
        """Zeichnet einen weißen Rahmen um die Kreatur"""
        width, height = surface.get_size()
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, width-1, height-1), 1)

    def render_creature(self, dna: Dict, health_percentage: float = 1.0, energy_percentage: float = 1.0) -> pygame.Surface:
        """Erstellt eine Kreatur im Pixel-Art Stil"""
        # Größe basierend auf DNA mit Fehlerbehandlung
        size = dna.get('physical', {}).get('size', 1.0)
        width = int(self.default_width * size)
        height = int(self.default_length * size)
        
        # Erstelle Surface
        surface = self._create_body_surface(width, height)
        
        # Features hinzufügen
        self._add_forward_movement_organs(surface, dna, energy_percentage)
        self._add_side_movement_organs(surface, dna, energy_percentage)
        self._add_mouth(surface, dna)
        self._add_eyes(surface, dna, energy_percentage)
        
        # Bounding Box zeichnen
        #self._draw_bounding_box(surface)
        
        return surface 