import numpy as np
import pygame

class Brain:
    def __init__(self, input_size, hidden_size, output_size):
        """Initialisiert das neuronale Netzwerk"""
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Gewichte und Biases initialisieren
        self.weights1 = np.random.randn(input_size, hidden_size) * 0.01
        self.weights2 = np.random.randn(hidden_size, output_size) * 0.01
        self.bias1 = np.zeros((1, hidden_size))
        self.bias2 = np.zeros((1, output_size))
        
        # Aktivierungszustände
        self.layers = []
        
    def forward(self, inputs):
        """Führt einen Vorwärtsdurchlauf durch"""
        # Input Layer
        self.layers = [inputs]
        
        # Hidden Layer
        hidden = np.dot(inputs, self.weights1) + self.bias1
        hidden = np.tanh(hidden)
        self.layers.append(hidden)
        
        # Output Layer
        output = np.dot(hidden, self.weights2) + self.bias2
        output = np.tanh(output)
        self.layers.append(output)
        
        return output
    
    def draw(self, surface, rect):
        """Zeichnet eine vereinfachte Visualisierung des neuronalen Netzes"""
        # Berechne die Position relativ zum Kamera-Offset und Zoom
        x = rect.x
        y = rect.y
        width = rect.width
        height = rect.height
        
        # Hintergrund
        pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height))
        
        # Wenn keine Layer vorhanden sind, zeichne ein einfaches Netzwerk
        if not self.layers:
            # Standard-Layer-Größen
            layer_sizes = [self.input_size, self.hidden_size, self.output_size]
            layer_spacing = width / (len(layer_sizes) + 1)
            neuron_spacing = height / (max(layer_sizes) + 1)
            neuron_radius = min(width, height) * 0.03  # Kleinerer Radius
            
            # Layer für Layer zeichnen
            for i, size in enumerate(layer_sizes):
                layer_x = x + (i + 1) * layer_spacing
                layer_y = y + (height - size * neuron_spacing) / 2
                
                # Neuronen in diesem Layer
                for j in range(size):
                    neuron_y = layer_y + j * neuron_spacing
                    pygame.draw.circle(surface, (100, 100, 100), 
                                     (int(layer_x), int(neuron_y)), 
                                     int(neuron_radius))
                
                # Verbindungen zum nächsten Layer
                if i < len(layer_sizes) - 1:
                    next_size = layer_sizes[i + 1]
                    next_layer_x = x + (i + 2) * layer_spacing
                    next_layer_y = y + (height - next_size * neuron_spacing) / 2
                    
                    # Gewichtungen für die Verbindungen
                    if i == 0:
                        weights = self.weights1
                    else:
                        weights = self.weights2
                    
                    for j in range(size):
                        for k in range(next_size):
                            # Gewichtung bestimmt die Linienfarbe und -stärke
                            weight = float(weights[j, k])  # Konvertierung zu float
                            color = [200, 200, 200]  # Standardfarbe grau
                            thickness = 1
                            
                            if abs(weight) > 0.2:  # Nur stärkere Verbindungen farbig
                                if weight > 0:
                                    # Positive Gewichtung: Grün
                                    color = [0, min(255, int(200 * weight)), 0]
                                else:
                                    # Negative Gewichtung: Rot
                                    color = [min(255, int(200 * -weight)), 0, 0]
                                thickness = max(1, int(2 * abs(weight)))
                            
                            pygame.draw.line(surface, tuple(color),
                                           (int(layer_x), int(layer_y + j * neuron_spacing)),
                                           (int(next_layer_x), int(next_layer_y + k * neuron_spacing)),
                                           thickness)
        else:
            # Neuronen zeichnen
            neuron_radius = min(width, height) * 0.03  # Kleinerer Radius
            layer_spacing = width / (len(self.layers) + 1)
            
            # Maximale Layer-Größe bestimmen
            max_neurons = max(layer.shape[1] if len(layer.shape) > 1 else layer.shape[0] 
                            for layer in self.layers)
            neuron_spacing = height / (max_neurons + 1)
            
            # Layer für Layer zeichnen
            for i, layer in enumerate(self.layers):
                layer_x = x + (i + 1) * layer_spacing
                layer_neurons = layer.shape[1] if len(layer.shape) > 1 else layer.shape[0]
                layer_y = y + (height - layer_neurons * neuron_spacing) / 2
                
                # Neuronen in diesem Layer
                for j in range(layer_neurons):
                    neuron_y = layer_y + j * neuron_spacing
                    
                    # Neuron zeichnen
                    color = [100, 100, 100]  # Standardfarbe
                    neuron_value = float(layer[0, j] if len(layer.shape) > 1 else layer[j])
                    if abs(neuron_value) > 0.2:  # Nur stärkere Aktivierungen farbig
                        if neuron_value > 0:
                            color = [0, min(255, int(200 * neuron_value)), 0]  # Grün für positive Aktivierung
                        else:
                            color = [min(255, int(200 * -neuron_value)), 0, 0]  # Rot für negative Aktivierung
                    
                    pygame.draw.circle(surface, tuple(color), 
                                     (int(layer_x), int(neuron_y)), 
                                     int(neuron_radius))
                    
                    # Verbindungen zum nächsten Layer
                    if i < len(self.layers) - 1:
                        next_layer = self.layers[i + 1]
                        next_layer_x = x + (i + 2) * layer_spacing
                        next_neurons = next_layer.shape[1] if len(next_layer.shape) > 1 else next_layer.shape[0]
                        next_layer_y = y + (height - next_neurons * neuron_spacing) / 2
                        
                        # Gewichtungen für die Verbindungen
                        if i == 0:
                            weights = self.weights1
                        else:
                            weights = self.weights2
                        
                        for k in range(next_neurons):
                            next_neuron_y = next_layer_y + k * neuron_spacing
                            
                            # Gewichtung bestimmt die Linienfarbe und -stärke
                            weight = float(weights[j, k])  # Konvertierung zu float
                            color = [200, 200, 200]  # Standardfarbe grau
                            thickness = 1
                            
                            if abs(weight) > 0.2:  # Nur stärkere Verbindungen farbig
                                if weight > 0:
                                    # Positive Gewichtung: Grün
                                    color = [0, min(255, int(200 * weight)), 0]
                                else:
                                    # Negative Gewichtung: Rot
                                    color = [min(255, int(200 * -weight)), 0, 0]
                                thickness = max(1, int(2 * abs(weight)))
                            
                            pygame.draw.line(surface, tuple(color),
                                           (int(layer_x), int(neuron_y)),
                                           (int(next_layer_x), int(next_neuron_y)),
                                           thickness) 