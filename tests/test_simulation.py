import pytest
import numpy as np
import pymunk
import pygame
from PyLife.simulation import Simulation

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
        assert simulation.population_size == 20  # Neue Eigenschaft

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
        assert hasattr(entity, 'brain')  # Überprüfe Brain-Initialisierung

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
        assert hasattr(food, 'energy_value')
        assert hasattr(food, 'quality')

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
        
        # Speichere den aktuellen Zoom-Wert
        current_zoom = simulation.zoom
        
        # Teste Zoom-Out
        simulation.handle_zoom(-1, (400, 300))
        assert simulation.zoom < current_zoom
        
        # Teste Zoom-Grenzen
        for _ in range(20):
            simulation.handle_zoom(1, (400, 300))
        assert simulation.zoom <= 4.0  # Maximaler Zoom
        
        for _ in range(20):
            simulation.handle_zoom(-1, (400, 300))
        assert simulation.zoom >= 0.25  # Minimaler Zoom

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
        # Spawne die initiale Population
        for _ in range(simulation.population_size):
            simulation.spawn_entity()
        
        # Setze verschiedene Fitness-Werte
        for i, entity in enumerate(simulation.entities):
            entity.food_eaten = i  # Unterschiedliche Fitness-Werte
        
        initial_count = len(simulation.entities)
        simulation.next_generation()
        
        # Überprüfe die neue Generation
        assert len(simulation.entities) == simulation.population_size
        assert simulation.generation == 2
        
        # Die besten Entities sollten überlebt haben
        survivors = [e for e in simulation.entities if e.food_eaten > 0]
        assert len(survivors) > 0

    def test_brain_updates(self, simulation):
        """Testet die Gehirn-Updates der Entities"""
        simulation.spawn_entity()
        entity = simulation.entities[0]
        
        # Initialer Brain-Output
        initial_output = entity.brain_output if hasattr(entity, 'brain_output') else None
        
        # Simuliere mehrere Updates
        for _ in range(5):
            simulation.update(1.0)
            
            # Brain-Output sollte sich ändern
            if initial_output is not None:
                assert not np.array_equal(entity.brain_output, initial_output)
            initial_output = entity.brain_output.copy()

    def test_fitness_based_selection(self, simulation):
        """Testet die fitnessbasierte Selektion"""
        # Spawne Entities mit verschiedenen Fitness-Werten
        for _ in range(simulation.population_size):
            simulation.spawn_entity()
        
        # Setze verschiedene Eigenschaften für unterschiedliche Fitness
        for i, entity in enumerate(simulation.entities):
            entity.health = entity.max_health * (i / len(simulation.entities))
            entity.energy = entity.max_energy * (i / len(simulation.entities))
            entity.food_eaten = i
            entity.children = i % 3
        
        # Speichere die besten Entities
        sorted_entities = sorted(simulation.entities, 
                               key=lambda e: e.fitness, 
                               reverse=True)
        best_entities = sorted_entities[:simulation.population_size // 5]
        best_ids = [id(e) for e in best_entities]
        
        # Nächste Generation
        simulation.next_generation()
        
        # Überprüfe, ob einige der besten Entities überlebt haben
        survivors = [e for e in simulation.entities if id(e) in best_ids]
        assert len(survivors) > 0 