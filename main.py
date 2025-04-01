import pygame
import sys
from simulation import Simulation

def main():
    # Initialize Pygame
    pygame.init()
    
    # Simulationsparameter
    STATS_WIDTH = 200  # Breite des Statistikbereichs
    SIMULATION_WIDTH = 1200  # Breite der Simulationsfläche
    TOTAL_WIDTH = SIMULATION_WIDTH + STATS_WIDTH
    HEIGHT = 800
    FPS = 60
    
    # Hauptfenster erstellen
    screen = pygame.display.set_mode((TOTAL_WIDTH, HEIGHT))
    pygame.display.set_caption("PyLife Evolution Simulation")
    
    # Separate Surfaces für UI, Simulation und Stats
    ui_surface = pygame.Surface((TOTAL_WIDTH, HEIGHT), pygame.SRCALPHA)
    sim_surface = pygame.Surface((SIMULATION_WIDTH, HEIGHT))
    stats_surface = pygame.Surface((STATS_WIDTH, HEIGHT))
    
    # Tickrate-Einstellungen
    TICK_RATES = [0.25, 0.5, 1.0, 2.0, 4.0]  # Verschiedene Tickraten
    current_tick_rate_index = 2  # Start bei 1.0
    
    # Farben
    BACKGROUND_COLOR = (240, 240, 245)  # Hellgrauer Hintergrund
    TEXT_COLOR = (50, 50, 60)  # Dunkles Grau für Text
    PANEL_COLOR = (255, 255, 255)  # Weiß für Panels
    ACCENT_COLOR = (70, 130, 180)  # Stahlblau für Akzente
    STATS_BACKGROUND = (245, 245, 250)  # Noch helleres Grau für Stats
    
    # Simulation erstellen
    sim = Simulation(SIMULATION_WIDTH, HEIGHT)
    
    # Erste Generation von Entities erstellen
    for _ in range(10):
        sim.spawn_entity()
    
    # Nahrung erstellen
    for _ in range(30):
        sim.spawn_food()
    
    # Spielschleife
    clock = pygame.time.Clock()
    running = True
    
    # Fonts
    try:
        title_font = pygame.font.SysFont("Arial", 19, bold=True)
        info_font = pygame.font.SysFont("Arial", 16)
    except:
        title_font = pygame.font.Font(None, 29)
        info_font = pygame.font.Font(None, 22)
    
    def draw_panel(surface, rect, color=PANEL_COLOR, alpha=200):
        """Zeichnet ein halbtransparentes Panel"""
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((*color, alpha))
        pygame.draw.rect(panel, (*ACCENT_COLOR, alpha), panel.get_rect(), 2)
        surface.blit(panel, rect)
    
    def draw_ui():
        """Zeichnet die UI-Elemente"""
        ui_surface.fill((0, 0, 0, 0))  # Transparenten Hintergrund
        
        # Info Panel (oben rechts in der Simulationsfläche)
        info_panel = pygame.Rect(SIMULATION_WIDTH - 200, 10, 190, 80)
        draw_panel(ui_surface, info_panel)
        
        # FPS und Tickrate anzeigen
        fps_text = info_font.render(f"FPS: {int(clock.get_fps())}", True, TEXT_COLOR)
        tick_text = info_font.render(f"Tickrate: {TICK_RATES[current_tick_rate_index]}x", True, TEXT_COLOR)
        gen_text = info_font.render(f"Generation: {sim.generation}", True, TEXT_COLOR)
        
        # Text im Info Panel positionieren
        ui_surface.blit(gen_text, (info_panel.x + 10, info_panel.y + 10))
        ui_surface.blit(fps_text, (info_panel.x + 10, info_panel.y + 30))
        ui_surface.blit(tick_text, (info_panel.x + 10, info_panel.y + 50))
        
        # Steuerungspanel (oben links)
        controls = [
            "Steuerung",
            "+/-: Tickrate ändern",
            "F: Nahrung hinzufügen",
            "Leertaste: Nächste Generation",
            "Linksklick: Entity auswählen"
        ]
        
        control_panel = pygame.Rect(10, 10, 200, len(controls) * 20 + 12)  # Höhe angepasst
        draw_panel(ui_surface, control_panel)
        
        # Steuerungstext zeichnen
        for i, text in enumerate(controls):
            if i == 0:  # Überschrift
                text_surface = title_font.render(text, True, TEXT_COLOR)
            else:
                text_surface = info_font.render(text, True, TEXT_COLOR)
            ui_surface.blit(text_surface, (control_panel.x + 8, control_panel.y + 8 + i * 20))  # Abstände angepasst
    
    def draw_stats_area():
        """Zeichnet den permanenten Statistikbereich"""
        stats_surface.fill(STATS_BACKGROUND)
        
        # Creature Preview Bereich
        preview_height = 150
        preview_rect = pygame.Rect(8, 8, STATS_WIDTH - 16, preview_height)  # Ränder angepasst
        draw_panel(stats_surface, preview_rect)
        
        if sim.selected_entity:
            # Kreatur in der Vorschau zeichnen
            preview_surface = pygame.Surface((preview_rect.width, preview_rect.height))
            preview_surface.fill(BACKGROUND_COLOR)
            sim.selected_entity.draw_preview(preview_surface)
            stats_surface.blit(preview_surface, preview_rect)
            
            # Statistiken
            y = preview_height + 16  # Abstand reduziert
            title = title_font.render("Statistiken", True, TEXT_COLOR)
            stats_surface.blit(title, (8, y))
            
            y += 24  # Abstand reduziert
            stats = [
                ("Alter", f"{sim.selected_entity.age}"),
                ("Gesundheit", f"{sim.selected_entity.health:.1f}/{sim.selected_entity.max_health}"),
                ("Energie", f"{sim.selected_entity.energy:.1f}/{sim.selected_entity.max_energy}"),
                ("Hunger", f"{sim.selected_entity.hunger:.1f}/{sim.selected_entity.max_hunger}"),
                ("Geschwindigkeit", f"{sim.selected_entity.speed:.1f}"),
                ("Zurückgelegt", f"{sim.selected_entity.distance_traveled:.1f}"),
                ("Nahrung gegessen", f"{sim.selected_entity.food_eaten}"),
                ("Nachkommen", f"{sim.selected_entity.children}")
            ]
            
            for label, value in stats:
                text = info_font.render(f"{label}: {value}", True, TEXT_COLOR)
                stats_surface.blit(text, (8, y))
                y += 20  # Zeilenabstand reduziert
            
            # DNA Werte
            y += 8  # Abstand reduziert
            dna_title = title_font.render("DNA", True, TEXT_COLOR)
            stats_surface.blit(dna_title, (8, y))
            y += 24  # Abstand reduziert
            
            for key, value in sim.selected_entity.dna.items():
                text = info_font.render(f"{key}: {value:.2f}", True, TEXT_COLOR)
                stats_surface.blit(text, (16, y))  # Einrückung angepasst
                y += 20  # Zeilenabstand reduziert
            
            # Neuronales Netzwerk
            y += 16  # Abstand reduziert
            nn_title = title_font.render("Neurons", True, TEXT_COLOR)
            stats_surface.blit(nn_title, (8, y))
            
            # Platz für Netzwerk-Visualisierung
            nn_height = 150
            nn_rect = pygame.Rect(8, y + 24, STATS_WIDTH - 16, nn_height)  # Abstände angepasst
            draw_panel(stats_surface, nn_rect)
            
            if hasattr(sim.selected_entity, 'brain'):
                sim.selected_entity.brain.draw(stats_surface, nn_rect)
        
        else:
            info_text = info_font.render("Keine Kreatur ausgewählt", True, TEXT_COLOR)
            stats_surface.blit(info_text, (8, 40))  # Position angepasst
        
        # Vertikale Trennlinie
        pygame.draw.line(screen, ACCENT_COLOR, 
                        (SIMULATION_WIDTH, 0), 
                        (SIMULATION_WIDTH, HEIGHT), 2)
    
    while running:
        # Event-Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Nur Klicks in der Simulationsfläche verarbeiten
                if event.pos[0] < SIMULATION_WIDTH:
                    sim.handle_click(event.pos, event.button)
            elif event.type == pygame.MOUSEWHEEL:
                # Mausrad-Event verarbeiten
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < SIMULATION_WIDTH:  # Nur in der Simulationsfläche
                    sim.handle_zoom(event.y, mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Nächste Generation mit Leertaste
                    sim.next_generation()
                elif event.key == pygame.K_f:
                    # Nahrung hinzufügen mit F-Taste
                    sim.spawn_food()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    # Tickrate erhöhen
                    current_tick_rate_index = min(len(TICK_RATES) - 1, current_tick_rate_index + 1)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    # Tickrate verringern
                    current_tick_rate_index = max(0, current_tick_rate_index - 1)
        
        # Simulation aktualisieren
        dt = 1.0 / FPS
        sim.update(dt * TICK_RATES[current_tick_rate_index])
        
        # Simulation zeichnen
        sim_surface.fill(BACKGROUND_COLOR)
        sim.draw(sim_surface)  # Simulation auf separate Surface zeichnen
        
        # Alles auf den Hauptbildschirm zeichnen
        screen.blit(sim_surface, (0, 0))  # Simulation
        draw_ui()  # UI aktualisieren
        screen.blit(ui_surface, (0, 0))  # UI
        draw_stats_area()  # Stats zeichnen
        screen.blit(stats_surface, (SIMULATION_WIDTH, 0))  # Stats
        
        pygame.display.flip()
        
        # FPS begrenzen
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 