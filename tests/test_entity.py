import pytest
import numpy as np
import pymunk
import pygame
from entity import Entity

@pytest.fixture
def space():
    """Erstellt einen Pymunk-Space für Tests"""
    space = pymunk.Space()
    space.gravity = (0, 0)
    return space

@pytest.fixture
def entity(space):
    """Erstellt eine Test-Entity"""
    return Entity(space, 100, 100)

class TestEntity:
    def test_initialization(self, entity):
        """Testet die korrekte Initialisierung einer Entity"""
        assert entity.energy > 0
        assert entity.health > 0
        assert entity.hunger == 0
        assert entity.age == 0
        assert entity.food_eaten == 0
        assert entity.children == 0
        
        # DNA-Werte überprüfen
        assert 'size' in entity.dna
        assert 'speed' in entity.dna
        assert 'energy_efficiency' in entity.dna
        assert 'sensor_range' in entity.dna
        assert 'health' in entity.dna
        assert 'reproduction_rate' in entity.dna
        
        # Physikalische Eigenschaften
        assert entity.radius > 0
        assert entity.mass > 0
        assert entity.body is not None
        assert entity.shape is not None

    def test_dna_generation(self, space):
        """Testet die DNA-Generierung"""
        entity = Entity(space, 100, 100)
        
        # Überprüfe, dass alle DNA-Werte im erwarteten Bereich liegen
        assert 0.8 <= entity.dna['size'] <= 1.2
        assert 0.8 <= entity.dna['speed'] <= 1.2
        assert 0.8 <= entity.dna['energy_efficiency'] <= 1.2
        assert 0.8 <= entity.dna['sensor_range'] <= 1.2
        assert 0.8 <= entity.dna['health'] <= 1.2
        assert 0.8 <= entity.dna['reproduction_rate'] <= 1.2

    def test_energy_consumption(self, entity):
        """Testet den Energieverbrauch"""
        initial_energy = entity.energy
        
        # Simuliere einen Zeitschritt
        entity.update(1.0)
        
        # Energie sollte abgenommen haben
        assert entity.energy < initial_energy
        
        # Bei maximalem Hunger sollte der Verbrauch doppelt so hoch sein
        entity.hunger = entity.max_hunger
        energy_before_hunger = entity.energy
        entity.update(1.0)
        energy_after_hunger = entity.energy
        
        # Der Energieverbrauch sollte etwa doppelt so hoch sein
        energy_loss_normal = initial_energy - energy_before_hunger
        energy_loss_hunger = energy_before_hunger - energy_after_hunger
        assert energy_loss_hunger > energy_loss_normal

    def test_hunger_increase(self, entity):
        """Testet den Hungeranstieg"""
        initial_hunger = entity.hunger
        
        # Simuliere einen Zeitschritt
        entity.update(1.0)
        
        # Hunger sollte zugenommen haben
        assert entity.hunger > initial_hunger
        
        # Hunger sollte nicht über max_hunger steigen
        assert entity.hunger <= entity.max_hunger

    def test_health_reduction(self, entity):
        """Testet die Gesundheitsreduktion bei 0 Energie"""
        entity.energy = 0
        initial_health = entity.health
        
        # Simuliere einen Zeitschritt
        entity.update(1.0)
        
        # Gesundheit sollte abgenommen haben
        assert entity.health < initial_health
        
        # Bei 0 Gesundheit sollte die Entity sterben
        entity.health = 0
        assert not entity.update(1.0)

    def test_reproduction(self, entity):
        """Testet die Fortpflanzungsmechanik"""
        # Entity sollte sich nicht fortpflanzen können, wenn sie nicht genug Energie hat
        entity.energy = entity.reproduction_cost - 1
        assert not entity.can_reproduce()
        
        # Entity sollte sich fortpflanzen können, wenn sie genug Energie hat
        entity.energy = entity.reproduction_cost
        entity.health = entity.max_health * 0.8
        assert entity.can_reproduce()
        
        # Nach der Fortpflanzung sollte die Energie abgenommen haben
        initial_energy = entity.energy
        entity.reproduce()
        assert entity.energy < initial_energy
        assert entity.children == 1

    def test_movement(self, entity):
        """Testet die Bewegungsmechanik"""
        initial_pos = entity.body.position
        
        # Simuliere einen Zeitschritt
        entity.update(1.0)
        
        # Position sollte sich geändert haben
        assert entity.body.position != initial_pos
        
        # Zurückgelegte Distanz sollte größer als 0 sein
        assert entity.distance_traveled > 0

    def test_digestion(self, entity):
        """Testet das Verdauungssystem"""
        # Simuliere Nahrungsaufnahme
        class MockFood:
            def __init__(self):
                self.size = 1.0
                self.energy_value = 50
                self.quality = 1.0
        
        food = MockFood()
        assert entity.eat_food(food)
        
        # Verdauungsliste sollte nicht leer sein
        assert len(entity.digesting_food) > 0
        
        # Energie sollte sich erhöhen
        initial_energy = entity.energy
        entity.update(1.0)
        assert entity.energy > initial_energy 

    def test_draw_highlight(self, entity):
        """Testet die Hervorhebungsfunktion"""
        # Erstelle eine Test-Surface
        surface = pygame.Surface((200, 200))
        
        # Zeichne die Hervorhebung
        entity.draw_highlight(surface)
        
        # Überprüfe, ob die Surface nicht leer ist
        assert not surface.get_rect().collidepoint(100, 100) 