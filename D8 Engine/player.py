"""Module contenant les classes liées au joueur, armes et inventaire"""
import pygame
from audioplayer import AudioPlayer
import math


class Weapon:
    """Classe de base pour les armes"""
    def __init__(self, name, image_path, fire_image_path=None, sound_path=None):
        self.name = name
        self.image = pygame.image.load(image_path).convert_alpha()
        self.fire_image = pygame.image.load(fire_image_path).convert_alpha() if fire_image_path else None
        self.sound = AudioPlayer(sound_path) if sound_path else None
        self.x = 350
        self.y = 305
        self.is_firing = False
        self.fire_timer = 0.0  # Timer en secondes
        self.fire_duration = 0.3  # Durée du flash de tir (0.3 secondes)
        self.animation_state = 0
        self.animation_time = 0
        
    def fire(self):
        """Tire avec l'arme"""
        if self.sound:
            self.sound.play()
        self.is_firing = True
        self.fire_timer = 0.0
        
    def update(self, delta_time):
        """Met à jour l'état de l'arme"""
        if self.is_firing:
            self.fire_timer += delta_time
            if self.fire_timer >= self.fire_duration:
                self.is_firing = False
                self.fire_timer = 0.0
            
    def draw(self, screen):
        """Dessine l'arme"""
        if self.is_firing and self.fire_image:
            screen.blit(self.fire_image, (self.x, self.y))
        else:
            screen.blit(self.image, (self.x, self.y))
            
    def update_position(self, mouse_x, mouse_y, base_y):
        """Met à jour la position de l'arme selon la souris"""
        # Mouvement vertical
        if mouse_y < 250:
            if self.y > base_y - 55:
                self.y -= 1
        elif mouse_y > 360:
            if self.y < base_y + 15:
                self.y += 1
        
        # Mouvement horizontal
        if mouse_x >= 600:
            if self.x < 430:
                self.x += 1
        elif mouse_x <= 365:
            if self.x > 320:
                self.x -= 1


class Gun(Weapon):
    """Classe pour le pistolet"""
    def __init__(self):
        super().__init__(
            "Pistolet",
            "assets/gun.png",
            "assets/gunfire.png",
            "assets/fire.mp3"
        )
        self.y = 305
        self.munitions = 10
        
    def fire(self):
        """Tire avec le pistolet si munitions disponibles"""
        if self.munitions > 0:
            super().fire()
            self.munitions -= 1
            return True
        return False
        
    def update_position(self, mouse_x, mouse_y):
        super().update_position(mouse_x, mouse_y, 305)


class Bow(Weapon):
    """Classe pour l'arc"""
    def __init__(self):
        super().__init__(
            "Arc",
            "assets/arc.png"
        )
        self.y = 35
        
    def update_position(self, mouse_x, mouse_y):
        # Mouvement vertical spécifique à l'arc
        if mouse_y < 250:
            if self.y > -80:
                self.y -= 1
        elif mouse_y > 360:
            if self.y < 50:
                self.y += 1
        
        # Mouvement horizontal
        if mouse_x >= 600:
            if self.x < 430:
                self.x += 1
        elif mouse_x <= 365:
            if self.x > 320:
                self.x -= 1


class Inventory:
    """Classe pour gérer l'inventaire d'armes"""
    def __init__(self):
        self.weapons = []
        self.current_weapon_index = 0
        self.switching_animation = {
            'active': False,
            'from_weapon': None,
            'to_weapon': None,
            'timer': 0.0,  # Timer en secondes
            'phase': 'down'  # 'down' ou 'up'
        }
        self.switch_duration = 0.3  # Durée de chaque phase (descente/montée)
        
    def add_weapon(self, weapon):
        """Ajoute une arme à l'inventaire"""
        self.weapons.append(weapon)
        
    def get_current_weapon(self):
        """Retourne l'arme actuellement équipée"""
        if self.weapons:
            return self.weapons[self.current_weapon_index]
        return None
        
    def switch_to_next(self):
        """Passe à l'arme suivante avec animation"""
        if len(self.weapons) > 1 and not self.switching_animation['active']:
            current = self.get_current_weapon()
            self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapons)
            next_weapon = self.get_current_weapon()
            
            self.switching_animation['active'] = True
            self.switching_animation['from_weapon'] = current
            self.switching_animation['to_weapon'] = next_weapon
            self.switching_animation['timer'] = 0.0
            self.switching_animation['phase'] = 'down'
            
    def switch_to_previous(self):
        """Passe à l'arme précédente avec animation"""
        if len(self.weapons) > 1 and not self.switching_animation['active']:
            current = self.get_current_weapon()
            self.current_weapon_index = (self.current_weapon_index - 1) % len(self.weapons)
            previous = self.get_current_weapon()
            
            self.switching_animation['active'] = True
            self.switching_animation['from_weapon'] = current
            self.switching_animation['to_weapon'] = previous
            self.switching_animation['timer'] = 0.0
            self.switching_animation['phase'] = 'down'
            
    def update_animation(self, delta_time):
        """Met à jour l'animation de changement d'arme"""
        if self.switching_animation['active']:
            self.switching_animation['timer'] += delta_time
            
            if self.switching_animation['phase'] == 'down':
                # Animation de descente de l'arme actuelle
                from_weapon = self.switching_animation['from_weapon']
                progress = self.switching_animation['timer'] / self.switch_duration
                
                if isinstance(from_weapon, Gun):
                    from_weapon.y = 305 + (600 - 305) * progress
                elif isinstance(from_weapon, Bow):
                    from_weapon.y = 35 + (600 - 35) * progress
                    
                if self.switching_animation['timer'] >= self.switch_duration:
                    self.switching_animation['phase'] = 'up'
                    self.switching_animation['timer'] = 0.0
                            
            elif self.switching_animation['phase'] == 'up':
                # Animation de montée de la nouvelle arme
                to_weapon = self.switching_animation['to_weapon']
                progress = self.switching_animation['timer'] / self.switch_duration
                
                if isinstance(to_weapon, Gun):
                    to_weapon.y = 600 - (600 - 305) * progress
                elif isinstance(to_weapon, Bow):
                    to_weapon.y = 600 - (600 - 35) * progress
                    
                if self.switching_animation['timer'] >= self.switch_duration:
                    if isinstance(to_weapon, Gun):
                        to_weapon.y = 305
                    elif isinstance(to_weapon, Bow):
                        to_weapon.y = 35
                    self.switching_animation['active'] = False


class Camera:
    """Classe pour gérer la caméra et le défilement"""
    def __init__(self):
        self.ground_y = 0
        self.saved_ground_y = 0  # Sauvegarde de la position avant le saut
        self.is_crouching = False  # État d'accroupissement
        self.crouch_offset = -40  # Décalage vers le bas quand accroupi
        self.crouch_animation_timer = 0.0
        self.crouch_animation_duration = 0.2  # Durée de l'animation (0.2 secondes)
        self.crouch_animating = False
        self.crouch_direction = 0  # 1 = descendre, -1 = monter
        self.jump_state = 'idle'  # 'idle', 'prepare', 'jumping', 'descending'
        self.jump_timer = 0.0
        self.jump_velocity = 0.0
        
        # Animation de balancement pendant le sprint
        self.head_bob_timer = 0.0
        self.head_bob_amplitude = 2.0  # Amplitude très minime (pixels)
        self.head_bob_frequency = 2.5  # Fréquence du balancement (cycles par seconde) - très doux
        
        # Paramètres du saut (ajustés pour la plage de vision étendue)
        self.prepare_duration = 0.15  # Durée de préparation (secondes)
        self.jump_gravity = -1000.0  # Gravité augmentée
        self.jump_force = 450.0  # Force de saut augmentée pour être plus visible
        
        self.jump_sound = AudioPlayer("assets/jump.wav")
        self.landing_sound = AudioPlayer("assets/landing.wav")
        
    def update_scroll(self, mouse_y):
        """Met à jour le défilement vertical selon la souris avec paliers de vitesse"""
        # Ne permet pas de scroller si on saute
        if self.jump_state != 'idle' or self.is_crouching:
            return
            
        # Paliers pour regarder vers le haut (y < 300)
        if mouse_y < 150:  # Zone rapide
            scroll_speed = 3.0
        elif mouse_y < 250:  # Zone moyenne
            scroll_speed = 1.5
        elif mouse_y < 300:  # Zone lente
            scroll_speed = 0.6
        # Paliers pour regarder vers le bas (y > 300)
        elif mouse_y > 450:  # Zone rapide
            scroll_speed = -3.0
        elif mouse_y > 375:  # Zone moyenne
            scroll_speed = -1.5
        elif mouse_y > 300:  # Zone lente
            scroll_speed = -0.6
        else:  # Zone centrale (300-300) - pas de mouvement
            scroll_speed = 0
            
        # Applique le scroll avec les limites
        new_ground_y = self.ground_y + scroll_speed
        self.ground_y = max(-120, min(80, new_ground_y))
                
    def start_crouch(self):
        """Commence à s'accroupir"""
        if self.jump_state == 'idle' and not self.is_crouching and not self.crouch_animating:
            self.saved_ground_y = self.ground_y
            self.crouch_animating = True
            self.crouch_animation_timer = 0.0
            self.crouch_direction = 1  # Descendre
    
    def stop_crouch(self):
        """Arrête de s'accroupir"""
        if self.is_crouching and not self.crouch_animating:
            self.crouch_animating = True
            self.crouch_animation_timer = 0.0
            self.crouch_direction = -1  # Remonter
    
    def update_crouch(self, delta_time):
        """Met à jour l'animation d'accroupissement"""
        if self.crouch_animating:
            self.crouch_animation_timer += delta_time
            progress = self.crouch_animation_timer / self.crouch_animation_duration
            
            if progress >= 1.0:
                # Animation terminée
                self.crouch_animating = False
                if self.crouch_direction == 1:
                    # Accroupissement terminé
                    self.is_crouching = True
                    self.ground_y = self.saved_ground_y + self.crouch_offset
                else:
                    # Relèvement terminé
                    self.is_crouching = False
                    self.ground_y = self.saved_ground_y
            else:
                # Animation en cours
                if self.crouch_direction == 1:
                    # Descendre progressivement
                    self.ground_y = self.saved_ground_y + (self.crouch_offset * progress)
                else:
                    # Remonter progressivement
                    current_offset = self.crouch_offset * (1.0 - progress)
                    self.ground_y = self.saved_ground_y + current_offset
                
    def start_jump(self):
        """Démarre un saut"""
        if self.jump_state == 'idle' and not self.is_crouching:
            self.saved_ground_y = self.ground_y  # Sauvegarde la position actuelle
            self.jump_state = 'prepare'
            self.jump_timer = 0.0
            
    def update_jump(self, delta_time):
        """Met à jour l'animation de saut"""
        if self.jump_state == 'prepare':
            # Phase de préparation (accroupissement plus prononcé)
            self.jump_timer += delta_time
            progress = self.jump_timer / self.prepare_duration
            self.ground_y = self.saved_ground_y - (30 * progress)  # Descend de 30px depuis la position sauvée
            
            if self.jump_timer >= self.prepare_duration:
                self.jump_state = 'jumping'
                self.jump_velocity = self.jump_force
                self.ground_y = self.saved_ground_y  # Repart de la position sauvée
                self.jump_sound.play()
                    
        elif self.jump_state == 'jumping' or self.jump_state == 'descending':
            # Physique de saut avec gravité
            self.jump_velocity += self.jump_gravity * delta_time
            self.ground_y += self.jump_velocity * delta_time
            
            # Bascule en descente quand la vitesse devient négative
            if self.jump_velocity < 0 and self.jump_state == 'jumping':
                self.jump_state = 'descending'
            
            # Atterrissage
            if self.ground_y <= self.saved_ground_y:
                self.ground_y = self.saved_ground_y  # Retourne à la position sauvée
                self.jump_velocity = 0
                self.jump_state = 'idle'
                self.landing_sound.play()
    
    def update_head_bob(self, delta_time, is_moving, is_sprinting):
        """Met à jour l'animation de balancement de tête pendant le sprint"""
        if is_sprinting and is_moving and self.jump_state == 'idle' and not self.crouch_animating:
            # Avance le timer
            self.head_bob_timer += delta_time * self.head_bob_frequency
            # Calcule l'offset sinusoïdal
            import math
            bob_offset = math.sin(self.head_bob_timer * 2 * math.pi) * self.head_bob_amplitude
            return bob_offset
        else:
            # Réinitialise progressivement le timer
            self.head_bob_timer *= 0.9
            return 0.0


class Player:
    """Classe pour gérer le joueur et ses mouvements en 3D"""
    def __init__(self):
        self.x = 0.0  # Position X (gauche/droite)
        self.y = 0.0  # Position Y (haut/bas)
        self.z = 0.0  # Position Z (profondeur)
        self.angle = 0.0  # Angle de rotation de la caméra (en radians)
        
        self.speed_forward = 0.0  # Vitesse avant/arrière
        self.speed_strafe = 0.0  # Vitesse latérale
        
        self.max_speed = 2.0  # Vitesse maximale normale
        self.sprint_speed = 4.0  # Vitesse maximale en sprint
        self.crouch_speed = 1.0  # Vitesse maximale accroupi
        self.acceleration = 0.3  # Accélération
        self.friction = 0.85  # Friction
        
        self.is_sprinting = False  # État du sprint
        
        self.rotation_speed = 0.002  # Vitesse de rotation de la tête
        
        self.moving_forward = False
        self.moving_backward = False
        self.moving_left = False
        self.moving_right = False
        
    def move_forward(self):
        self.moving_forward = True
        
    def move_backward(self):
        self.moving_backward = True
        
    def move_left(self):
        self.moving_left = True
        
    def move_right(self):
        self.moving_right = True
        
    def stop_forward(self):
        self.moving_forward = False
        
    def stop_backward(self):
        self.moving_backward = False
        
    def stop_left(self):
        self.moving_left = False
        
    def stop_right(self):
        self.moving_right = False
    
    def start_sprint(self):
        self.is_sprinting = True
    
    def stop_sprint(self):
        self.is_sprinting = False
        
    def update_head_rotation(self, mouse_x):
        """Met à jour la rotation de la tête selon la position de la souris avec plusieurs paliers"""
        # Système à 4 paliers de rotation
        
        # Bords extrêmes : rotation rapide
        if mouse_x > 850:
            self.angle -= 0.04  # Rotation rapide à droite
        elif mouse_x < 150:
            self.angle += 0.04  # Rotation rapide à gauche
            
        # Zone proche des bords : rotation moyenne
        elif mouse_x > 700:
            self.angle -= 0.02  # Rotation moyenne à droite
        elif mouse_x < 300:
            self.angle += 0.02  # Rotation moyenne à gauche
            
        # Zone intermédiaire : rotation lente
        elif mouse_x > 600:
            self.angle -= 0.008  # Rotation lente à droite
        elif mouse_x < 400:
            self.angle += 0.008  # Rotation lente à gauche
            
        # Centre (400-600) : pas de rotation
        
    def update(self, camera=None):
        """Met à jour la position du joueur en 3D"""
        # Mouvement avant/arrière (W/S)
        if self.moving_forward:
            self.speed_forward += self.acceleration
        elif self.moving_backward:
            self.speed_forward -= self.acceleration
        else:
            self.speed_forward *= self.friction
            if abs(self.speed_forward) < 0.01:
                self.speed_forward = 0
        
        # Mouvement latéral (Q/D)
        if self.moving_left:
            self.speed_strafe -= self.acceleration
        elif self.moving_right:
            self.speed_strafe += self.acceleration
        else:
            self.speed_strafe *= self.friction
            if abs(self.speed_strafe) < 0.01:
                self.speed_strafe = 0
        
        # Limite les vitesses (selon si sprint, accroupi ou normal)
        if camera and camera.is_crouching:
            current_max_speed = self.crouch_speed
        elif self.is_sprinting:
            current_max_speed = self.sprint_speed
        else:
            current_max_speed = self.max_speed
        
        self.speed_forward = max(-current_max_speed, min(self.speed_forward, current_max_speed))
        self.speed_strafe = max(-current_max_speed, min(self.speed_strafe, current_max_speed))
        
        # Calcule le déplacement en fonction de l'angle de vue actuel
        # Important: on utilise self.angle qui doit être mis à jour AVANT cet appel
        
        # Vecteur avant basé sur l'angle
        forward_x = -math.sin(self.angle)
        forward_z = math.cos(self.angle)
        
        # Vecteur latéral (perpendiculaire à l'avant)
        strafe_x = -math.cos(self.angle)
        strafe_z = -math.sin(self.angle)
        
        # Applique les mouvements
        self.x += forward_x * self.speed_forward + strafe_x * self.speed_strafe
        self.z += forward_z * self.speed_forward + strafe_z * self.speed_strafe
