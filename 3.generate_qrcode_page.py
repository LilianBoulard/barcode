# coding: utf-8

"""

Ce script place les QRcodes sur une page afin de pouvoir les imprimer.
Le papier requis est une page blanche sans pré-découpage (le script va placer les QR codes en fonction des paramètres indiqués ci-dessous).

"""



# DPI du scan, fait par le convertisseur PDF > Image.
# Cette variable doit coïncider avec celle du script en question (2.convert_pdf_to_png.py).
DPI_SCAN = 1000
# DPI de l'imprimante.
DPI_IMP = 224

# Dossier source, là où le script ira chercher les QR codes à imprimer.
SRC = "C:/dossier/images_a_imprimer/"
# Extension des fichiers qu'il faut placer sur la feuille, se tranvant dans le dossier ci-dessus. Il faut que l'extension soit celle d'une image (png, jpg, etc).
EXT_DST = ".png"
# Nom du fichier de sortie - la page à imprimer. Ne pas inclure l'extension.
FL_NAME = "output"

# Nombre de QR codes à faire apparaître sur la page.
# En date de Février 2020, on imprime 3 QR codes : un pour l'ordinateur, un pour le chargeur et un pour l'étiquette de la sacoche.
NB_QR = 3
# Adapter les valeurs suivantes pour que le QR code soit lisible (ni trop grand ni trop petit).
# Hauteur minimale de chaque QR, en centimètres.
MIN_HEI_QR = 3.2
# Hauteur maximale de chaque QR, en centimètres.
MAX_HEI_QR = 4.5
# Longueur et hauteur de la page, en centimètres.
PAGE_SIZE_CM = (21.0, 29.7)
# Espacement entre chaque QR code, en centimètres.
ESP_CM = 0.1



# NE PAS MODIFIER CI-DESSOUS (sauf si vous êtes compétent en Python)



def install_module(package):
    """
    Utilise pip pour installer un nouveau module Python.
    Retourne un booléen "Vrai" lorsque ça fonctionne, "Faux" autrement.
    """
    import subprocess, sys
    try:
        # Lance la commande pip pour installer le module
        if subprocess.check_call([sys.executable, "-m", "pip", "install", package]) == 0:
            return True
    except subprocess.CalledProcessError as e:
        input("Erreur rencontrée lors de l'installation du module \"{}\" : {}\nMerci de l'installer manuellement en utilisant pip.".format(package, e))
        return False

# Importe les modules requis
import os
try:
    from PIL import Image
except ImportError:
    if install_module("Image"):
        from PIL import Image
    else:
        exit()

"""
Note :
DPI est l'indication du nombre de pixels par pouces.
96 DPI signifie qu'il y a 96 pixels par pouces.
1 pouce est égal à 2.54 centimètres.
La formule est :
Pixel = (cm x DPI) / 2.54
= (18 x 120) / 2.54
= 850.394 px
"""

def px_to_cm(px, dpi):
    """
    Convertit un nombre de pixels en une mesure en centimètres, en fonction d'un DPI.
    """
    return (px / dpi) * 2.54

def cm_to_px(cm, dpi):
    """
    Convertit une mesure en centimètres en un nombre de pixels, en fonction d'un DPI.
    """
    # Retourne un arrondi (on ne veut pas de portion de pixels)
    return int((cm * dpi) / 2.54)

def get_image_size(fl):
    """
    Retourne la taille de l'image passée.
    """
    with Image.open(fl) as img:
        return img.size

def construct_new_page(PAGE_SIZE_PX, ESP_PX, qr_index = 0, l_index = 0, g_index = 1):
    """
    Construit une page, en format image, où seront incrustés les QR codes.
    l_index est un index "local" : si par exemple il faut imprimer 2 codes par QR codes, mais que le deuxième QR
    """
    # Cette variable va permettre de vérifier si les autres fichiers image ont la même taille. On l'initialise vide.
    source_qr = ()
    # On initialise la variable coords, qui corresponds au pixel coordonnées x, y où se trouve le pointeur.
    coords = [ESP_PX, ESP_PX]
    # Crééer une nouvelle page
    with Image.new("RGB", PAGE_SIZE_PX, (255, 255, 255)) as img:
        for fl in os.listdir(SRC)[l_index:]:
            # Construit le nom du fichier
            a_fl = SRC + fl
            # Et l'ouvre
            with Image.open(a_fl) as qr:
                # Si la variable "source_qr" est vide.
                if source_qr == ():
                    # On y sauvegarde le nom du fichier et ses dimensions
                    source_qr = (fl, qr.size)
                # Si l'image en cours de traitement a les même dimensions que l'image source
                if qr.size == source_qr[1]:
                    # Pour autant de fois que la variable NB_QR (le nombre de codes que l'on veut par QR)
                    for i, x in enumerate(range(NB_QR)[qr_index:]):
                        # On colle le QR code aux coordonnées.
                        img.paste(qr, tuple(coords))
                        # Si la coordonnée x (horizontale) du pointeur + 2x la longueur du QR code est plus grande que la taille horizontale de la page, cela signifie que nous sommes à la fin d'une ligne, et qu'il faut donc passer à la suivante.
                        if coords[0] + (qr.size[0] * 2) > PAGE_SIZE_PX[0]:
                            # On réinitialise la coordonnée x
                            coords[0] = ESP_PX
                            # Et si la coordonnée y (verticale) + 2x la hauteur du QR code est plus grande que la taille verticale de la page, cela signifie que nous sommes au bout de la page, et qu'il faut donc en créer une nouvelle.
                            if coords[1] + (qr.size[1] * 2) > PAGE_SIZE_PX[1]:
                                # On appelle récursivement la fonction, en incrémentant l'index global
                                construct_new_page(PAGE_SIZE_PX, ESP_PX, i, l_index, g_index + 1)
                                # L'index global permet d'adapter le nom du fichier de sortie.
                                img.save("{}{}{}".format(FL_NAME, g_index, EXT_DST))
                                return
                            else: # Si les coordonnées restent dans la page
                                # On incrémente les coordonnées de la hauteur du QR code + la marge
                                coords[1] += qr.size[1] + ESP_PX
                        else:
                            # On incrémente les coordonnées de la longueur du QR code + la marge
                            coords[0] += qr.size[0] + ESP_PX
                else:
                    input("Deux fichiers ont des tailles différentes !\n{} - {} | {} - {}\nTous les QR codes doivent avoir la même taille ; merci de corriger.".format(*source_qr, fl, img.size))
                    exit()
            # On incrémente l'index du fichier en cours de traitement
            l_index += 1
        img.save("{}{}{}".format(FL_NAME, g_index, EXT_DST))
        return

if __name__ == "__main__":
    # Défini une nouvelle constante, qui équivaut à la taille de la page, en pixels.
    PAGE_SIZE_PX = (cm_to_px(PAGE_SIZE_CM[0], DPI_SCAN), cm_to_px(PAGE_SIZE_CM[1], DPI_SCAN))
    ESP_PX = cm_to_px(ESP_CM, DPI_SCAN)
    construct_new_page(PAGE_SIZE_PX, ESP_PX)
    input("Terminé. Appuyez sur entrée pour quitter...")
