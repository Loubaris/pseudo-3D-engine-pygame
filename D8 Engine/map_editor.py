"""Éditeur de map avec vue top-down pour créer facilement des niveaux"""
import pygame
import sys

pygame.init()

class MapEditor:
    """Éditeur de map top-down"""
    def __init__(self):
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("D8 Engine - Map Editor")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Caméra de l'éditeur (vue top-down)
        self.camera_x = 0
        self.camera_z = 0
        self.camera_speed = 10
        
        # Échelle de la vue (pixels par unité 3D)
        self.scale = 0.5  # 1 unité 3D = 0.5 pixel
        
        # Liste des objets placés
        self.objects = []
        
        # Objet sélectionné pour modification
        self.selected_object = None
        
        # Copier-coller
        self.copied_object = None
        
        # Drag and drop
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_z = 0
        
        # Grid snapping
        self.snap_to_grid = False
        self.grid_size = 50  # Grid cell size
        
        # Undo/Redo
        self.history = []  # List of states for undo
        self.history_index = -1
        self.max_history = 50
        
        # Multi-select
        self.selected_objects = []  # Multiple selection support
        
        # Police pour le texte
        self.font = pygame.font.Font(None, 16)
        self.font_large = pygame.font.Font(None, 24)
        
        # Couleurs
        self.bg_color = (40, 40, 40)
        self.grid_color = (60, 60, 60)
        self.object_color = (100, 200, 100)
        self.selected_color = (255, 200, 50)
        self.text_color = (255, 255, 255)
        
        # Mode d'édition
        self.show_input_dialog = False
        self.input_fields = {
            'texture': '',
            'y': '0',
            'destroyable': 'False'
        }
        self.active_field = 'texture'
        self.temp_position = (0, 0)  # Position temporaire pour le nouvel objet
        
    def world_to_screen(self, x, z):
        """Convertit les coordonnées 3D (x, z) en coordonnées écran"""
        screen_x = 600 + (x - self.camera_x) * self.scale
        screen_y = 400 + (z - self.camera_z) * self.scale
        return int(screen_x), int(screen_y)
    
    def screen_to_world(self, screen_x, screen_y):
        """Convertit les coordonnées écran en coordonnées 3D (x, z)"""
        x = (screen_x - 600) / self.scale + self.camera_x
        z = (screen_y - 400) / self.scale + self.camera_z
        
        # Apply grid snapping if enabled
        if self.snap_to_grid:
            x = round(x / self.grid_size) * self.grid_size
            z = round(z / self.grid_size) * self.grid_size
        
        return x, z
    
    def save_state(self):
        """Save current state for undo/redo"""
        # Remove any states after current index
        self.history = self.history[:self.history_index + 1]
        
        # Deep copy current state
        import copy
        state = copy.deepcopy(self.objects)
        self.history.append(state)
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.history_index += 1
    
    def undo(self):
        """Undo last action"""
        if self.history_index > 0:
            self.history_index -= 1
            import copy
            self.objects = copy.deepcopy(self.history[self.history_index])
            self.selected_object = None
            self.selected_objects = []
    
    def redo(self):
        """Redo last undone action"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            import copy
            self.objects = copy.deepcopy(self.history[self.history_index])
            self.selected_object = None
            self.selected_objects = []
    
    def handle_events(self):
        """Gère les événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    if not self.show_input_dialog:
                        # Vérifier si on clique sur un objet existant
                        mouse_x, mouse_y = event.pos
                        clicked_object = None
                        
                        for obj in self.objects:
                            sx, sy = self.world_to_screen(obj['x'], obj['z'])
                            if abs(sx - mouse_x) < 20 and abs(sy - mouse_y) < 20:
                                clicked_object = obj
                                break
                        
                        if clicked_object:
                            # Multi-select with Shift
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                if clicked_object in self.selected_objects:
                                    self.selected_objects.remove(clicked_object)
                                else:
                                    self.selected_objects.append(clicked_object)
                                self.selected_object = clicked_object
                            else:
                                # Single select and start drag
                                self.selected_object = clicked_object
                                self.selected_objects = [clicked_object]
                                self.dragging = True
                                world_x, world_z = self.screen_to_world(mouse_x, mouse_y)
                                self.drag_offset_x = clicked_object['x'] - world_x
                                self.drag_offset_z = clicked_object['z'] - world_z
                        else:
                            # Ouvrir la boîte de dialogue pour créer un nouvel objet
                            world_x, world_z = self.screen_to_world(mouse_x, mouse_y)
                            self.temp_position = (world_x, world_z)
                            self.show_input_dialog = True
                            self.input_fields = {
                                'texture': '',
                                'y': '0',
                                'destroyable': 'False'
                            }
                            self.active_field = 'texture'
                            
                elif event.button == 3:  # Clic droit - supprimer
                    if self.selected_object:
                        self.objects.remove(self.selected_object)
                        self.selected_object = None
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Relâchement clic gauche
                    self.dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.selected_object:
                    # Déplacer l'objet avec la souris
                    mouse_x, mouse_y = event.pos
                    world_x, world_z = self.screen_to_world(mouse_x, mouse_y)
                    self.selected_object['x'] = round(world_x + self.drag_offset_x, 2)
                    self.selected_object['z'] = round(world_z + self.drag_offset_z, 2)
            
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom avec la molette de la souris
                if event.y > 0:  # Scroll up - zoom in
                    self.scale = min(2.0, self.scale + 0.05)
                elif event.y < 0:  # Scroll down - zoom out
                    self.scale = max(0.1, self.scale - 0.05)
                        
            elif event.type == pygame.KEYDOWN:
                if self.show_input_dialog:
                    # Gestion de la saisie dans la boîte de dialogue
                    if event.key == pygame.K_RETURN:
                        # Valider et créer l'objet
                        self.create_object()
                    elif event.key == pygame.K_ESCAPE:
                        # Annuler
                        self.show_input_dialog = False
                    elif event.key == pygame.K_TAB:
                        # Changer de champ
                        fields = ['texture', 'y', 'destroyable']
                        current_index = fields.index(self.active_field)
                        self.active_field = fields[(current_index + 1) % len(fields)]
                    elif event.key == pygame.K_BACKSPACE:
                        # Effacer un caractère
                        if self.input_fields[self.active_field]:
                            self.input_fields[self.active_field] = self.input_fields[self.active_field][:-1]
                    else:
                        # Ajouter le caractère
                        if event.unicode.isprintable():
                            self.input_fields[self.active_field] += event.unicode
                else:
                    # Navigation and shortcuts
                    if event.key == pygame.K_g:
                        # Toggle grid snap (G key)
                        self.snap_to_grid = not self.snap_to_grid
                        print(f"Grid snap: {'ON' if self.snap_to_grid else 'OFF'}")
                    elif event.key == pygame.K_DELETE and self.selected_object:
                        self.save_state()
                        for obj in self.selected_objects:
                            if obj in self.objects:
                                self.objects.remove(obj)
                        self.selected_object = None
                        self.selected_objects = []
                    elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Undo (Ctrl+Z)
                        self.undo()
                        print("Undo")
                    elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Redo (Ctrl+Y)
                        self.redo()
                        print("Redo")
                    elif event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Quick duplicate (Ctrl+D)
                        if self.selected_object:
                            self.save_state()
                            new_obj = self.selected_object.copy()
                            new_obj['x'] += 50
                            new_obj['z'] += 50
                            self.objects.append(new_obj)
                            self.selected_object = new_obj
                            self.selected_objects = [new_obj]
                            print("Object duplicated!")
                    elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Save (Ctrl+S)
                        self.export_map()
                    elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Copy (Ctrl+C)
                        if self.selected_object:
                            self.copied_object = self.selected_object.copy()
                            print("Object copied!")
                    elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Paste (Ctrl+V)
                        if self.copied_object:
                            self.save_state()
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            world_x, world_z = self.screen_to_world(mouse_x, mouse_y)
                            new_object = self.copied_object.copy()
                            new_object['x'] = round(world_x, 2)
                            new_object['z'] = round(world_z, 2)
                            self.objects.append(new_object)
                            self.selected_object = new_object
                            self.selected_objects = [new_object]
                            print("Object pasted!")
    
    def create_object(self):
        """Crée un nouvel objet avec les paramètres saisis"""
        texture = self.input_fields['texture'].strip()
        if not texture:
            self.show_input_dialog = False
            return
        
        try:
            y = float(self.input_fields['y'])
        except ValueError:
            y = 0.0
        
        destroyable = self.input_fields['destroyable'].strip().lower() in ['true', '1', 'yes', 'oui']
        
        self.save_state()  # Save state before adding new object
        
        new_object = {
            'texture': texture,
            'x': round(self.temp_position[0], 2),
            'y': y,
            'z': round(self.temp_position[1], 2),
            'destroyable': destroyable
        }
        
        self.objects.append(new_object)
        self.selected_object = new_object
        self.selected_objects = [new_object]
        self.show_input_dialog = False
    
    def update(self):
        """Met à jour la logique de l'éditeur"""
        if not self.show_input_dialog:
            keys = pygame.key.get_pressed()
            
            # Déplacement de la caméra
            if keys[pygame.K_UP]:
                self.camera_z -= self.camera_speed
            if keys[pygame.K_DOWN]:
                self.camera_z += self.camera_speed
            if keys[pygame.K_LEFT]:
                self.camera_x -= self.camera_speed
            if keys[pygame.K_RIGHT]:
                self.camera_x += self.camera_speed
            
            # Zoom
            if keys[pygame.K_PLUS] or keys[pygame.K_KP_PLUS]:
                self.scale = min(2.0, self.scale + 0.01)
            if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
                self.scale = max(0.1, self.scale - 0.01)
    
    def draw_grid(self):
        """Dessine la grille de fond"""
        grid_size = 100  # Taille de la grille en unités 3D
        
        # Lignes verticales
        start_x = int(self.camera_x / grid_size) * grid_size - grid_size
        for i in range(-5, 30):
            x = start_x + i * grid_size
            sx1, sy1 = self.world_to_screen(x, self.camera_z - 2000)
            sx2, sy2 = self.world_to_screen(x, self.camera_z + 2000)
            if -100 < sx1 < 1300:
                pygame.draw.line(self.screen, self.grid_color, (sx1, sy1), (sx2, sy2), 1)
        
        # Lignes horizontales
        start_z = int(self.camera_z / grid_size) * grid_size - grid_size
        for i in range(-5, 30):
            z = start_z + i * grid_size
            sx1, sy1 = self.world_to_screen(self.camera_x - 2000, z)
            sx2, sy2 = self.world_to_screen(self.camera_x + 2000, z)
            if -100 < sy1 < 900:
                pygame.draw.line(self.screen, self.grid_color, (sx1, sy1), (sx2, sy2), 1)
    
    def draw_objects(self):
        """Dessine tous les objets placés"""
        for obj in self.objects:
            sx, sy = self.world_to_screen(obj['x'], obj['z'])
            
            # Dessine un carré pour l'objet
            is_selected = obj == self.selected_object or obj in self.selected_objects
            color = self.selected_color if is_selected else self.object_color
            rect_size = 40
            rect = pygame.Rect(sx - rect_size // 2, sy - rect_size // 2, rect_size, rect_size)
            pygame.draw.rect(self.screen, color, rect, 0)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
            
            # Affiche le nom de la texture (court)
            texture_name = obj['texture'].split('/')[-1].replace('.png', '')
            text = self.font.render(texture_name, True, self.text_color)
            text_rect = text.get_rect(center=(sx, sy - rect_size // 2 - 10))
            self.screen.blit(text, text_rect)
            
            # Affiche les coordonnées en petit
            coords_text = f"({obj['x']:.0f}, {obj['z']:.0f})"
            coords_surface = self.font.render(coords_text, True, (200, 200, 200))
            coords_rect = coords_surface.get_rect(center=(sx, sy + rect_size // 2 + 10))
            self.screen.blit(coords_surface, coords_rect)
    
    def draw_ui(self):
        """Dessine l'interface utilisateur"""
        # Panneau d'informations en haut
        info_texts = [
            "D8 Engine - Map Editor",
            f"Camera: ({self.camera_x:.0f}, {self.camera_z:.0f}) | Scale: {self.scale:.2f}x",
            f"Objects: {len(self.objects)} | Selected: {len(self.selected_objects)}",
            f"Grid Snap: {'ON' if self.snap_to_grid else 'OFF'} (G to toggle)",
            "",
            "Controls:",
            "Arrows: Move camera | +/- : Zoom | G: Toggle grid snap",
            "Left Click: Place/Drag | Shift+Click: Multi-select | Right Click: Delete",
            "Ctrl+C: Copy | Ctrl+V: Paste | Ctrl+D: Duplicate | Ctrl+S: Export",
            "Ctrl+Z: Undo | Ctrl+Y: Redo | Delete: Remove selected"
        ]
        
        y_offset = 10
        for text in info_texts:
            if text == "D8 Engine - Map Editor":
                surface = self.font_large.render(text, True, (255, 255, 100))
            else:
                surface = self.font.render(text, True, self.text_color)
            self.screen.blit(surface, (10, y_offset))
            y_offset += 20 if text else 10
        
        # Affiche les infos de l'objet sélectionné
        if self.selected_object:
            y_offset = 500
            selected_texts = [
                "=== Selected Object ===",
                f"Texture: {self.selected_object['texture']}",
                f"Position: ({self.selected_object['x']:.1f}, {self.selected_object['y']:.1f}, {self.selected_object['z']:.1f})",
                f"Destroyable: {self.selected_object['destroyable']}"
            ]
            for text in selected_texts:
                surface = self.font.render(text, True, (255, 255, 100))
                self.screen.blit(surface, (10, y_offset))
                y_offset += 20
        
        # Object list panel (right side)
        self.draw_object_list()
    
    def draw_object_list(self):
        """Draw a list of all objects on the right side"""
        panel_x = 950
        panel_y = 200
        panel_width = 240
        panel_height = 590
        
        # Background
        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title
        title = self.font_large.render("Object List", True, (255, 255, 100))
        self.screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Statistics
        tree_count = sum(1 for obj in self.objects if 'tree' in obj['texture'].lower())
        statue_count = sum(1 for obj in self.objects if 'statue' in obj['texture'].lower())
        destroyable_count = sum(1 for obj in self.objects if obj['destroyable'])
        
        stats = [
            f"Total: {len(self.objects)}",
            f"Trees: {tree_count}",
            f"Statues: {statue_count}",
            f"Destroyable: {destroyable_count}"
        ]
        
        y_offset = panel_y + 40
        for stat in stats:
            stat_surface = self.font.render(stat, True, (200, 200, 200))
            self.screen.blit(stat_surface, (panel_x + 10, y_offset))
            y_offset += 18
        
        # Separator
        pygame.draw.line(self.screen, (100, 100, 100), (panel_x + 10, y_offset + 5), (panel_x + panel_width - 10, y_offset + 5), 1)
        y_offset += 15
        
        # Object list (scrollable)
        max_display = 20
        start_index = max(0, len(self.objects) - max_display)
        
        for i, obj in enumerate(self.objects[start_index:], start=start_index):
            if y_offset > panel_y + panel_height - 25:
                break
            
            texture_name = obj['texture'].split('/')[-1].replace('.png', '')
            is_selected = obj in self.selected_objects
            color = (255, 255, 100) if is_selected else (180, 180, 180)
            
            obj_text = f"{i+1}. {texture_name[:15]}"
            obj_surface = self.font.render(obj_text, True, color)
            self.screen.blit(obj_surface, (panel_x + 10, y_offset))
            y_offset += 18
    
    def draw_input_dialog(self):
        """Dessine la boîte de dialogue de saisie"""
        if not self.show_input_dialog:
            return
        
        # Fond semi-transparent
        overlay = pygame.Surface((1200, 800))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Boîte de dialogue
        dialog_rect = pygame.Rect(300, 250, 600, 300)
        pygame.draw.rect(self.screen, (50, 50, 50), dialog_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), dialog_rect, 3)
        
        # Titre
        title = self.font_large.render("Create New Object", True, (255, 255, 100))
        self.screen.blit(title, (dialog_rect.centerx - title.get_width() // 2, dialog_rect.y + 20))
        
        # Champs de saisie
        y_offset = dialog_rect.y + 70
        fields_info = [
            ('texture', 'Texture Path (e.g., assets/statue.png):'),
            ('y', 'Y Position (height):'),
            ('destroyable', 'Destroyable (True/False):')
        ]
        
        for field_name, label in fields_info:
            # Label
            label_surface = self.font.render(label, True, self.text_color)
            self.screen.blit(label_surface, (dialog_rect.x + 20, y_offset))
            y_offset += 25
            
            # Champ de saisie
            field_rect = pygame.Rect(dialog_rect.x + 20, y_offset, 560, 30)
            color = (255, 255, 100) if field_name == self.active_field else (100, 100, 100)
            pygame.draw.rect(self.screen, color, field_rect, 2)
            
            # Texte dans le champ
            text_surface = self.font.render(self.input_fields[field_name], True, self.text_color)
            self.screen.blit(text_surface, (field_rect.x + 5, field_rect.y + 7))
            
            y_offset += 45
        
        # Instructions
        instructions = [
            "Press TAB to switch fields",
            "Press ENTER to create object",
            "Press ESCAPE to cancel"
        ]
        y_offset += 10
        for instruction in instructions:
            inst_surface = self.font.render(instruction, True, (200, 200, 200))
            self.screen.blit(inst_surface, (dialog_rect.x + 20, y_offset))
            y_offset += 20
    
    def draw(self):
        """Dessine tout"""
        self.screen.fill(self.bg_color)
        
        # Dessine la grille
        self.draw_grid()
        
        # Dessine les axes (origine)
        origin_x, origin_y = self.world_to_screen(0, 0)
        pygame.draw.line(self.screen, (255, 0, 0), (origin_x - 20, origin_y), (origin_x + 20, origin_y), 3)
        pygame.draw.line(self.screen, (0, 0, 255), (origin_x, origin_y - 20), (origin_x, origin_y + 20), 3)
        
        # Dessine les objets
        self.draw_objects()
        
        # Dessine l'UI
        self.draw_ui()
        
        # Dessine la boîte de dialogue si active
        self.draw_input_dialog()
        
        pygame.display.flip()
    
    def export_map(self):
        """Exporte la map dans un fichier Python"""
        filename = "map/map.py"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\"\"\"Fichier de map pour D8 Engine\"\"\"\n")
            f.write("from world import GameObject\n\n")
            f.write("def load_map():\n")
            f.write("    \"\"\"Retourne la liste des objets de la map\"\"\"\n")
            f.write("    return [\n")
            
            for obj in self.objects:
                f.write(f"        GameObject(\"{obj['texture']}\", x={obj['x']}, y={obj['y']}, z={obj['z']}, destroyable={obj['destroyable']}),\n")
            
            f.write("    ]\n")
        
        print(f"Map exported to {filename} with {len(self.objects)} objects!")
    
    def run(self):
        """Boucle principale"""
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    editor = MapEditor()
    editor.run()
