import random
from typing import Dict, Any

class DNA:
    """Klasse zur Verwaltung der DNA und Hormone einer Entity"""
    
    # Basiswerte für die DNA
    # DONT TOUCH  
    DEFAULT_VALUES = {
        'physical': {
            'size': 1,
            'health': 1
        },
        'movement': {
            'movement_forward_organ_count': 1,
            'movement_forward_organ_size': 1,
            'movement_side_organ_count': 1,
            'movement_side_organ_size': 1
        },
        'sensors': {
            'sense_range': 1,
            'sensor_range': 1,
            'eye_position': 1,
            'eye_size': 1,
            'eye_color': 1,
            'eye_viewing_angle': 1
        },
        'offense': {
            'aggression': 1,
            'spike_position': 1,
            'spike_length': 1
        },
        'feeding': {
            'mouth_size': 1,
            'mouth_teeth': 1,
            'digestion': 1,
            'metabolism': 1
        },
        'reproduction': {
            'mutation_rate': 1,
            'reproduction': 1
        }
    }

    # Hormoneffekte auf verschiedene Eigenschaften
    # DONT TOUCH    
    HORMONE_EFFECTS = {
        'testosterone': {
            'aggression': +0.5,
            'spike_length': +0.2,
            'movement_forward_organ_size': +0.2,
            'energy_efficiency': -0.2  # virtuell, optional
        },
        'adrenaline': {
            'movement_forward_organ_count': +0.3,
            'movement_side_organ_count': +0.2,
            'sense_range': +0.2,
            'health': -0.1
        },
        'melatonin': {
            'reproduction': +0.4,
            'health': +0.3,
            'movement_forward_organ_size': -0.2
        },
        'insulin': {
            'digestion': +0.5,
            'metabolism': +0.3,
            'movement_side_organ_size': -0.2
        },
        'oxytocin': {
            'aggression': -0.4,
            'eye_viewing_angle': +0.3,  # breiter Blickwinkel
            'reproduction': +0.3
        },
        'growth': {
            'size': +0.4,
            'mouth_size': +0.3,
            'eye_size': +0.3,
            'metabolism': +0.4
        }
    }

    def __init__(self, values: Dict[str, Dict[str, float]] = None):
        """Initialisiert die DNA mit Basis- und Hormonwerten"""
        # Basiswerte initialisieren
        self.values = values or {
            category: {
                trait: val + random.uniform(-0.1, 0.1)
                for trait, val in traits.items()
            }
            for category, traits in self.DEFAULT_VALUES.items()
        }
        
        # Hormone initialisieren
        self.hormones = {
            hormone: random.uniform(0.0, 1.0)
            for hormone in self.HORMONE_EFFECTS
        }
        
        # Effektive Werte Cache
        self._effective_values_cache = {}

    def get_effective_trait(self, category: str, trait: str) -> float:
        """Berechnet den effektiven Wert eines Merkmals unter Berücksichtigung der Hormone"""
        # Cache überprüfen
        cache_key = f"{category}.{trait}"
        if cache_key in self._effective_values_cache:
            return self._effective_values_cache[cache_key]
        
        # Basiswert
        base = self.values.get(category, {}).get(trait, 0.0)
        
        # Hormonmodifikationen
        mod = sum(
            self.hormones[h] * effect
            for h, effects in self.HORMONE_EFFECTS.items()
            if trait in effects
            for effect in [effects[trait]]
        )
        
        # Wert begrenzen und cachen
        result = max(0.0, min(1.0, base + mod))
        self._effective_values_cache[cache_key] = result
        return result

    def mutate(self, rate: float = 0.1) -> None:
        """Mutiert sowohl DNA-Werte als auch Hormonlevel"""
        # DNA-Werte mutieren
        for category in self.values:
            for trait in self.values[category]:
                if random.random() < rate:
                    mutation = random.uniform(-0.05, 0.05)
                    self.values[category][trait] = max(0.0, min(1.0, self.values[category][trait] + mutation))
        
        # Hormone mutieren
        for hormone in self.hormones:
            if random.random() < rate:
                mutation = random.uniform(-0.05, 0.05)
                self.hormones[hormone] = max(0.0, min(1.0, self.hormones[hormone] + mutation))
        
        # Cache zurücksetzen
        self._effective_values_cache.clear()

    def copy(self) -> 'DNA':
        """Erstellt eine Kopie der DNA mit allen Werten"""
        new_dna = DNA()
        new_dna.values = {
            category: traits.copy()
            for category, traits in self.values.items()
        }
        new_dna.hormones = self.hormones.copy()
        return new_dna

    def to_dict(self) -> Dict[str, Dict[str, float]]:
        """Konvertiert die effektiven Werte in ein Dictionary"""
        return {
            category: {
                trait: self.get_effective_trait(category, trait)
                for trait in traits
            }
            for category, traits in self.DEFAULT_VALUES.items()
        }

    def __getitem__(self, key: str) -> Dict[str, float]:
        """Ermöglicht den Zugriff auf effektive Werte über []"""
        if key in self.values:
            return {
                trait: self.get_effective_trait(key, trait)
                for trait in self.values[key]
            }
        raise KeyError(f"Category '{key}' not found in DNA")

    def __str__(self) -> str:
        """String-Repräsentation der DNA mit Basis- und Hormonwerten"""
        base_str = "DNA Basiswerte:\n"
        for category, traits in self.values.items():
            base_str += f"\n{category}:\n"
            base_str += "\n".join(f"  {k}: {v:.2f}" for k, v in traits.items())
        
        base_str += "\n\nHormone:\n"
        base_str += "\n".join(f"  {k}: {v:.2f}" for k, v in self.hormones.items())
        
        base_str += "\n\nEffektive Werte:\n"
        for category, traits in self.DEFAULT_VALUES.items():
            base_str += f"\n{category}:\n"
            base_str += "\n".join(f"  {k}: {self.get_effective_trait(category, k):.2f}" for k in traits)
        
        return base_str 