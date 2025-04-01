import pygame
import sys
from PyLife.simulation import Simulation

# Globale Variablen für das Scrolling
stats_scroll_position = 0
debug_mode = False  # Debug-Modus für erweiterte Kreatur-Informationen
nn_detail_view = False  # Detailansicht für neuronales Netzwerk

def main():
    global stats_scroll_position, debug_mode, nn_detail_view
    
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
    
    # Scrolling-Einstellungen für Statistikbereich
    global stats_scroll_position
    stats_scroll_speed = 20
    is_scrollbar_dragging = False
    scrollbar_drag_start = 0
    scrollbar_width = 8
    scrollbar_margin = 2
    
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
            "D: Debug-Info ein/aus",
            "N: Neuronales Netzwerk",
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
        global stats_scroll_position
        stats_surface.fill(STATS_BACKGROUND)
        
        # Verwendung einer virtuellen Oberfläche zum Scrolling
        virtual_height = 1500  # Ausreichend groß für alle Inhalte
        virtual_stats = pygame.Surface((STATS_WIDTH, virtual_height))
        virtual_stats.fill(STATS_BACKGROUND)
        
        # Y-Position zum Zeichnen auf der virtuellen Oberfläche
        y = 8
        
        if sim.selected_entity:
            # Creature Preview Bereich
            preview_height = 150
            preview_rect = pygame.Rect(8, y, STATS_WIDTH - 16, preview_height)
            draw_panel(virtual_stats, preview_rect)
            
            # Kreatur in der Vorschau zeichnen
            preview_surface = pygame.Surface((preview_rect.width, preview_rect.height))
            preview_surface.fill(BACKGROUND_COLOR)
            sim.selected_entity.draw_preview(preview_surface, debug_mode)
            virtual_stats.blit(preview_surface, preview_rect)
            
            # Statistiken
            y += preview_height + 16
            title = title_font.render("Statistiken", True, TEXT_COLOR)
            virtual_stats.blit(title, (8, y))
            
            y += 24
            stats = [
                ("Alter", f"{sim.selected_entity.age:.1f}"),
                ("Gesundheit", f"{sim.selected_entity.health:.1f}/{sim.selected_entity.max_health:.1f}"),
                ("Energie", f"{sim.selected_entity.energy:.1f}/{sim.selected_entity.max_energy:.1f}"),
                ("Hunger", f"{sim.selected_entity.hunger:.1f}/{sim.selected_entity.max_hunger:.1f}"),
                ("Geschwindigkeit", f"{sim.selected_entity.base_speed:.1f}"),
                ("Zurückgelegt", f"{sim.selected_entity.distance_traveled:.1f}"),
                ("Nahrung gegessen", f"{sim.selected_entity.food_eaten}"),
                ("Nachkommen", f"{sim.selected_entity.children}")
            ]
            
            for label, value in stats:
                text = info_font.render(f"{label}: {value}", True, TEXT_COLOR)
                virtual_stats.blit(text, (8, y))
                y += 20
            
            # DNA Werte
            y += 8
            dna_title = title_font.render("DNA", True, TEXT_COLOR)
            virtual_stats.blit(dna_title, (8, y))
            y += 24
            
            # DNA-Werte als Dictionary abrufen
            dna_dict = sim.selected_entity.dna.to_dict()
            
            # DNA-Werte anzeigen
            for category, traits in dna_dict.items():
                # Kategorie-Überschrift
                category_text = f"{category}:"
                category_surface = info_font.render(category_text, True, TEXT_COLOR)
                virtual_stats.blit(category_surface, (8, y))
                y += 20
                
                # Traits der Kategorie
                for trait, value in traits.items():
                    text = f"  {trait}: {value:.2f}"
                    text_surface = info_font.render(text, True, TEXT_COLOR)
                    virtual_stats.blit(text_surface, (20, y))
                    y += 20
                
                y += 8  # Zusätzlicher Abstand zwischen Kategorien
            
            # Neuronales Netzwerk
            y += 16
            nn_title = title_font.render("Neurons", True, TEXT_COLOR)
            virtual_stats.blit(nn_title, (8, y))
            
            # Platz für Netzwerk-Visualisierung
            nn_height = 150
            nn_rect = pygame.Rect(8, y + 24, STATS_WIDTH - 16, nn_height)
            draw_panel(virtual_stats, nn_rect)
            
            if hasattr(sim.selected_entity, 'brain'):
                sim.selected_entity.brain.draw(virtual_stats, nn_rect)
            
            y += nn_height + 40  # Etwas zusätzlicher Platz am Ende
        
        else:
            info_text = info_font.render("Keine Kreatur ausgewählt", True, TEXT_COLOR)
            virtual_stats.blit(info_text, (8, 40))
        
        # Tatsächliche virtuelle Höhe festlegen
        virtual_height = max(HEIGHT, y)
        
        # Scrollposition anpassen, um Überscrolling zu verhindern
        max_scroll = max(0, virtual_height - HEIGHT)
        stats_scroll_position = max(0, min(stats_scroll_position, max_scroll))
        
        # Sichtbaren Bereich auf die stats_surface blitten
        stats_surface.blit(virtual_stats, (0, 0), (0, stats_scroll_position, STATS_WIDTH, HEIGHT))
        
        # Scrollindikatoren zeichnen wenn nötig
        if virtual_height > HEIGHT:
            # Oberer Indikator
            if stats_scroll_position > 0:
                pygame.draw.polygon(stats_surface, ACCENT_COLOR, [
                    (STATS_WIDTH // 2, 5),
                    (STATS_WIDTH // 2 - 10, 15),
                    (STATS_WIDTH // 2 + 10, 15)
                ])
            
            # Unterer Indikator
            if stats_scroll_position < max_scroll:
                pygame.draw.polygon(stats_surface, ACCENT_COLOR, [
                    (STATS_WIDTH // 2, HEIGHT - 5),
                    (STATS_WIDTH // 2 - 10, HEIGHT - 15),
                    (STATS_WIDTH // 2 + 10, HEIGHT - 15)
                ])
            
            # Scrollbalken
            scrollbar_x = STATS_WIDTH - scrollbar_width - scrollbar_margin
            scrollbar_height = HEIGHT * (HEIGHT / virtual_height)  # Höhe proportional zum sichtbaren Anteil
            scrollbar_y = scrollbar_margin + (HEIGHT - scrollbar_height - 2*scrollbar_margin) * (stats_scroll_position / max_scroll)
            
            # Hintergrund des Scrollbalkens
            pygame.draw.rect(stats_surface, (200, 200, 200), 
                           (scrollbar_x, scrollbar_margin, scrollbar_width, HEIGHT - 2*scrollbar_margin), 
                           0, 3)  # Abgerundete Ecken
            
            # Scrollbalken selbst
            pygame.draw.rect(stats_surface, ACCENT_COLOR, 
                           (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), 
                           0, 3)  # Abgerundete Ecken
        
        # Vertikale Trennlinie
        pygame.draw.line(screen, ACCENT_COLOR, 
                        (SIMULATION_WIDTH, 0), 
                        (SIMULATION_WIDTH, HEIGHT), 2)
    
    # Separates Fenster für detaillierte Netzansicht
    def draw_neural_network_detail():
        """Zeichnet eine detaillierte Ansicht des neuronalen Netzes in einem separaten Fenster"""
        if not sim.selected_entity or not hasattr(sim.selected_entity, 'brain'):
            return
            
        # Fenstergröße für detaillierte Ansicht
        nn_width, nn_height = 800, 600
        
        # Neues Fenster erstellen, falls nicht vorhanden
        nn_window = pygame.Surface((nn_width, nn_height))
        nn_window.fill((245, 245, 250))
        
        # Titel und Infos
        title_font = pygame.font.SysFont("Arial", 22, bold=True)
        info_font = pygame.font.SysFont("Arial", 16)
        
        # Titel
        title = title_font.render(f"Neuronales Netzwerk - Kreatur #{id(sim.selected_entity) % 1000}", True, (0, 0, 0))
        nn_window.blit(title, (20, 20))
        
        # Info zur Kreatur
        info_text = [
            f"Position: ({sim.selected_entity.body.position.x:.1f}, {sim.selected_entity.body.position.y:.1f})",
            f"Gesundheit: {sim.selected_entity.health:.1f}/{sim.selected_entity.max_health:.1f}",
            f"Energie: {sim.selected_entity.energy:.1f}/{sim.selected_entity.max_energy:.1f}",
            f"Hunger: {sim.selected_entity.hunger:.1f}/{sim.selected_entity.max_hunger:.1f}",
            f"Alter: {sim.selected_entity.age:.1f}",
            f"Nachkommen: {sim.selected_entity.children}"
        ]
        
        for i, text in enumerate(info_text):
            info_surf = info_font.render(text, True, (60, 60, 90))
            nn_window.blit(info_surf, (20, 60 + i * 25))
        
        # Großer Bereich für das neuronale Netzwerk
        nn_rect = pygame.Rect(20, 220, nn_width - 40, nn_height - 260)
        sim.selected_entity.brain.draw(nn_window, nn_rect)
        
        # Erklärungen zu den Eingaben und Ausgaben
        info_y = nn_height - 30
        input_info = info_font.render("Eingabewerte: Energie, Gesundheit, Hunger, Alter, Nahrungsdistanz, Nahrungsrichtung, Geschwindigkeit, Richtung", True, (0, 0, 0))
        output_info = info_font.render("Ausgabewerte: Vorwärts/Rückwärts (-1..1), Drehung links/rechts (-1..1)", True, (0, 0, 0))
        nn_window.blit(input_info, (20, info_y - 40))
        nn_window.blit(output_info, (20, info_y - 20))
        
        # Hinweis zum Schließen
        close_info = info_font.render("Drücke 'N' zum Schließen", True, (150, 30, 30))
        nn_window.blit(close_info, (nn_width - close_info.get_width() - 20, 20))
        
        # In die Hauptoberfläche einblenden
        main_x = (SIMULATION_WIDTH - nn_width) // 2
        main_y = (HEIGHT - nn_height) // 2
        screen.blit(nn_window, (main_x, main_y))
    
    while running:
        # Event-Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Nur Klicks in der Simulationsfläche verarbeiten, wenn kein Detailansicht geöffnet ist
                if not nn_detail_view and event.pos[0] < SIMULATION_WIDTH:
                    sim.handle_click(event.pos, event.button)
                elif event.pos[0] >= SIMULATION_WIDTH:  # Statistikbereich
                    # Berechne die relative Position innerhalb des Stats-Bereichs
                    stats_x = event.pos[0] - SIMULATION_WIDTH
                    
                    # Prüfen, ob der Klick im Bereich des Scrollbalkens ist
                    scrollbar_x = STATS_WIDTH - scrollbar_width - scrollbar_margin
                    if stats_x >= scrollbar_x:
                        # Virtuelle Höhe berechnen (vereinfacht)
                        virtual_height = 1500  # Sollte dynamisch sein, wie in draw_stats_area()
                        max_scroll = max(0, virtual_height - HEIGHT)
                        
                        if max_scroll > 0:  # Nur wenn Scrolling nötig ist
                            scrollbar_height = HEIGHT * (HEIGHT / virtual_height)
                            scrollbar_y = scrollbar_margin + (HEIGHT - scrollbar_height - 2*scrollbar_margin) * (stats_scroll_position / max_scroll)
                            
                            # Klick auf den Scrollbalken selbst
                            if scrollbar_y <= event.pos[1] <= scrollbar_y + scrollbar_height:
                                is_scrollbar_dragging = True
                                scrollbar_drag_start = event.pos[1] - scrollbar_y
                            else:
                                # Klick auf den Scrollbalken-Hintergrund - springe zur Position
                                scroll_ratio = (event.pos[1] - scrollbar_margin) / (HEIGHT - 2*scrollbar_margin)
                                stats_scroll_position = max_scroll * scroll_ratio
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Linke Maustaste
                    is_scrollbar_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if is_scrollbar_dragging:
                    # Virtuelle Höhe berechnen (vereinfacht)
                    virtual_height = 1500
                    max_scroll = max(0, virtual_height - HEIGHT)
                    
                    if max_scroll > 0:
                        scrollbar_height = HEIGHT * (HEIGHT / virtual_height)
                        scrollable_area = HEIGHT - scrollbar_height - 2*scrollbar_margin
                        
                        # Neue Position des Scrollbalkens
                        relative_y = event.pos[1] - scrollbar_drag_start - scrollbar_margin
                        scroll_ratio = max(0, min(1, relative_y / scrollable_area))
                        
                        # Neue Scrollposition
                        stats_scroll_position = max_scroll * scroll_ratio
            elif event.type == pygame.MOUSEWHEEL:
                # Mausrad-Event verarbeiten
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < SIMULATION_WIDTH:  # In der Simulationsfläche
                    sim.handle_zoom(event.y, mouse_pos)
                elif mouse_pos[0] >= SIMULATION_WIDTH:  # Im Statistikbereich
                    stats_scroll_position -= event.y * stats_scroll_speed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Nächste Generation mit Leertaste
                    sim.next_generation()
                elif event.key == pygame.K_f:
                    # Nahrung hinzufügen mit F-Taste
                    sim.spawn_food()
                elif event.key == pygame.K_d:
                    # Debug-Modus umschalten
                    debug_mode = not debug_mode
                elif event.key == pygame.K_n:
                    # Neuronales Netzwerk Detailansicht umschalten
                    if sim.selected_entity:
                        nn_detail_view = not nn_detail_view
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    # Tickrate erhöhen
                    current_tick_rate_index = min(len(TICK_RATES) - 1, current_tick_rate_index + 1)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    # Tickrate verringern
                    current_tick_rate_index = max(0, current_tick_rate_index - 1)
                # Pfeiltasten zum Scrollen
                elif event.key == pygame.K_UP:
                    stats_scroll_position -= stats_scroll_speed
                elif event.key == pygame.K_DOWN:
                    stats_scroll_position += stats_scroll_speed
        
        # Simulation aktualisieren, wenn keine Detailansicht aktiv ist
        if not nn_detail_view:
            dt = 1.0 / FPS
            sim.update(dt * TICK_RATES[current_tick_rate_index])
        
        # Simulation zeichnen
        sim_surface.fill(BACKGROUND_COLOR)
        sim.draw(sim_surface, debug_mode)  # Debug-Modus übergeben
        
        # Alles auf den Hauptbildschirm zeichnen
        screen.blit(sim_surface, (0, 0))  # Simulation
        draw_ui()  # UI aktualisieren
        screen.blit(ui_surface, (0, 0))  # UI
        draw_stats_area()  # Stats zeichnen
        screen.blit(stats_surface, (SIMULATION_WIDTH, 0))  # Stats
        
        # Neuronales Netzwerk Detailansicht zeichnen, wenn aktiv
        if nn_detail_view:
            draw_neural_network_detail()
            
        pygame.display.flip()
        
        # FPS begrenzen
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 