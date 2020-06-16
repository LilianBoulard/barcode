# coding: utf-8

"""

Ce script récupère des fichiers sur un serveur distant (Linux !), en utilisant SSH.

"""



# Adresse du serveur. Peut être une adresse IP (v4 ou v6) ou un nom DNS FQDN.
server = "serveur.domaine.local"
# Port SSH du serveur ci-dessus
port = 22
# Compute local du serveur ci-dessus
user = "glpi"

# Emplacement des fichiers QRcode sur le serveur
remoteQRcodesLocation = "/var/www/glpi/files/_plugins/barcode/"
# Une expression contenant un ou plusieurs caractère(s) générique(s) (sous Linux, c'est le caractère "*"), qui sert à copier tous les fichiers PDF qui nous intéressent.
# Voir "https://en.wikipedia.org/wiki/Wildcard_character" pour plus d'informations sur les caractères génériques.
qrCodeWildcard = "*_QRcode.pdf"
# Destination, là où seront copiés les fichiers
copyDestination = "C:/dossier/pdf/"



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
        input(f"Erreur rencontrée lors de l'installation du module \"{package}\" : {e}\nMerci de l'installer manuellement en utilisant pip.")
        return False


# Importe les modules requis
from getpass import getpass

try:
    from scp import SCPClient
except ImportError:
    if install_module("scp") == True:
        from scp import SCPClient
    else:
        print("Le module \"scp\" n'a pas pu être installé. Merci de le faire manuellement en utilisant votre système de gestion de module (habituellement pip).")
        exit()

try:
    import paramiko
except ImportError:
    if install_module("paramiko") == True:
        import paramiko
    else:
        exit()


def createSSHClient(server, port, user, password):
    """
    Créer un client SSH et le retourne.
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # On utilise une boucle True pour réessayer lorsque le mot de passe entré est erroné
    while True:
        try:
            client.connect(server, port, user, password)
            break
        except paramiko.ssh_exception.AuthenticationException:
            password = getpass(f"Le mot de passe entré est incorrect.\nVeuillez entrer le mot de passe du compte \"{user}\"\n>")
    return client


# Demande de confirmation.
print(f"Le script va copier à l'emplacement \"{copyDestination}\" les fichiers nommés de la sorte : \"{qrCodeWildcard}\", se trouvant sur le serveur \"{server}\" à l'emplacement \"{remoteQRcodesLocation}\",  en utilisant l'utilisateur distant \"{user}\".\n")
input("Appuyez sur entrée pour continuer. Pour annuler l'opération, fermez cette fenêtre ou faites Ctrl + C.")

# Demande le mot de passe du compte distant
password = getpass(f"Veuillez entrer le mot de passe du compte \"{user}\"\n>")

ssh = createSSHClient(server, port, user, password)
with SCPClient(ssh.get_transport(), sanitize = lambda x: x) as scp:
    # On lance la commande en local
    scp.get(r"{remoteQRcodesLocation}{qrCodeWildcard}".format(remoteQRcodesLocation=remoteQRcodesLocation, qrCodeWildcard=qrCodeWildcard), r"{copyDestination}".format(copyDestination=copyDestination))

ssh.exec_command(f"sudo mv {remoteQRcodesLocation}*.pdf {remoteQRcodesLocation}old/")


input("Terminé. Appuyez sur entrée pour quitter...")
