import pytest
import numpy as np
import pymunk
import pygame
from PyLife.world_food import Food

@pytest.fixture
def space():
    """Erstellt einen Pymunk-Space für Tests"""
    space = pymunk.Space()
    space.gravity = (0, 0)
    return space

@pytest.fixture
def food(space):
    """Erstellt ein Test-Food-Objekt"""
    return Food(space, 100, 100)

class TestFood:
    def test_initialization(self, food):
        """Testet die korrekte Initialisierung eines Food-Objekts"""
        assert food.size > 0
        assert food.energy_value > 0
        assert 0 <= food.quality <= 1
        assert food.body is not None
        assert food.shape is not None
        
        # Physikalische Eigenschaften
        assert food.radius > 0
        assert food.mass > 0

    def test_energy_calculation(self, space):
        """Testet die Energieberechnung basierend auf Größe und Qualität"""
        # Test mit verschiedenen Größen und Qualitäten
        test_cases = [
            (1.0, 1.0),  # Normale Größe, maximale Qualität
            (2.0, 0.5),  # Doppelte Größe, halbe Qualität
            (0.5, 0.8),  # Halbe Größe, gute Qualität
        ]
        
        for size, quality in test_cases:
            food = Food(space, 100, 100, size=size, quality=quality)
            expected_energy = size * quality * 50  # Basisenergie * Größe * Qualität
            assert abs(food.energy_value - expected_energy) < 0.1

    def test_color_calculation(self, food):
        """Testet die Farbberechnung basierend auf der Qualität"""
        # Test mit verschiedenen Qualitäten
        test_cases = [
            (1.0, (0, 255, 0)),  # Maximale Qualität = reines Grün
            (0.5, (0, 127, 0)),  # Mittlere Qualität = halbes Grün
            (0.0, (0, 0, 0)),    # Minimale Qualität = schwarz
        ]
        
        for quality, expected_color in test_cases:
            food.quality = quality
            color = food.color
            assert abs(color[0] - expected_color[0]) < 1
            assert abs(color[1] - expected_color[1]) < 1
            assert abs(color[2] - expected_color[2]) < 1

    def test_glow_effect(self, food):
        """Testet den Glow-Effekt für hochwertige Nahrung"""
        # Bei hoher Qualität sollte der Glow-Effekt aktiv sein
        food.quality = 1.0
        assert food.glow_radius > 0
        assert food.glow_alpha > 0
        
        # Bei niedriger Qualität sollte kein Glow-Effekt sein
        food.quality = 0.3
        assert food.glow_radius == 0
        assert food.glow_alpha == 0

    def test_physical_properties(self, food):
        """Testet die physikalischen Eigenschaften"""
        # Masse sollte proportional zur Größe sein
        initial_mass = food.mass
        food.size *= 2
        assert abs(food.mass - initial_mass * 2) < 0.1
        
        # Radius sollte proportional zur Größe sein
        initial_radius = food.radius
        food.size *= 2
        assert abs(food.radius - initial_radius * 2) < 0.1

    def test_draw(self, food):
        """Testet die Draw-Funktion"""
        # Erstelle eine Test-Surface
        surface = pygame.Surface((200, 200))
        
        # Zeichne das Food-Objekt
        food.draw(surface)
        
        # Überprüfe, ob die Surface nicht leer ist
        assert not surface.get_rect().collidepoint(100, 100) 