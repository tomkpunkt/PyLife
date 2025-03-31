# PyLife Evolution Simulation

Eine 2D-Top-Down-Simulation von Kreaturen mit neuronalen Netzen und evolutionären Eigenschaften.

## Features
- Prozedural generierte Kreaturen mit individuellen Eigenschaften
- Neuronale Netze für Entscheidungsfindung
- Physik-basierte Bewegung und Kollisionserkennung
- Evolutionäres System mit DNA-Vererbung
- Detaillierte Statistiken und Visualisierungen
- Interaktive Benutzeroberfläche

## Installation

1. Python 3.12 oder höher installieren
2. Repository klonen oder herunterladen
3. Abhängigkeiten installieren:
```bash
python -m pip install -r requirements.txt
```

## Ausführung
```bash
python main.py
```

## Steuerung
- **Linksklick**: Kreatur auswählen/abwählen
- **Leertaste**: Nächste Generation starten
- **F**: Nahrung hinzufügen
- **+/-**: Simulationsgeschwindigkeit anpassen

## Technische Details

### Kreaturen
- Prozedural generierte Körper mit:
  - Variabler Größe und Form
  - Anpassbarer Anzahl von Augen
  - Bewegungsorganen
  - Stacheln oder Auswüchsen

### DNA-System
- Vererbbare Eigenschaften:
  - Größe und Geschwindigkeit
  - Energieeffizienz
  - Sensorreichweite
  - Gesundheit
  - Fortpflanzungsrate
  - Visuelle Merkmale

### Neuronales Netzwerk
- 8 Eingabeneuronen für Umgebungswahrnehmung
- 16 versteckte Neuronen
- 4 Ausgabeneuronen für Bewegungssteuerung
- Evolutionäre Anpassung durch Mutation und Kreuzung

### Benutzeroberfläche
- Permanentes Statistik-Panel
- Kreaturvorschau
- Echtzeit-Statistiken
- Visualisierung des neuronalen Netzwerks
- Übersichtliche Steuerungselemente

## Projektstruktur
- `main.py`: Hauptprogramm und UI
- `entity.py`: Kreatur-Implementierung
- `simulation.py`: Simulationslogik
- `neural_network.py`: KI-Komponente
- `creature_renderer.py`: Visuelle Darstellung 