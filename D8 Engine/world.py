"""Module contenant les fonctions 3D et la classe GameObject pour le monde"""
import pygame
import math


def rotate_point_y(x, z, angle):
    """Rotation d'un point autour de l'axe Y (rotation horizontale)"""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    new_x = x * cos_a - z * sin_a
    new_z = x * sin_a + z * cos_a
    return new_x, new_z


def project_3d_to_2d(x, y, z, camera_x, camera_y, camera_z, camera_angle):
    """Projette un point 3D vers l'écran 2D avec la caméra"""
    # Distance focale pour la projection
    focal_length = 500
    
    # Position relative à la caméra
    rel_x = x - camera_x
    rel_y = y - camera_y
    rel_z = z - camera_z
    
    # Rotation selon l'angle de la caméra
    rotated_x, rotated_z = rotate_point_y(rel_x, rel_z, -camera_angle)
    
    # Évite la division par zéro
    if rotated_z <= 0.1:
        return None, None, 0
    
    # Projection perspective
    scale = focal_length / rotated_z
    screen_x = 500 + (rotated_x * scale)
    screen_y = 300 - (rel_y * scale)
    
    return screen_x, screen_y, scale


class GameObject:
    """Classe de base pour les objets du décor avec coordonnées 3D"""
    # Cache partagé entre toutes les instances pour les images
    _image_cache = {}
    
    def __init__(self, image_path, x, y, z, destroyable=False):
        # Utilise le cache d'images pour éviter de recharger plusieurs fois la même image
        if image_path not in GameObject._image_cache:
            GameObject._image_cache[image_path] = pygame.image.load(image_path).convert_alpha()
        self.original_image = GameObject._image_cache[image_path]
        self.image = self.original_image
        self.x = x  # Position X (gauche/droite)
        self.y = y  # Position Y (haut/bas)
        self.z = z  # Position Z (profondeur)
        self.destroyable = destroyable  # Peut être détruit
        self.original_height = self.original_image.get_height()  # Hauteur pour calcul d'ancrage
        self.original_width = self.original_image.get_width()
        self.screen_x = 0
        self.screen_y = 0
        self.scale = 1.0
        self.visible = False
        # Cache pour l'image redimensionnée
        self.cached_size = (0, 0)
        self.cached_image = None
        
    def update_projection(self, camera_x, camera_y, camera_z, camera_angle):
        """Met à jour la projection 3D vers 2D"""
        screen_x, screen_y, scale = project_3d_to_2d(
            self.x, self.y, self.z,
            camera_x, camera_y, camera_z, camera_angle
        )
        
        if screen_x is None or scale <= 0:
            self.visible = False
            return
        
        # Culling frustum étendu - ne calcule que si potentiellement visible
        if screen_x < -1000 or screen_x > 2000:
            self.visible = False
            return
        
        self.visible = True
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.scale = scale
        
        # Redimensionne l'image selon la distance SEULEMENT si la taille change
        scale_clamped = max(0.1, min(scale, 5.0))
        new_width = int(self.original_width * scale_clamped)
        new_height = int(self.original_height * scale_clamped)
        
        # Utilise le cache pour éviter les redimensionnements inutiles
        if new_width > 0 and new_height > 0:
            new_size = (new_width, new_height)
            if self.cached_size != new_size:
                self.cached_size = new_size
                self.cached_image = pygame.transform.smoothscale(self.original_image, new_size)
            self.image = self.cached_image
    
    def get_distance_squared(self, camera_x, camera_y, camera_z):
        """Calcule la distance au carré (plus rapide, suffisant pour le tri)"""
        dx = self.x - camera_x
        dy = self.y - camera_y
        dz = self.z - camera_z
        return dx*dx + dy*dy + dz*dz
    
    def is_in_crosshair(self, screen_center_x=500, screen_center_y=300, max_distance=800):
        """Vérifie si l'objet est dans la zone de visée (palier basé sur la distance)"""
        if not self.visible:
            return False
        
        # Vérification de la distance Z (profondeur) - ne peut pas tirer trop loin
        # Position relative à la caméra déjà calculée dans update_projection via scale
        # Scale diminue avec la distance, donc on vérifie si scale est suffisant
        # Scale ~1.0 = proche, scale ~0.1 = très loin
        # On refuse si l'échelle est trop petite (objet trop loin)
        if self.scale < 0.25:  # Correspond à environ 2000 unités de distance
            return False
        
        # Calcul du palier de tolérance : plus l'objet est loin (scale petit), plus le palier est petit
        # Scale proche (1.0) = palier large (125px), scale loin (0.1) = palier étroit (35px)
        tolerance = 35 + (90 * self.scale)
        
        # Calcul des centres de l'objet
        obj_center_x = self.screen_x
        obj_center_y = self.screen_y - (self.image.get_height() // 2)
        
        # Vérification si dans le palier
        dx = abs(obj_center_x - screen_center_x)
        dy = abs(obj_center_y - screen_center_y)
        
        return dx < tolerance and dy < tolerance
            
    def draw(self, screen, ground_offset=0):
        """Dessine l'objet si visible"""
        if not self.visible or self.screen_x < -500 or self.screen_x > 1500:
            return
        
        # Pré-calcul des dimensions (appel unique)
        img_width = self.image.get_width()
        img_height = self.image.get_height()
        
        # Centre l'image sur la position
        draw_x = int(self.screen_x - (img_width >> 1))  # Division par 2 optimisée
        
        # Abaisse l'objet pour qu'il soit posé sur le sol
        # Facteur pré-calculé selon la taille originale
        factor = 0.4 if self.original_height > 400 else 0.25
        ground_anchor_offset = 40 + (img_height * factor)
        
        draw_y = int(self.screen_y - img_height + ground_anchor_offset + ground_offset)
        
        screen.blit(self.image, (draw_x, draw_y))
