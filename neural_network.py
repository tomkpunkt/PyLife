import numpy as np
import tensorflow as tf
import pygame

class NeuralNetwork:
    def __init__(self):
        # Einfaches neuronales Netz mit:
        # - 8 Eingabeneuronen (für Sensoren)
        # - 16 versteckte Neuronen
        # - 4 Ausgabeneuronen (für Bewegungssteuerung)
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(16, activation='relu', input_shape=(8,)),
            tf.keras.layers.Dense(4, activation='tanh')
        ])
        
        # Optimizer und Loss-Funktion
        self.model.compile(
            optimizer='adam',
            loss='mse'
        )
        
    def predict(self, inputs):
        """Gibt Vorhersagen basierend auf den Eingaben zurück"""
        # Eingaben normalisieren
        inputs = np.array(inputs).reshape(1, -1)
        return self.model.predict(inputs, verbose=0)[0]
    
    def mutate(self, mutation_rate=0.1):
        """Mutiert die Gewichte des neuronalen Netzes"""
        weights = self.model.get_weights()
        for i in range(len(weights)):
            mask = np.random.random(weights[i].shape) < mutation_rate
            mutation = np.random.normal(0, 0.1, weights[i].shape)
            weights[i] = np.where(mask, weights[i] + mutation, weights[i])
        self.model.set_weights(weights)
    
    def crossover(self, other):
        """Kreuzt dieses Netz mit einem anderen"""
        new_network = NeuralNetwork()
        weights1 = self.model.get_weights()
        weights2 = other.model.get_weights()
        
        new_weights = []
        for w1, w2 in zip(weights1, weights2):
            mask = np.random.random(w1.shape) < 0.5
            new_w = np.where(mask, w1, w2)
            new_weights.append(new_w)
            
        new_network.model.set_weights(new_weights)
        return new_network
        
    def draw(self, surface, rect):
        """Visualisiert das neuronale Netzwerk"""
        # Farben
        NODE_COLOR = (70, 130, 180)  # Blau für Neuronen
        ACTIVE_COLOR = (100, 200, 100)  # Grün für aktive Verbindungen
        INACTIVE_COLOR = (200, 100, 100)  # Rot für inaktive Verbindungen
        
        # Schichten definieren
        layers = [8, 16, 4]  # Eingabe, versteckt, Ausgabe
        
        # Abstand und Größe berechnen
        padding = 20
        node_radius = min(
            (rect.height - 2 * padding) / (max(layers) * 2),
            (rect.width - 2 * padding) / (len(layers) * 4)
        )
        
        # Gewichte des Netzwerks holen
        weights = self.model.get_weights()
        
        # Positionen für alle Neuronen berechnen
        positions = []
        for layer_idx, layer_size in enumerate(layers):
            layer_positions = []
            x = rect.x + padding + (rect.width - 2 * padding) * layer_idx / (len(layers) - 1)
            for i in range(layer_size):
                y = rect.y + padding + (rect.height - 2 * padding) * i / (layer_size - 1)
                layer_positions.append((x, y))
            positions.append(layer_positions)
        
        # Verbindungen zeichnen
        for layer_idx in range(len(layers) - 1):
            weight_matrix = weights[layer_idx * 2]  # Gewichte zwischen den Schichten
            for i, pos1 in enumerate(positions[layer_idx]):
                for j, pos2 in enumerate(positions[layer_idx + 1]):
                    weight = weight_matrix[i, j]
                    # Farbe basierend auf Gewicht
                    if abs(weight) < 0.1:
                        continue  # Sehr schwache Verbindungen nicht zeichnen
                    color = ACTIVE_COLOR if weight > 0 else INACTIVE_COLOR
                    alpha = min(255, int(abs(weight) * 255))
                    pygame.draw.line(surface, (*color, alpha), pos1, pos2, 1)
        
        # Neuronen zeichnen
        for layer_positions in positions:
            for x, y in layer_positions:
                # Äußerer Kreis (dunklerer Rand)
                pygame.draw.circle(surface, (40, 80, 120), (int(x), int(y)), 
                                 int(node_radius))
                # Innerer Kreis (heller)
                pygame.draw.circle(surface, NODE_COLOR, (int(x), int(y)), 
                                 int(node_radius - 1))
                # Glanzpunkt
                pygame.draw.circle(surface, (150, 200, 255), 
                                 (int(x - node_radius/3), int(y - node_radius/3)), 
                                 int(node_radius/4)) 