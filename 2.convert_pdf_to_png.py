# coding: utf-8

"""

Ce script convertis les fichiers PDF trouvés dans le dossier source (variable SRC) en images, qu'il enregistre dans le dossier destination (variable DST).
Le script s'occupe aussi de rogner ces images afin de garder uniquement le QRcode.

TODO :
Masque sur le QRcode afin de filtrer le bruit du scan.

"""



# Dossier dans lequel se trouvent les fichiers PDF
SRC = "C:/dossier/pdf/"
# Dossier de destination pour les fichiers image.
DST = "C:/dossier/image/"
# DPI (résolution) utilisée par le convertisseur PDF > PNG.
# Plus la valeur est grande, plus la résolution du scan sera importante mais les fichiers seront plus lourds et le traitement sera plus long. Conseillé entre 500 et 1000. Pas besoin d'utiliser le même DPI que l'imprimante.
# Cette variable doit coïncider avec celle du script qui place les QR codes sur la page (3.generate_qrcode_page.py).
DPI_SCAN = 1000
# Extension des fichiers à convertir
EXT_SRC = ".pdf"
# Extension / type d'image à convertir
EXT_DST = [".png", "PNG"]



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
from time import time
from shutil import copy2
# On utilise le multithreading pour améliorer les performances
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
try:
    import pdf2image
except ImportError:
    if install_module("pdf2image"):
        import pdf2image
    else:
        exit()
try:
    from PIL import Image
except ImportError:
    if install_module("Image"):
        from PIL import Image
    else:
        exit()

#input("Merci d'installer poppler manuellement en suivant les étapes suivantes : \
#\n> Téléchargez le dernier package en date depuis le site \"http://blog.alivate.com.au/poppler-windows/\". \
#\n> Une fois téléchargé, extraire l'archive sous le C: (dans Temp par exemple) et ajouter le dossier \"bin\" à la variable d'environnement (Path). \
#\nAppuyez sur entrée pour fermer le programme...")

def parse_pixels(qrcode, pixels, color, reverse = False):
    """
    Fonction utilisée pour analyser les pixels.
    Elle analyse tous les pixels de chaque ligne de gauche à droite en partant d'en haut à gauche si "reverse" est sur "False", de droite à gauche en partant d'en bas à droite lorsque "reverse" est sur "True"
    Retourne le couple de coordonnées quand la couleur du pixel est égal au tuple Rouge-Vert-Bleu "color".
    """
    argsRow = [qrcode.size[1] - 1, -1, -1] if reverse else [qrcode.size[1]]
    argsCol = [qrcode.size[0] - 1, -1, -1] if reverse else [qrcode.size[0]]
    for row in range(*argsRow): # Pour chaque ligne
        for col in range(*argsCol): # Pour chaque colonne
            if pixels[col, row] == color:
                return (col, row)

def get_qrcode_dimensions(qrcode, color = (0, 0, 0)):
    """
    Analyse l'image qrcode, la convertit en une matrice de pixels.
    Retourne une tuple de 4 items : les deux premiers sont les coordonnées du premier pixel (celui en haut à gauche du QR code) et les deux derniers sont les coordonnées du dernier pixel (celui en bas à droite du QR code)
    Note : RVB(0, 0, 0) = noir ; RVB(255, 255, 255) = blanc
    """
    # Convertir l'image en matrice de pixels.
    pixels = qrcode.load()
    # Retourne un tuple de 4 objets, les coordonnées de l'origine et les coordonnées du dernier pixel.
    return parse_pixels(qrcode, pixels, color, False) + parse_pixels(qrcode, pixels, color, True)

def convertPdf(fl):
    """
    Convertit les PDFs en fichiers image.
    """
    # Si l'extension correspond à celle recherchée
    if os.path.splitext(fl)[1] == EXT_SRC:
        try:
            # Récupère la première page du PDF et la convertit en image
            pages = pdf2image.convert_from_path(SRC + fl, dpi = DPI_SCAN, last_page = 1)
            for page in pages:
                # Sauvegarde temporairement l'image en là d'où est lancé le script. Elle sera enregistrée au bon endroit (DST) lors du traitement.
                page.save("{}{}".format(os.path.splitext(os.path.basename(fl))[0], EXT_DST[0]), EXT_DST[1])
            print("Fichier {} converti et sauvegardé.".format(fl))
        except Exception as e:
            print("Erreur avec {} : {}".format(fl, e))

def cropImage(fl):
    """
    Coupe l'image pour qu'il n'y ai plus que le QR code.
    """
    # Si l'extension correspond à celle recherchée
    if os.path.splitext(fl)[1] == EXT_DST[0]:
        try:
            # Essaye de l'ouvrir en tant qu'image
            im = Image.open(fl)
            # Récupère les coordonnée du début et de la fin du fichier
            size = list(im.getbbox())
            # Coupe la partie basse de l'image (sur l'axe vertical), afin de se débarrasser du numéro de page.
            size[3] = int(size[3] - (DPI_SCAN / 4)) # DPI_SCAN / 4 correspond au nombre de pixels entre le haut du marquage de page (1/1) et le bas de la page. Cette ligne permet de retirer une bande de 250 pixels en partant du bas.
            im2 = im.crop(tuple(size))
            # Puis recoupe l'image pour juste avoir le rectangle du QRcode
            im2 = im.crop(get_qrcode_dimensions(im2))
            # Sauvegarde le fichier
            im2.save(DST + fl)
            # Et supprime le fichier temporaire
            os.remove(fl)
            print("Fichier {} traité.".format(fl))
        except Exception as e:
            print("Erreur avec {} : {}".format(fl, e))

if __name__ == "__main__":
    tic = time()
    pool = ThreadPool(cpu_count())
    # Pour chaque fichier PDF trouvé dans le dossier SRC, on le converti en image en appelant la fonction convertPdf
    pool.map(convertPdf, os.listdir(SRC))
    # Pour chaque fichier trouvé dans le dossier courant, on appelle la fonction cropImage
    pool.map(cropImage, os.listdir(os.path.dirname(os.path.realpath(__file__)) + "\\"))
    # On supprime tous les fichiers PDF du dossier source
    for fl in os.listdir(SRC):
        os.remove(SRC + fl)
    tac = time()
    input("Terminé en {} minutes, {} secondes. Appuyez sur entrée pour quitter...".format(int((tac-tic) / 60), round((tac - tic) % 60, 3)))
