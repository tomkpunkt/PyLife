import pytest
import numpy as np
import pymunk
import pygame
from PyLife.creature import Entity

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
        assert 'physical' in entity.dna.values
        assert 'movement' in entity.dna.values
        assert 'sensors' in entity.dna.values
        assert 'offense' in entity.dna.values
        assert 'feeding' in entity.dna.values
        assert 'reproduction' in entity.dna.values
        
        # Physikalische Eigenschaften
        assert entity.radius > 0
        assert entity.mass > 0
        assert entity.body is not None
        assert entity.shape is not None
        
        # Neuronales Netzwerk
        assert hasattr(entity, 'brain')
        assert entity.brain is not None

    def test_dna_generation(self, space):
        """Testet die DNA-Generierung"""
        entity = Entity(space, 100, 100)
        
        # Überprüfe, dass alle DNA-Werte im erwarteten Bereich liegen
        assert 0.0 <= entity.dna['physical']['size'] <= 1.0
        assert 0.0 <= entity.dna['movement']['movement_forward_organ_size'] <= 1.0
        assert 0.0 <= entity.dna['sensors']['sensor_range'] <= 1.0
        assert 0.0 <= entity.dna['physical']['health'] <= 1.0
        assert 0.0 <= entity.dna['reproduction']['reproduction'] <= 1.0

    def test_energy_consumption(self, entity):
        """Testet den Energieverbrauch"""
        initial_energy = entity.energy
        
        # Simuliere einen Zeitschritt
        entity.update(1.0)
        
        # Energie sollte abgenommen haben
        assert entity.energy < initial_energy
        
        # Bei maximalem Hunger sollte der Verbrauch höher sein
        entity.hunger = entity.max_hunger
        energy_before_hunger = entity.energy
        entity.update(1.0)
        energy_after_hunger = entity.energy
        
        # Der Energieverbrauch sollte mit Hunger höher sein
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
        assert entity.health >= 0  # Gesundheit kann nicht negativ sein

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
                self.quality = 1.0
                self.energy_value = 50
        
        food = MockFood()
        assert entity.eat_food(food)
        
        # Verdauungsliste sollte nicht leer sein
        assert len(entity.digesting_food) > 0
        
        # Energie sollte sich erhöhen
        initial_energy = entity.energy
        entity.update(1.0)
        assert entity.energy > initial_energy

    def test_brain_functionality(self, entity):
        """Testet die Funktionalität des neuronalen Netzwerks"""
        # Teste Brain-Inputs
        inputs = entity.get_brain_inputs()
        assert inputs.shape == (1, 8)  # 8 Input-Neuronen
        assert np.all(inputs >= -1) and np.all(inputs <= 1)  # Normalisierte Werte
        
        # Teste Brain-Outputs
        entity._update_brain(1.0)
        assert hasattr(entity, 'brain_output')
        assert entity.brain_output.shape == (1, 2)  # 2 Output-Neuronen
        
        # Teste Bewegungsanwendung
        initial_angle = entity.body.angle
        entity._apply_movement(1.0)
        assert entity.body.angle != initial_angle  # Winkel sollte sich geändert haben

    def test_fitness_calculation(self, entity):
        """Testet die Fitness-Berechnung"""
        # Teste initiale Fitness
        initial_fitness = entity.fitness
        assert initial_fitness >= 1.0  # Basis-Fitness sollte mindestens 1.0 sein
        
        # Teste Fitness mit maximalen Werten
        entity.health = entity.max_health
        entity.energy = entity.max_energy
        entity.age = 100
        entity.food_eaten = 10
        entity.distance_traveled = 1000
        entity.children = 3
        
        max_fitness = entity.fitness
        assert max_fitness > initial_fitness
        
        # Teste Fitness mit minimalen Werten
        entity.health = 0
        entity.energy = 0
        entity.age = 0
        entity.food_eaten = 0
        entity.distance_traveled = 0
        entity.children = 0
        
        min_fitness = entity.fitness
        assert min_fitness < max_fitness
        assert min_fitness >= 0  # Fitness kann nicht negativ sein

    def test_draw_preview(self, entity):
        """Testet die Vorschau-Zeichenfunktion"""
        # Erstelle eine Test-Surface
        surface = pygame.Surface((400, 400))
        
        # Teste normales Rendering
        entity.draw_preview(surface, debug_mode=False)
        
        # Teste Debug-Rendering
        entity.draw_preview(surface, debug_mode=True)
        
        # Teste Rendering mit Brain-Output
        entity._update_brain(1.0)
        entity.draw_preview(surface, debug_mode=True)
        
        # Surface sollte nicht leer sein
        assert surface.get_at((200, 200)) != (0, 0, 0, 255)

    def test_hormone_system(self, entity):
        """Testet das Hormonsystem"""
        # Teste Adrenalin-Effekt
        initial_speed = entity.base_speed
        entity.health = entity.max_health * 0.2  # Niedrige Gesundheit
        entity._update_hormones(1.0)
        assert entity.base_speed > initial_speed
        
        # Teste Testosteron-Effekt
        initial_aggression = entity.aggression
        entity.energy = entity.max_energy * 0.8  # Hohe Energie
        entity._update_hormones(1.0)
        assert entity.aggression > initial_aggression
        
        # Teste Insulin-Effekt
        initial_digestion = entity.digestion_efficiency
        entity.hunger = entity.max_hunger * 0.8  # Hoher Hunger
        entity._update_hormones(1.0)
        assert entity.digestion_efficiency > initial_digestion

    def test_draw_highlight(self, entity):
        """Testet die Hervorhebungsfunktion"""
        # Erstelle eine Test-Surface
        surface = pygame.Surface((200, 200))
        
        # Zeichne die Hervorhebung
        entity.draw_highlight(surface)
        
        # Überprüfe, ob die Surface nicht leer ist
        assert not surface.get_rect().collidepoint(100, 100) 

    def test_extreme_values(self, space):
        """Testet die Entity mit extremen Werten"""
        # Erstelle eine Entity mit maximalen DNA-Werten
        max_dna = {
            'size': 1.0,          # Maximale Größe
            'speed': 1.0,         # Maximale Geschwindigkeit
            'sense_range': 1.0,   # Maximale Sensorreichweite
            'mouth_size': 1.0,    # Maximale Mundgröße
            'digestion': 1.0,     # Maximale Verdauungseffizienz
            'metabolism': 1.0,    # Maximaler Stoffwechsel
            'mutation_rate': 1.0,  # Maximale Mutationsrate
            'aggression': 1.0,    # Maximale Aggression
            'reproduction': 1.0    # Maximale Reproduktionsneigung
        }
        max_entity = Entity(space, 100, 100, max_dna)
        
        # Setze alle Werte auf Maximum
        max_entity.energy = max_entity.max_energy
        max_entity.health = max_entity.max_health
        max_entity.hunger = max_entity.max_hunger
        max_entity.age = 1000
        max_entity.food_eaten = 1000
        max_entity.children = 1000
        max_entity.distance_traveled = 10000
        
        # Erstelle eine Test-Surface
        surface = pygame.Surface((400, 400))
        
        # Teste das Rendering
        max_entity.draw(surface)
        max_entity.draw_preview(surface)
        
        # Erstelle eine Entity mit minimalen DNA-Werten
        min_dna = {
            'size': 0.0,
            'speed': 0.0,
            'sense_range': 0.0,
            'mouth_size': 0.0,
            'digestion': 0.0,
            'metabolism': 0.0,
            'mutation_rate': 0.0,
            'aggression': 0.0,
            'reproduction': 0.0
        }
        min_entity = Entity(space, 100, 100, min_dna)
        
        # Setze alle Werte auf Minimum
        min_entity.energy = 0
        min_entity.health = 0
        min_entity.hunger = 0
        min_entity.age = 0
        min_entity.food_eaten = 0
        min_entity.children = 0
        min_entity.distance_traveled = 0
        
        # Teste das Rendering
        min_entity.draw(surface)
        min_entity.draw_preview(surface)
        
        # Teste extreme Bewegungen
        max_entity.body.velocity = (1000, 1000)  # Sehr hohe Geschwindigkeit
        min_entity.body.velocity = (0.0001, 0.0001)  # Sehr niedrige Geschwindigkeit
        
        # Update mehrmals um Stabilität zu testen
        for _ in range(100):
            max_entity.update(1.0)
            min_entity.update(1.0)
            
            # Teste das Rendering nach jedem Update
            max_entity.draw(surface)
            min_entity.draw(surface)
        
        # Teste extreme Nahrungsaufnahme
        huge_food = {
            'size': 1000,
            'quality': 1.0,
            'energy': 10000
        }
        tiny_food = {
            'size': 0.0001,
            'quality': 0.0,
            'energy': 0.0001
        }
        
        # Füge extreme Nahrung zum Verdauungssystem hinzu
        max_entity.digesting_food.append({
            'food': huge_food,
            'ticks_remaining': 100
        })
        min_entity.digesting_food.append({
            'food': tiny_food,
            'ticks_remaining': 1
        })
        
        # Update und teste Verdauung
        for _ in range(100):
            max_entity.update(1.0)
            min_entity.update(1.0)
            
            # Teste Waste-Generierung
            max_waste = max_entity.get_waste_to_create()
            min_waste = min_entity.get_waste_to_create()
            
            # Prüfe ob die Waste-Werte im gültigen Bereich sind
            for waste in max_waste:
                assert waste[0] >= 0  # Size
                assert 0 <= waste[1] <= 1  # Quality
            
            for waste in min_waste:
                assert waste[0] >= 0  # Size
                assert 0 <= waste[1] <= 1  # Quality
        
        # Teste das neuronale Netz mit Extremwerten
        max_inputs = np.ones((1, 8))  # Alle Inputs auf Maximum
        min_inputs = np.zeros((1, 8))  # Alle Inputs auf Minimum
        
        # Führe Forward-Pass durch
        max_outputs = max_entity.brain.forward(max_inputs)
        min_outputs = min_entity.brain.forward(min_inputs)
        
        # Prüfe ob die Outputs im gültigen Bereich sind (-1 bis 1 wegen tanh)
        assert np.all(max_outputs >= -1) and np.all(max_outputs <= 1)
        assert np.all(min_outputs >= -1) and np.all(min_outputs <= 1)
        
        # Teste die Visualisierung des neuronalen Netzes
        nn_surface = pygame.Surface((200, 200))
        max_entity.brain.draw(nn_surface, nn_surface.get_rect())
        min_entity.brain.draw(nn_surface, nn_surface.get_rect())
        
        # Wenn wir bis hier gekommen sind, haben alle Tests bestanden
        assert True 