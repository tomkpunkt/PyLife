import pytest
import numpy as np
import pymunk
import pygame
from simulation import Simulation

@pytest.fixture
def simulation():
    """Erstellt eine Test-Simulation"""
    return Simulation(800, 600)

class TestSimulation:
    def test_initialization(self, simulation):
        """Testet die korrekte Initialisierung der Simulation"""
        assert simulation.width == 800
        assert simulation.height == 600
        assert simulation.space is not None
        assert simulation.entities == []
        assert simulation.food == []
        assert simulation.waste == []
        assert simulation.selected_entity is None
        assert simulation.generation == 1
        assert simulation.zoom == 1.0
        assert simulation.camera_offset == (0, 0)

    def test_spawn_entity(self, simulation):
        """Testet das Spawnen von Entities"""
        initial_count = len(simulation.entities)
        simulation.spawn_entity()
        assert len(simulation.entities) == initial_count + 1
        
        # Überprüfe, ob die Entity korrekt initialisiert wurde
        entity = simulation.entities[-1]
        assert entity.body.position.x >= 0
        assert entity.body.position.x <= simulation.width
        assert entity.body.position.y >= 0
        assert entity.body.position.y <= simulation.height

    def test_spawn_food(self, simulation):
        """Testet das Spawnen von Nahrung"""
        initial_count = len(simulation.food)
        simulation.spawn_food()
        assert len(simulation.food) == initial_count + 1
        
        # Überprüfe, ob das Food korrekt initialisiert wurde
        food = simulation.food[-1]
        assert food.body.position.x >= 0
        assert food.body.position.x <= simulation.width
        assert food.body.position.y >= 0
        assert food.body.position.y <= simulation.height

    def test_entity_selection(self, simulation):
        """Testet die Entity-Auswahl"""
        # Spawne eine Entity
        simulation.spawn_entity()
        entity = simulation.entities[0]
        
        # Simuliere einen Klick auf die Entity
        pos = (int(entity.body.position.x), int(entity.body.position.y))
        simulation.handle_click(pos)
        assert simulation.selected_entity == entity
        
        # Simuliere einen Klick außerhalb der Entity
        simulation.handle_click((0, 0))
        assert simulation.selected_entity is None

    def test_zoom(self, simulation):
        """Testet die Zoom-Funktionalität"""
        initial_zoom = simulation.zoom
        
        # Teste Zoom-In
        simulation.handle_zoom(1, (400, 300))
        assert simulation.zoom > initial_zoom
        
        # Teste Zoom-Out
        simulation.handle_zoom(-1, (400, 300))
        assert simulation.zoom < simulation.zoom
        
        # Teste Zoom-Grenzen
        simulation.zoom = 0.1
        simulation.handle_zoom(-1, (400, 300))
        assert simulation.zoom == 0.1
        
        simulation.zoom = 3.0
        simulation.handle_zoom(1, (400, 300))
        assert simulation.zoom == 3.0

    def test_entity_death(self, simulation):
        """Testet das Entfernen toter Entities"""
        # Spawne eine Entity
        simulation.spawn_entity()
        entity = simulation.entities[0]
        
        # Setze Energie und Gesundheit auf 0
        entity.energy = 0
        entity.health = 0
        
        # Aktualisiere die Simulation
        simulation.update(1.0)
        
        # Entity sollte entfernt worden sein
        assert entity not in simulation.entities

    def test_food_consumption(self, simulation):
        """Testet die Nahrungsaufnahme"""
        # Spawne eine Entity und Nahrung
        simulation.spawn_entity()
        simulation.spawn_food()
        
        entity = simulation.entities[0]
        food = simulation.food[0]
        
        # Setze Entity und Food auf die gleiche Position
        entity.body.position = food.body.position
        
        # Aktualisiere die Simulation
        simulation.update(1.0)
        
        # Überprüfe, ob die Nahrung verarbeitet wurde
        assert food not in simulation.food
        assert len(entity.digesting_food) > 0

    def test_next_generation(self, simulation):
        """Testet die Generationswechsel"""
        # Spawne einige Entities
        for _ in range(5):
            simulation.spawn_entity()
        
        initial_count = len(simulation.entities)
        simulation.next_generation()
        
        # Überprüfe, ob die alte Generation entfernt wurde
        assert len(simulation.entities) < initial_count
        
        # Überprüfe, ob die neue Generation gestartet wurde
        assert simulation.generation > 1 