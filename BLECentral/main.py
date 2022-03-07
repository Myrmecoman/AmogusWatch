# Ce script montre comment créer un central UART c'est à dire comment :
# 1 - Détecter un périphérique exécutant le service UART et exposant deux caractéristiques : TX et RX.
# 2 - Se connecter à ce périphérique pour recevoir, sous forme de caractères encodés UTF-8, un message notifié par TX.
# 3 - Répondre au périphérique en écrivant 20 octets max. dans RX.
# Dans cet exemple :
#   - le périphérique envoie une chaîne de caractères contenant la représentation affichable de valeurs
#     de température, pression et humidité qu'il a mesurées.
#   - le central reçoit cette chaîne et l'affiche
#   - le central renvoie au périphérique un simple accusé de réception. On notera que ce message retour ne peut pas être 
#     plus long que 20 caractères du fait d'une limitation de gattc_write dans sa version actuelle (?).

import bluetooth # Classes "primitives du BLE"
from ble_advertising import decode_services, decode_name # Pour décoder les messages reçus

# Constantes requises pour construire le service GATT BLE UART
# Voir : https://docs.micropython.org/en/latest/library/ubluetooth.html
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)

# Objet connectables avec advertising scannable
_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)

# Paramètres pour fixer le rapport cyclique du scan GAP
_SCAN_DURATION_MS = const(2000)
_SCAN_INTERVAL_US = const(30000)
_SCAN_WINDOW_US = const(30000)

# Définition du service UART avec ses deux caractéristiques RX et TX
_UART_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX_CHAR_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_CHAR_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

# Variables globales partagées par les fonctions asynchrones qui répondent aux évènements (callback) 
adresse_MAC = 0 # Adresse matérielle de la radio BLE du central
AR_central_requis = 0 # Est-ce que le central doit envoyer un accusé de réception au périphérique ?


receipt = []


# Classe pour gérer le Central BLE
class BLECentral:

	# Initialisation 
	def __init__(self, ble):
		self._ble = ble
		self._ble.active(True)
		self._ble.irq(self._irq)
		self._reset()
	
	# Réinitialisation (appelée lors des déconnexions)
	def _reset(self):
		# Efface le cache des adresses et des noms des scans
		self._name = None
		self._addr_type = None
		self._addr = None
		
		# Fonctions de réponses (callback) à la complétion de différents évènements
		self._scan_callback = None
		self._conn_callback = None
		self._read_callback = None

		# Fonction de réponse du central aux notifications des périphériques 
		self._notify_callback = None

		# Adresses et caractéristiques du périphérique connecté
		self._conn_handle = None
		self._start_handle = None
		self._end_handle = None
		self._tx_handle = None
		self._rx_handle = None

	# Interruptions de gestion des évènements
	def _irq(self, event, data):
	
		# Evènement "Résultat de scan"
		if event == _IRQ_SCAN_RESULT:
			# Lecture du contenu de la trame d'advertising
			addr_type, addr, adv_type, rssi, adv_data = data
			# Si l'advertising signale un service UART
			if adv_type in (_ADV_IND, _ADV_DIRECT_IND) and _UART_SERVICE_UUID in decode_services(adv_data):
				# Un périphérique potentiel est identifié, référence le et arrète le scan.
				self._addr_type = addr_type
				self._addr = bytes(addr) # Note: le tampon addr a pour propriétaire l'appelant, donc il faut le copier.
				self._name = decode_name(adv_data) or "?"
				self._ble.gap_scan(None)

		# Evènement "Scan terminé"
		elif event == _IRQ_SCAN_DONE:
			if self._scan_callback:
				if self._addr:
					# Un périphérique a été détecté (et le scan a été explicitement interrompu en conséquence)
					self._scan_callback(self._addr_type, self._addr, self._name)
					self._scan_callback = None
				else:
					# Le scan a dépassé son délai de "time-out".
					self._scan_callback(None, None, None)

		# Evènement "Connexion réussie"
		elif event == _IRQ_PERIPHERAL_CONNECT:
			conn_handle, addr_type, addr = data
			if addr_type == self._addr_type and addr == self._addr:
				self._conn_handle = conn_handle
				self._ble.gattc_discover_services(self._conn_handle)

		# Evènement "Déconnexion" (initié par le central ou par le périphérique)
		elif event == _IRQ_PERIPHERAL_DISCONNECT:
			conn_handle, _, _ = data
			if conn_handle == self._conn_handle:
				# Si déconnexion initiée par le central, le reset a déjà été fait
				self._reset()

		# Evènement "Le périphérique connecté a notifié un service au central"
		elif event == _IRQ_GATTC_SERVICE_RESULT:
			conn_handle, start_handle, end_handle, uuid = data
			if conn_handle == self._conn_handle and uuid == _UART_SERVICE_UUID:
				self._start_handle, self._end_handle = start_handle, end_handle

		# Evènement "Recherche de services terminée"
		elif event == _IRQ_GATTC_SERVICE_DONE:
			if self._start_handle and self._end_handle:
				self._ble.gattc_discover_characteristics(
					self._conn_handle, self._start_handle, self._end_handle
				)
			else:
				print("Le service UART est introuvable.")

		# Evènement "Le périphérique connecté a notifié une caractéristique au central"
		elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
			conn_handle, def_handle, value_handle, properties, uuid = data
			if conn_handle == self._conn_handle and uuid == _UART_RX_CHAR_UUID:
				self._rx_handle = value_handle
			if conn_handle == self._conn_handle and uuid == _UART_TX_CHAR_UUID:
				self._tx_handle = value_handle

		# Evènement "Recherche de caractéristiques terminée"
		elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
			if self._tx_handle is not None and self._rx_handle is not None:
				# Nous avons terminé la connexion et la découverte de périphériques, génère le callback de connexion.
				if self._conn_callback:
					self._conn_callback()
			else:
				print("Caractéristique UART RX introuvable.")

		# Evènement "Accusé de réception du périphérique", 
		# qui survient lorsque le central envoie un message, si on a explicitement demandé un AR
		elif event == _IRQ_GATTC_WRITE_DONE:
			conn_handle, value_handle, status = data
			print("Ecriture dans RX réalisée")

		# Evènement "Réponse aux notifications du périphérique" sur la caractéristique TX
		elif event == _IRQ_GATTC_NOTIFY:
			conn_handle, value_handle, notify_data = data
			if conn_handle == self._conn_handle and value_handle == self._tx_handle:
				if self._notify_callback:
					self._notify_callback(notify_data)

	# Revoie True si nous sommes connectés au service UART.
	def is_connected(self):
		return (
			self._conn_handle is not None
			and self._tx_handle is not None
			and self._rx_handle is not None
		)

	# Recherche un périphérique qui propose le service UART
	def scan(self, callback=None):
		self._addr_type = None
		self._addr = None
		self._scan_callback = callback
		# Scanne pendant _SCAN_DURATION_MS, pendant des durées de _SCAN_WINDOWS_US espacées de _SCAN_INTERVAL_US
		self._ble.gap_scan(_SCAN_DURATION_MS, _SCAN_INTERVAL_US, _SCAN_WINDOW_US)

	# Se connecte au périphérique spécifié
	# Si aucun périphérique spécifié, utilise les adresses mises en cache après un scan
	def connect(self, addr_type=None, addr=None, callback=None):
		self._addr_type = addr_type or self._addr_type
		self._addr = addr or self._addr
		self._conn_callback = callback
		if self._addr_type is None or self._addr is None:
			return False
		self._ble.gap_connect(self._addr_type, self._addr)
		return True

	# Se déconnecte du périphérique
	def disconnect(self):
		if not self._conn_handle:
			return
		self._ble.gap_disconnect(self._conn_handle)
		self._reset()

	# Envoie des données sur l'UART (écriture dans la caractéristique RX)
	# Cette méthode permet au central d'envoyer un message au périphérique connecté.

	def write(self, v, response = False):
		
		if not self.is_connected():
			return
		self._ble.gattc_write(self._conn_handle, self._rx_handle, v, 1 if response else 0)
		
		# Confirme que l'accusé de réception a bien été envoyé
		global AR_central_requis
		AR_central_requis = 0

	# Active le gestionnaire des évènements de réception sur l'UART
	def on_notify(self, callback):
		self._notify_callback = callback

# Gestionnaire de l'évènement de réception qui répond à une notification lorsque la caractéristique TX
# est modifiée.
def on_receipt(v):
	
	# Conversion en octets de la charge utile de TX
	b = bytes(v)

	# On convertit les octets reçus en caractères codés au format UTF-8
	payload = b.decode('utf-8')
	print("Message recu de " + str(adresse_MAC) + " : ", payload)
	liste = float(payload)
	# Le central a bien reçu un message du périphérique, donc il doit lui envoyer un accusé de réception
	global AR_central_requis
	AR_central_requis = 1
	global receipt
	receipt = liste

# Création d'une instance de la classe central
ble = bluetooth.BLE()
central = BLECentral(ble)

aucun_peripherique = 0 # Vaudra 1 si un périphérique est détecté

# Gestionnaire des évènements de scan
def on_scan(addr_type, addr, name):

	import ubinascii # Pour convertir des informations binaires en texte
	from ubinascii import hexlify # Pour convertir un nombre hexadécimal en sa représentation binaire affichable

	if addr_type is not None:
		global adresse_MAC
		b = bytes(addr)
		print("Périphérique trouvé : ", name)
		adresse_MAC = hexlify(b).decode("ascii")
		central.connect()
	else:
		global aucun_peripherique
		aucun_peripherique = 1
		print("Aucun périphérique trouvé.")

# Programme principal
def demo():

	print("Central BLE")

	import time # Pour gérér le temps et les temporisations

	aucun_peripherique = 0

	#Capture les évènements de scan
	central.scan(callback=on_scan)

	# Attente de connexion...
	while not central.is_connected():
		time.sleep_ms(100)
		if aucun_peripherique == 1:
			return
	print("Connecté")
 
	# Capture les évènements de réception. La notification provient de la caractéristique TX.
	central.on_notify(on_receipt)

	# Envoi d'un message d'accusé de réception du central au périphérique
	while central.is_connected():
		if AR_central_requis == 1:
			try: # Essaie d'envoyer un message
				print(receipt)
				v = str(int(receipt)**2)
				central.write(v)
			except: # En cas d'échec...
				print("Echec d'émission de la réponse du central")

	# Pour le cas où le central se retrouverait déconnecté
	print("Déconnecté")

# Si le nom du script est "main", exécute la fonction "demo()"
if __name__ == "__main__":
	demo()