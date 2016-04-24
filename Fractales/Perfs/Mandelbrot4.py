#!/usr/bin/python2
import pygame, numpy
pygame.init()

##############
# Constantes #
##############
resolution = largeur, hauteur = 200, 200

noir = 0, 0, 0
rouge = 255, 0, 0
blanc = 255, 255, 255

#############
# Variables #
#############
police = pygame.font.SysFont("arial", 15);
minX = -5.0/2
maxX = 3.0/4
minY = -3.0/2
maxY = 3.0/2
maxIterations = 256
zoom = 1.0
zoomFactor = 2.0

img = None
x = None
y = None
cx = None
cy = None
ix = None
iy = None

def init():
    global img, cx, cy, x, y, ix, iy
    ix, iy = numpy.mgrid[0:largeur, 0:hauteur]
    cx = numpy.linspace(minX, maxX, largeur)[ix]
    cy = numpy.linspace(maxY, minY, hauteur)[iy]
    x = numpy.zeros(cx.shape)
    y = numpy.zeros(cx.shape)
    img = numpy.zeros(cx.shape, dtype=int)
    # On passe nos tableaux 2D a 1D pour pouvoir enlever les valeurs qui divergent au fur et a mesure
    ix.shape = largeur*hauteur
    iy.shape = largeur*hauteur
    cx.shape = largeur*hauteur
    cy.shape = largeur*hauteur
    x.shape = largeur*hauteur
    y.shape = largeur*hauteur

def trf():
    global img, x, y, cx, cy, ix, iy
    if not len(x): return img
    tmp = x*x - y*y + cx
    y = 2.0*x*y + cy
    x = tmp
    # Les points qui divergent a cette iteration:
    rem = x*x+y*y>4.0
    img[ix[rem], iy[rem]] = 255
    # Les points qui ne divergent pas (encore ?):
    rem = -rem
    x,y = x[rem], y[rem]
    ix, iy = ix[rem], iy[rem]
    cx,cy = cx[rem], cy[rem]
    return img

##################
# Initialisation #
##################
ecran = pygame.display.set_mode(resolution)
pygame.display.set_caption("Ensemble de Mandelbrot")
init()

quitter = False
i = 0
# Profiling
import cProfile, pstats, StringIO
pr = cProfile.Profile()
pr.enable()
#####################
# Boucle principale #
#####################
while quitter != True:
    # Boucle d'evenements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitter = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quitter = True
            if event.key == pygame.K_r:
                i = 0
            if event.key == pygame.K_p:
                maxIterations *= 2
            if event.key == pygame.K_m:
                maxIterations /= 2
        if event.type == pygame.MOUSEBUTTONDOWN:
            centerX = minX + 1.0*event.pos[0]/largeur*(maxX-minX)
            centerY = minY + 1.0*(maxY-minY)*(hauteur-event.pos[1])/hauteur
            if pygame.mouse.get_pressed()[0]:
                print("Clic en (%s, %s) dans (%s, %s) -> (%s, %s)" % (event.pos[0], event.pos[1], minX, minY, maxX, maxY))
                newLargeur = (maxX - minX) / zoomFactor
                newHauteur = (maxY - minY) / zoomFactor
                zoom *= zoomFactor
                print("Zoom (%s, %s) => (%s, %s) (%s, %s)" % (centerX, centerY, minX, minY, maxX, maxY))
            elif pygame.mouse.get_pressed()[2]:
                newLargeur = (maxX - minX) * zoomFactor
                newHauteur = (maxY - minY) * zoomFactor
                zoom /= zoomFactor
                print("Dezoom (%s, %s) => (%s, %s) (%s, %s)" % (centerX, centerY, minX, minY, maxX, maxY))
            else:
                continue
            i = 0
            minX = centerX - newLargeur/2.0
            maxX = centerX + newLargeur/2.0
            minY = centerY - newHauteur/2.0
            maxY = centerY + newHauteur/2.0
            init()

    dessine = False

    if i < maxIterations:
        i += 1
        ecran.fill(noir)
        pygame.surfarray.blit_array(ecran, trf())
        infos = police.render("Iter=%s/%s - Zoom=%s" % (i, maxIterations, zoom), True, rouge)
        ecran.blit(infos, (0, 0))
        pygame.display.flip()
    # Activer (en mettant 'and True') pour le profiling
    if i == maxIterations and False:
        quitter = True

###############
# Terminaison #
###############
pygame.quit()

# Profiling
pr.disable()
s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print s.getvalue()
