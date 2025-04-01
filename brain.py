import numpy as np
import pygame

class Brain:
    def __init__(self, input_size, hidden_size, output_size, values=None):
        """Initialisiert das neuronale Netzwerk"""
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        if values is None:
            # Zufällige Initialisierung der Gewichte und Biases
            self.weights_ih = np.random.uniform(-1.0, 1.0, (hidden_size, input_size))
            self.weights_ho = np.random.uniform(-1.0, 1.0, (output_size, hidden_size))
            self.bias_h = np.random.uniform(-1.0, 1.0, hidden_size)
            self.bias_o = np.random.uniform(-1.0, 1.0, output_size)
        else:
            # Gewichte und Biases aus den übergebenen Werten setzen
            self.weights_ih = values['weights_ih']
            self.weights_ho = values['weights_ho']
            self.bias_h = values['bias_h']
            self.bias_o = values['bias_o']
        
        # Speicher für die Aktivierungswerte
        self.hidden_values = np.zeros(hidden_size)
        self.output_values = np.zeros(output_size)
        
        # Eingabewerte speichern für die Visualisierung
        self.input_values = np.zeros(input_size)
        
        # Namen der Eingabeneuronen für die Visualisierung
        self.input_names = [
            "Energie", "Gesundheit", "Hunger", "Alter", 
            "Nahrungsdist", "Nahrungsricht", "Geschw.", "Richtung"
        ]
        
        # Namen der Ausgabeneuronen für die Visualisierung
        self.output_names = ["Vorwärts", "Drehung"]
        
    def forward(self, inputs):
        """Führt einen Vorwärtsdurchlauf durch"""
        # Eingabewerte für die Visualisierung speichern
        self.input_values = inputs.flatten()
        
        # Input Layer
        self.layers = [inputs]
        
        # Hidden Layer (korrigierte Matrix-Multiplikation)
        hidden = np.dot(inputs, self.weights_ih.T) + self.bias_h
        self.hidden_values = np.tanh(hidden).flatten()
        self.layers.append(hidden)
        
        # Output Layer
        output = np.dot(self.hidden_values.reshape(1, -1), self.weights_ho.T) + self.bias_o
        self.output_values = np.tanh(output).flatten()
        self.layers.append(output)
        
        # Neuronenwerte für die Visualisierung speichern
        self.neuron_values = {
            'input': inputs.flatten(),
            'hidden': self.hidden_values,
            'output': self.output_values
        }
        
        return output
    
    def draw(self, surface, rect):
        """Zeichnet das neuronale Netzwerk im angegebenen Rechteck"""
        # Hintergrund für das neuronale Netzwerk
        pygame.draw.rect(surface, (240, 240, 245), rect, border_radius=10)
        pygame.draw.rect(surface, (200, 200, 210), rect, 2, border_radius=10)
        
        # Titel, wenn Platz vorhanden
        if rect.height > 120:
            title_font = pygame.font.SysFont("Arial", 18, bold=True)
            title = title_font.render("Neuronales Netzwerk", True, (50, 50, 70))
            surface.blit(title, (rect.x + (rect.width - title.get_width()) // 2, rect.y + 10))
        
        # Abstände und Größen berechnen
        padding_x = 40 if rect.width > 300 else 20
        padding_y = 40 if rect.height > 200 else 20
        
        # Verfügbarer Platz
        available_width = rect.width - 2 * padding_x
        available_height = rect.height - 2 * padding_y
        
        # Position für jede Neuronenebene
        input_x = rect.x + padding_x
        hidden_x = rect.x + rect.width // 2
        output_x = rect.x + rect.width - padding_x
        
        # Höhe für jede Ebene
        input_height = available_height
        hidden_height = available_height
        output_height = available_height
        
        # Abstand zwischen Neuronen
        input_spacing = input_height / (self.input_size + 1)
        hidden_spacing = hidden_height / (self.hidden_size + 1)
        output_spacing = output_height / (self.output_size + 1)
        
        # Farben für die Visualisierung
        neuron_color = (100, 100, 150)
        connection_color_pos = (0, 150, 0)  # Grün für positive Gewichte
        connection_color_neg = (150, 0, 0)  # Rot für negative Gewichte
        
        # Beschriftungsgröße basierend auf verfügbarem Platz
        label_size = max(10, min(14, int(rect.width / 40)))
        font_size = max(10, min(12, int(rect.width / 50)))
        label_font = pygame.font.SysFont("Arial", label_size, bold=True)
        neuron_font = pygame.font.SysFont("Arial", font_size)
        
        # Positionen der Neuronen berechnen
        input_positions = []
        for i in range(self.input_size):
            y = rect.y + padding_y + (i + 1) * input_spacing
            input_positions.append((input_x, y))
        
        hidden_positions = []
        for i in range(self.hidden_size):
            y = rect.y + padding_y + (i + 1) * hidden_spacing
            hidden_positions.append((hidden_x, y))
        
        output_positions = []
        for i in range(self.output_size):
            y = rect.y + padding_y + (i + 1) * output_spacing
            output_positions.append((output_x, y))
        
        # Verbindungen zwischen Eingabe- und versteckter Ebene zeichnen
        for i in range(self.input_size):
            for h in range(self.hidden_size):
                weight = self.weights_ih[h, i]
                color = connection_color_pos if weight > 0 else connection_color_neg
                # Alpha-Wert (Transparenz) basierend auf Gewichtsstärke
                alpha = int(min(255, abs(weight) * 200))
                # Liniendicke basierend auf Gewichtsstärke
                thickness = max(1, min(4, int(abs(weight) * 3)))
                
                # Linie mit Alpha-Wert zeichnen
                line_color = (*color, alpha)
                pygame.draw.line(
                    surface, line_color, 
                    input_positions[i], hidden_positions[h], 
                    thickness
                )
        
        # Verbindungen zwischen versteckter und Ausgabeebene zeichnen
        for h in range(self.hidden_size):
            for o in range(self.output_size):
                # Gewicht bestimmen für Farbintensität
                weight = self.weights_ho[o, h]
                # Farbintensität basierend auf Gewicht
                if weight > 0:
                    color = (200, 240, 200, int(min(255, abs(weight) * 150)))
                else:
                    color = (240, 200, 200, int(min(255, abs(weight) * 150)))
                pygame.draw.line(surface, color, hidden_positions[h], output_positions[o], 1)
        
        # Neuronenradius basierend auf Fenstergröße
        neuron_radius = min(10, max(5, int(rect.width / 60)))
        
        # Eingabeneuronen zeichnen
        for i, pos in enumerate(input_positions):
            # Farbintensität basierend auf Aktivierung
            activation = max(0, min(1, (self.input_values[i] + 1) / 2))
            color = (
                int(200 * (1 - activation) + 50 * activation),
                int(50 * (1 - activation) + 200 * activation),
                int(100)
            )
            
            # Neuron zeichnen
            pygame.draw.circle(surface, color, pos, neuron_radius)
            pygame.draw.circle(surface, (50, 50, 70), pos, neuron_radius, 1)
            
            # Beschriftung, wenn Platz vorhanden
            if rect.width > 400 and i < len(self.input_names):
                label = label_font.render(self.input_names[i], True, (50, 50, 70))
                surface.blit(label, (pos[0] - label.get_width() - 5, pos[1] - label.get_height() // 2))
                
                # Wert anzeigen
                value_str = f"{self.input_values[i]:.2f}"
                value_surf = neuron_font.render(value_str, True, (80, 80, 100))
                surface.blit(value_surf, (pos[0] - value_surf.get_width() - 5, pos[1] + 5))
        
        # Versteckte Neuronen zeichnen
        for i, pos in enumerate(hidden_positions):
            # Farbintensität basierend auf Aktivierung
            activation = max(0, min(1, (self.hidden_values[i] + 1) / 2))
            color = (
                int(200 * (1 - activation) + 50 * activation),
                int(50 * (1 - activation) + 200 * activation),
                int(100)
            )
            
            # Neuron zeichnen
            pygame.draw.circle(surface, color, pos, neuron_radius)
            pygame.draw.circle(surface, (50, 50, 70), pos, neuron_radius, 1)
            
            # Aktivierungswert, wenn Platz vorhanden
            if rect.width > 500:
                value_str = f"{self.hidden_values[i]:.2f}"
                value_surf = neuron_font.render(value_str, True, (80, 80, 100))
                surface.blit(value_surf, (pos[0] - value_surf.get_width() // 2, pos[1] + neuron_radius + 2))
        
        # Ausgabeneuronen zeichnen
        for i, pos in enumerate(output_positions):
            # Farbintensität basierend auf Aktivierung
            activation = max(0, min(1, (self.output_values[i] + 1) / 2))
            color = (
                int(200 * (1 - activation) + 50 * activation),
                int(50 * (1 - activation) + 200 * activation),
                int(100)
            )
            
            # Neuron zeichnen
            pygame.draw.circle(surface, color, pos, neuron_radius)
            pygame.draw.circle(surface, (50, 50, 70), pos, neuron_radius, 1)
            
            # Beschriftung, wenn Platz vorhanden
            if rect.width > 400 and i < len(self.output_names):
                label = label_font.render(self.output_names[i], True, (50, 50, 70))
                surface.blit(label, (pos[0] + 5, pos[1] - label.get_height() // 2))
                
                # Wert anzeigen
                value_str = f"{self.output_values[i]:.2f}"
                value_surf = neuron_font.render(value_str, True, (80, 80, 100))
                surface.blit(value_surf, (pos[0] + 5, pos[1] + 5))
        
        # Ebenen-Labels, wenn genug Platz vorhanden
        if rect.height > 150:
            layer_font = pygame.font.SysFont("Arial", 16, bold=True)
            
            input_label = layer_font.render("Eingabe", True, (50, 50, 70))
            hidden_label = layer_font.render("Versteckt", True, (50, 50, 70))
            output_label = layer_font.render("Ausgabe", True, (50, 50, 70))
            
            surface.blit(input_label, (input_x - input_label.get_width() // 2, rect.y + rect.height - 25))
            surface.blit(hidden_label, (hidden_x - hidden_label.get_width() // 2, rect.y + rect.height - 25))
            surface.blit(output_label, (output_x - output_label.get_width() // 2, rect.y + rect.height - 25))
            
        # Legende für Gewichte
        if rect.width > 500 and rect.height > 300:
            legend_font = pygame.font.SysFont("Arial", 14)
            legend_y = rect.y + rect.height - 60
            
            # Positive Gewichte
            pygame.draw.line(surface, connection_color_pos, (rect.x + 20, legend_y), (rect.x + 50, legend_y), 3)
            pos_text = legend_font.render("Positive Gewichte", True, (50, 50, 70))
            surface.blit(pos_text, (rect.x + 55, legend_y - pos_text.get_height() // 2))
            
            # Negative Gewichte
            pygame.draw.line(surface, connection_color_neg, (rect.x + 20, legend_y + 20), (rect.x + 50, legend_y + 20), 3)
            neg_text = legend_font.render("Negative Gewichte", True, (50, 50, 70))
            surface.blit(neg_text, (rect.x + 55, legend_y + 20 - neg_text.get_height() // 2))

    # Kompaktere Debug-Version für die Kreaturenansicht
    def draw_compact(self, surface, rect):
        """Zeichnet eine kompaktere Version des Netzwerks für die Debug-Ansicht"""
        padding = 5
        neuron_radius = max(2, min(3, rect.width // 50))
        
        # Hintergrund
        pygame.draw.rect(surface, (240, 240, 245), rect, border_radius=5)
        pygame.draw.rect(surface, (200, 200, 210), rect, 1, border_radius=5)
        
        # Verfügbarer Platz
        available_width = rect.width - 2 * padding
        available_height = rect.height - 2 * padding - 14  # Platz für Text unten freihalten
        
        # Position für jede Neuronenebene
        input_x = rect.x + padding + neuron_radius + 2
        hidden_x = rect.x + rect.width // 2
        output_x = rect.x + rect.width - padding - neuron_radius - 2
        
        # Höhe für jede Ebene
        input_height = available_height
        hidden_height = available_height
        output_height = available_height
        
        # Abstand zwischen Neuronen
        input_spacing = input_height / (self.input_size + 1)
        hidden_spacing = hidden_height / (self.hidden_size + 1)
        output_spacing = output_height / (self.output_size + 1)
        
        # Titel
        tiny_font = pygame.font.SysFont("Arial", 8)
        title = tiny_font.render("Neural Network", True, (50, 50, 70))
        surface.blit(title, (rect.centerx - title.get_width() // 2, rect.y + 2))
        
        # Positionen der Neuronen berechnen
        input_positions = []
        for i in range(self.input_size):
            y = rect.y + padding + 10 + (i + 1) * input_spacing
            input_positions.append((input_x, y))
        
        hidden_positions = []
        for i in range(self.hidden_size):
            y = rect.y + padding + 10 + (i + 1) * hidden_spacing
            hidden_positions.append((hidden_x, y))
        
        output_positions = []
        for i in range(self.output_size):
            y = rect.y + padding + 10 + (i + 1) * output_spacing
            output_positions.append((output_x, y))
        
        # Verbindungen zeichnen (vereinfacht)
        for i in range(self.input_size):
            for h in range(self.hidden_size):
                # Gewicht bestimmen für Farbintensität
                weight = self.weights_ih[h, i]
                # Farbintensität basierend auf Gewicht
                if weight > 0:
                    color = (200, 240, 200, int(min(255, abs(weight) * 150)))
                else:
                    color = (240, 200, 200, int(min(255, abs(weight) * 150)))
                pygame.draw.line(surface, color, input_positions[i], hidden_positions[h], 1)
        
        for h in range(self.hidden_size):
            for o in range(self.output_size):
                # Gewicht bestimmen für Farbintensität
                weight = self.weights_ho[o, h]
                # Farbintensität basierend auf Gewicht
                if weight > 0:
                    color = (200, 240, 200, int(min(255, abs(weight) * 150)))
                else:
                    color = (240, 200, 200, int(min(255, abs(weight) * 150)))
                pygame.draw.line(surface, color, hidden_positions[h], output_positions[o], 1)
        
        # Neuronen zeichnen
        for i, pos in enumerate(input_positions):
            activation = max(0, min(1, (self.input_values[i] + 1) / 2))
            color = (
                int(200 * (1 - activation) + 50 * activation),
                int(50 * (1 - activation) + 200 * activation),
                int(100)
            )
            pygame.draw.circle(surface, color, pos, neuron_radius)
            
        for i, pos in enumerate(hidden_positions):
            activation = max(0, min(1, (self.hidden_values[i] + 1) / 2))
            color = (
                int(200 * (1 - activation) + 50 * activation),
                int(50 * (1 - activation) + 200 * activation),
                int(100)
            )
            pygame.draw.circle(surface, color, pos, neuron_radius)
            
        for i, pos in enumerate(output_positions):
            activation = max(0, min(1, (self.output_values[i] + 1) / 2))
            color = (
                int(200 * (1 - activation) + 50 * activation),
                int(50 * (1 - activation) + 200 * activation),
                int(100)
            )
            pygame.draw.circle(surface, color, pos, neuron_radius)
            
        # Output-Werte kompakt anzeigen (unten im Rechteck)
        output_text_y = rect.bottom - 12
        f_color = (0, 150, 0) if self.output_values[0] > 0 else (150, 0, 0)
        t_color = (0, 150, 0) if self.output_values[1] > 0 else (150, 0, 0)
        
        f_text = tiny_font.render(f"F: {self.output_values[0]:.2f}", True, f_color)
        t_text = tiny_font.render(f"T: {self.output_values[1]:.2f}", True, t_color)
        
        # Zentriere die Texte
        f_text_x = rect.x + rect.width // 4 - f_text.get_width() // 2
        t_text_x = rect.x + 3 * rect.width // 4 - t_text.get_width() // 2
        
        surface.blit(f_text, (f_text_x, output_text_y))
        surface.blit(t_text, (t_text_x, output_text_y)) 