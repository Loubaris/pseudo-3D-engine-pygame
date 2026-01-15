import pygame
from random import randrange
from time import sleep
import math

# Imports des modules personnalisés
from player import Player, Camera, Weapon, Gun, Bow, Inventory
from world import GameObject
from map.map import load_map

pygame.init()

# ========================= CLASSE PRINCIPALE =========================


class Game:
    """Classe principale du jeu"""
    def __init__(self):
        pygame.display.set_caption("D8 Engine")
        self.screen = pygame.display.set_mode((1000, 600))
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Chargement des images de fond
        self.background = pygame.image.load("assets/jour.png").convert_alpha()
        self.ground = pygame.image.load("assets/sol.png").convert_alpha()
        self.crosshair = pygame.image.load("assets/viseur.png").convert_alpha()
        
        # Système de viseur (auto-aim sur l'objet touché)
        self.show_crosshair = False
        self.crosshair_timer = 0.0
        self.crosshair_duration = 0.3  # 0.3 secondes
        self.crosshair_target_x = 0  # Position X de l'objet touché
        self.crosshair_target_y = 0  # Position Y de l'objet touché
        
        # Animation de balancement de tête
        self.head_bob_offset = 0.0
        
        # Game state
        self.paused = False
        self.kill_count = 0
        
        # Initialisation de la caméra et du joueur
        self.camera = Camera()
        self.player = Player()
        
        # Initialisation de l'inventaire
        self.inventory = Inventory()
        self.inventory.add_weapon(Gun())
        self.inventory.add_weapon(Bow())
        self.inventory.current_weapon_index = 1  # Commence avec l'arc
        
        # Chargement de la map depuis le fichier externe
        self.objects = load_map()
        
        print("MOTEUR DE JEU LANCÉ")
        print("Contrôles:")
        print("  W/S - Avancer/Reculer")
        print("  Q/D - Strafe gauche/droite")
        print("  SOURIS - Rotation de la tête (360°)")
        print("  ESPACE - Sauter")
        print("  HAUT/BAS - Changer d'arme")
        print("  CLIC - Tirer (pistolet)")
        print("\n🎮 Système 3D avec coordonnées X, Y, Z activé!")
        
    def handle_events(self):
        """Gère les événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                weapon = self.inventory.get_current_weapon()
                if isinstance(weapon, Gun):
                    if weapon.fire():
                        # Vérifie si un objet destructible est dans la zone de visée
                        for obj in self.objects:
                            if obj.destroyable and obj.is_in_crosshair():
                                # Affiche le viseur sur l'objet touché
                                self.show_crosshair = True
                                self.crosshair_timer = 0.0
                                self.crosshair_target_x = obj.screen_x
                                
                                # Calcul correct de la position Y du viseur (centre de l'objet affiché)
                                img_height = obj.image.get_height()
                                factor = 0.4 if obj.original_height > 400 else 0.25
                                ground_anchor_offset = 40 + (img_height * factor)
                                # Position Y du centre de l'objet affiché
                                self.crosshair_target_y = obj.screen_y - (img_height // 2) + ground_anchor_offset + self.camera.ground_y
                                
                                # Détruit l'objet (le retire de la liste)
                                self.objects.remove(obj)
                                self.kill_count += 1  # Increment kill counter
                                break  # Ne détruit qu'un seul objet par tir
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused  # Toggle pause
                elif event.key == pygame.K_DOWN:
                    self.inventory.switch_to_next()
                elif event.key == pygame.K_r:
                    # Reload weapon
                    weapon = self.inventory.get_current_weapon()
                    if isinstance(weapon, Gun):
                        weapon.start_reload()
                elif event.key == pygame.K_SPACE:
                    self.camera.start_jump()
                elif event.key == pygame.K_w:
                    self.player.move_forward()
                elif event.key == pygame.K_s:
                    self.player.move_backward()
                elif event.key == pygame.K_d:
                    self.player.move_left()
                elif event.key == pygame.K_a:
                    self.player.move_right()
                elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    self.player.start_sprint()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.camera.start_crouch()
                    
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.inventory.switch_to_previous()
                elif event.key == pygame.K_w:
                    self.player.stop_forward()
                elif event.key == pygame.K_s:
                    self.player.stop_backward()
                elif event.key == pygame.K_d:
                    self.player.stop_left()
                elif event.key == pygame.K_a:
                    self.player.stop_right()
                elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    self.player.stop_sprint()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.camera.stop_crouch()
                    
    def update(self, delta_time):
        """Met à jour le jeu"""
        if self.paused:
            return  # Don't update when paused
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # IMPORTANT: Mise à jour de l'angle AVANT le mouvement du joueur
        self.player.update_head_rotation(mouse_x)
        self.player.update(self.camera)  # Passe la caméra pour vérifier l'accroupissement
        
        # Vérifie si le joueur se déplace pour l'animation de sprint
        is_moving = (self.player.moving_forward or self.player.moving_backward or 
                     self.player.moving_left or self.player.moving_right)
        
        # Update stamina
        self.player.update_stamina(delta_time, is_moving)
        
        # Check collisions with objects
        self.player.check_collision(self.objects)
        
        # Mise à jour de la caméra
        self.camera.update_scroll(mouse_y)
        self.camera.update_jump(delta_time)
        self.camera.update_crouch(delta_time)  # Anime l'accroupissement
        
        # Animation de balancement pendant le sprint
        self.head_bob_offset = self.camera.update_head_bob(delta_time, is_moving, self.player.is_sprinting)
        self.camera.ground_y += self.head_bob_offset
        
        # Mise à jour de l'arme actuelle
        current_weapon = self.inventory.get_current_weapon()
        if current_weapon:
            current_weapon.update(delta_time)
            if not self.inventory.switching_animation['active']:
                current_weapon.update_position(mouse_x, mouse_y)
        
        # Mise à jour de l'animation de changement d'arme
        self.inventory.update_animation(delta_time)
        
        # Mise à jour du viseur
        if self.show_crosshair:
            self.crosshair_timer += delta_time
            if self.crosshair_timer >= self.crosshair_duration:
                self.show_crosshair = False
                self.crosshair_timer = 0.0
        
        # Mise à jour de la projection des objets 3D
        for obj in self.objects:
            obj.update_projection(self.player.x, self.player.y, self.player.z, self.player.angle)
            
    def draw(self):
        """Dessine tous les éléments"""
        # Fond
        self.screen.blit(self.background, (0, 0))
        
        # Sol
        self.screen.blit(self.ground, (0, self.camera.ground_y))
        
        # Trie les objets par distance au carré (plus rapide, même ordre)
        sorted_objects = sorted(
            self.objects, 
            key=lambda obj: obj.get_distance_squared(self.player.x, self.player.y, self.player.z),
            reverse=True
        )
        
        # Dessine les objets du décor dans l'ordre de profondeur
        for obj in sorted_objects:
            obj.draw(self.screen, self.camera.ground_y)
        
        # Arme (toujours au premier plan)
        if not self.inventory.switching_animation['active']:
            current_weapon = self.inventory.get_current_weapon()
            if current_weapon:
                current_weapon.draw(self.screen)
        else:
            # Pendant l'animation, on dessine l'arme qui sort
            if self.inventory.switching_animation['phase'] == 'down':
                self.inventory.switching_animation['from_weapon'].draw(self.screen)
            else:
                self.inventory.switching_animation['to_weapon'].draw(self.screen)
        
        # Viseur (affiché pendant 0.3s sur l'objet touché - auto-aim)
        if self.show_crosshair:
            crosshair_x = self.crosshair_target_x - self.crosshair.get_width() // 2
            crosshair_y = self.crosshair_target_y - self.crosshair.get_height() // 2
            self.screen.blit(self.crosshair, (crosshair_x, crosshair_y))
        
        # Affichage des infos de débogage
        font = pygame.font.Font(None, 24)
        pos_text = font.render(f"Position: X={self.player.x:.1f} Y={self.player.y:.1f} Z={self.player.z:.1f}", True, (255, 255, 255))
        angle_text = font.render(f"Angle: {math.degrees(self.player.angle):.1f}°", True, (255, 255, 255))
        speed_text = font.render(f"Vitesse: Av={self.player.speed_forward:.2f} Lat={self.player.speed_strafe:.2f}", True, (255, 255, 255))
        self.screen.blit(pos_text, (10, 10))
        self.screen.blit(angle_text, (10, 35))
        self.screen.blit(speed_text, (10, 60))
        
        # Affichage des munitions pour le pistolet
        current_weapon = self.inventory.get_current_weapon()
        if isinstance(current_weapon, Gun):
            if current_weapon.is_reloading:
                reload_progress = (current_weapon.reload_timer / current_weapon.reload_duration) * 100
                ammo_text = font.render(f"Reloading... {reload_progress:.0f}%", True, (255, 255, 0))
            else:
                ammo_text = font.render(f"Ammo: {current_weapon.munitions}/{current_weapon.reserve_ammo}", True, (255, 255, 255))
            self.screen.blit(ammo_text, (10, 85))
        
        # Stamina bar
        stamina_bar_width = 200
        stamina_bar_height = 20
        stamina_percent = self.player.stamina / self.player.max_stamina
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 110, stamina_bar_width, stamina_bar_height))
        pygame.draw.rect(self.screen, (0, 200, 255), (10, 110, int(stamina_bar_width * stamina_percent), stamina_bar_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (10, 110, stamina_bar_width, stamina_bar_height), 2)
        stamina_text = font.render("Stamina", True, (255, 255, 255))
        self.screen.blit(stamina_text, (220, 110))
        
        # Kill counter
        kill_text = font.render(f"Kills: {self.kill_count}", True, (255, 255, 100))
        self.screen.blit(kill_text, (10, 140))
        
        # Pause menu overlay
        if self.paused:
            overlay = pygame.Surface((1000, 600))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            pause_font = pygame.font.Font(None, 72)
            pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(500, 250))
            self.screen.blit(pause_text, pause_rect)
            
            info_font = pygame.font.Font(None, 32)
            info_text = info_font.render("Press ESC to resume", True, (200, 200, 200))
            info_rect = info_text.get_rect(center=(500, 330))
            self.screen.blit(info_text, info_rect)
        
        # Mini-map (top-right corner)
        self.draw_minimap()
        
        # Restaure le ground_y original après le rendu
        self.camera.ground_y -= self.head_bob_offset
        
        pygame.display.flip()
    
    def draw_minimap(self):
        """Draw a mini-map in the top-right corner"""
        minimap_size = 180
        minimap_x = 1000 - minimap_size - 10
        minimap_y = 10
        minimap_scale = 0.08  # Scale factor for world to minimap
        
        # Background
        pygame.draw.rect(self.screen, (30, 30, 30), (minimap_x, minimap_y, minimap_size, minimap_size))
        pygame.draw.rect(self.screen, (255, 255, 255), (minimap_x, minimap_y, minimap_size, minimap_size), 2)
        
        # Center of minimap
        center_x = minimap_x + minimap_size // 2
        center_y = minimap_y + minimap_size // 2
        
        # Draw objects
        for obj in self.objects:
            rel_x = (obj.x - self.player.x) * minimap_scale
            rel_z = (obj.z - self.player.z) * minimap_scale
            
            # Rotate relative to player angle
            cos_a = math.cos(-self.player.angle)
            sin_a = math.sin(-self.player.angle)
            rotated_x = rel_x * cos_a - rel_z * sin_a
            rotated_z = rel_x * sin_a + rel_z * cos_a
            
            map_x = int(center_x + rotated_x)
            map_y = int(center_y + rotated_z)
            
            # Only draw if within minimap bounds
            if minimap_x < map_x < minimap_x + minimap_size and minimap_y < map_y < minimap_y + minimap_size:
                color = (255, 100, 100) if obj.destroyable else (100, 255, 100)
                pygame.draw.circle(self.screen, color, (map_x, map_y), 3)
        
        # Draw player (center, facing up)
        pygame.draw.circle(self.screen, (255, 255, 0), (center_x, center_y), 5)
        # Direction indicator
        dir_length = 12
        end_x = center_x
        end_y = center_y - dir_length
        pygame.draw.line(self.screen, (255, 255, 0), (center_x, center_y), (end_x, end_y), 2)
        
        # Label
        label_font = pygame.font.Font(None, 18)
        label_text = label_font.render("Mini-Map", True, (255, 255, 255))
        self.screen.blit(label_text, (minimap_x + 5, minimap_y + minimap_size + 5))
        
    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            # Calcule le temps écoulé depuis la dernière frame (en secondes)
            delta_time = self.clock.tick(60) / 1000.0  # Convertit ms en secondes
            
            self.handle_events()
            self.update(delta_time)
            self.draw()


# ========================= LANCEMENT DU JEU =========================

if __name__ == "__main__":
    game = Game()
    game.run()
