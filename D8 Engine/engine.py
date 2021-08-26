import pygame
from random import randrange
from time import sleep
from audioplayer import AudioPlayer
pygame.init()



pygame.display.set_caption("D8 Engine")
screen = pygame.display.set_mode((1000, 600))

print("MOTEUR DE JEU LANCÉ")

# CHARGEMENT DES IMAGES

matin = pygame.image.load("assets/jour.png").convert_alpha()
gun = pygame.image.load("assets/gun.png").convert_alpha()
gunfire = pygame.image.load("assets/gunfire.png").convert_alpha()
arc = pygame.image.load("assets/arc.png").convert_alpha()
sol = pygame.image.load("assets/sol.png").convert_alpha()
gunfiresound = AudioPlayer("assets/fire.mp3")
viseur = pygame.image.load("assets/viseur.png").convert_alpha()
tree = pygame.image.load("assets/tree.png").convert_alpha()
stree = pygame.image.load("assets/tree.png").convert_alpha()
statue1 = pygame.image.load("assets/statue.png").convert_alpha()
statue2 = pygame.image.load("assets/statue.png").convert_alpha()
running = True



# Initialisation des variables de l'engine

fire = 0
chrono = 0
munition = 10
weapon = 2
animationarc = 0
animationtime = 0
animationgun = 0
animationtimegun = 0

animationarchaut = 0
animationtimehaut = 0
animationgunhaut = 0
animationtimegunhaut = 0

# OBJECTS

soly = 0
treey = 500
streey = 350
ttreey = 220
ftreey = 50
statue1y = 1600
statue2y = 250
scaletree = 15


arcy = 35
guny = 305
weaponx = 350

# PERSONNAGE

mouvement = 0

while running:	



# Background
	screen.blit(matin, (0, 0))


# Le sol

	screen.blit(sol, (0, soly))
	x, y = pygame.mouse.get_pos()
	if y < 210 and y > 0:
		if soly < 80:
			soly += 0.5
	elif y > 400 and y < 600:
		if soly > 0:
			soly -= 0.5


# MOUVEMENT EQUIPEMENT

	if y < 250 and y > 0:
		if arcy > -80:
			arcy -= 1

	if y > 360 and y < 600:
		if arcy < 50:
			arcy += 1

	if y < 250 and y > 0:
		if guny > 250:
			guny -= 1

	if y > 360 and y < 600:
		if guny < 320:
			guny += 1


	if x >= 600:
		if weaponx < 430:
			weaponx+=1
	elif x <= 365:
		if weaponx > 320:
			weaponx-=1



# La souris
	if treey >= -30 and treey <= 1000:
		screen.blit(tree, (treey, soly))
	if streey >= -30 and streey <= 1000:
		screen.blit(tree, (streey, soly))
	if ttreey >= -30 and ttreey <= 1000:
		screen.blit(tree, (ttreey, soly))
	if ftreey >= -30 and ftreey <= 1000:
		screen.blit(tree, (ftreey, soly))
	if statue1y >= -100 and statue1y <= 1000:
		screen.blit(statue1, (statue1y, soly))
	if statue2y >= -100 and statue2y <= 1000:
		screen.blit(statue2, (statue2y, soly))
	if x > 700:
		treey -= 2
		streey -= 2
		ttreey -= 2
		ftreey -= 2
		statue1y -= 2
		statue2y -= 2
	elif x < 300:
		treey+= 2
		streey += 2
		ttreey += 2
		ftreey += 2
		statue1y += 2
		statue2y += 2
	if treey > 2000:
		treey = 1
	elif treey < -1000:
		treey = 999
	elif streey > 2000:
		streey = 1
	elif streey < -1000:
		streey = 999
	elif ttreey > 2000:
		ttreey = 1
	elif ttreey < -1000:
		ttreey = 999
	elif ftreey > 2000:
		ftreey = 1
	elif ftreey < -1000:
		ftreey = 999
	elif statue1y > 2000:
		statue1y = 1
	elif statue1y < -1000:
		statue1y = 999
	elif statue2y > 2000:
		statue2y = 1
	elif statue2y < -1000:
		statue2y = 999
	



# Joueur

	if weapon == 1: # PISTOLET
		if fire == 0:
			screen.blit(gun, (weaponx, guny))   # Pistolet 
		elif fire == 1:
			screen.blit(gunfire, (weaponx, guny))
	elif weapon == 2: # ARC
		screen.blit(arc, (weaponx, arcy)) 

# CHANGEMENT D'ÉQUIPEMENT ANIMATION

# Quittez le moteur

	pygame.display.flip()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			pygame.quit()

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if weapon == 1:
				if munition > 0:
					fire = 1
					chrono = 0
					gunfiresound.play()
					munition -= 1

		# CHANGEMENT D'EQUIPEMENT
					
		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_UP:
				if weapon == 1:
					animationgun = 1
			mouvement = 0

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_DOWN:
				if weapon == 2:
					animationarc = 1

		# MOUVEMENTS PERSO
			elif event.key == pygame.K_w:
				print("AVANCER")
				mouvement = 1

	
		

	chrono += 1
	if chrono > 20 and chrono < 40:
		fire = 0
	elif chrono >= 1000:
		chrono = 0

	if animationarc == 1:
		animationtime+=1
		if animationtime == 1:
			arcy+=9
			animationtime = 0
			if arcy >= 600:
				weapon = 1
				arcy = 35
				guny = 600
				animationarc = 0
				animationgunhaut = 1

	if animationgun == 1:
		animationtimegun+=1
		if animationtimegun == 1:
			guny+=3
			animationtimegun = 0
			if guny >= 600:
				guny = 305
				arcy = 600
				weapon = 2
				animationgun = 0
				animationarchaut = 1

	if animationarchaut == 1:
		animationtimehaut+=1
		if animationtimehaut == 1:
			arcy = arcy-9
			animationtimehaut = 0
			if arcy >= 35 and arcy <= 45:
				arcy = 35
				animationarchaut = 0

	if animationgunhaut == 1:
		animationtimegunhaut+=1
		if animationtimegunhaut == 1:
			guny-=3
			animationtimegunhaut = 0
			if guny >= 305 and guny <= 315:
				guny = 305
				animationgunhaut = 0

		
