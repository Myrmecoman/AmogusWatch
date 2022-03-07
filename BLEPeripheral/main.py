# Ce script montre comment créer un periphérique UART  avec le Nordic Uart Service.
# Il va :
# 1 - Exposer deux caractéristiques TX et RX pour échanger des données.
# 2 - Se connecter à un central et lui notifier des messages dans TX.
# 3 - Lire les données écrites en retour par le central dans RX. 
# Le périphérique envoie au central une chaîne de caractères contenant la température, l'humidité et la pression.

import bluetooth # Classes "primitives du BLE"
import ble_advertising
import random
from binascii import hexlify # Convertit une donnée binaire en sa représentation hexadécimale

# Constantes requises pour construire le service BLE UART
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# Définition du service UART avec ses deux caractéristiques RX et TX
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
	bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
	_FLAG_NOTIFY, # Cette caractéristique notifiera le central des modifications que lui apportera le périphérique
)
_UART_RX = (
	bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
	_FLAG_WRITE, # Le central pourra écrire dans cette caractéristique
)
_UART_SERVICE = (
	_UART_UUID,
	(_UART_TX, _UART_RX),
)

# Nombre maximum d'octets qui peuvent être échangés par la caractéristique RX
_MAX_NB_BYTES = const(100)

class BLEUART:

	# Initialisations
	def __init__(self, ble, name="STM32BLE", rxbuf=_MAX_NB_BYTES):
		self._ble = ble
		self._ble.active(True)
		self._ble.irq(self._irq)
		# Enregistrement du service
		((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
		# Augmente la taille du tampon rx et active le mode "append"
		self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
		self._connections = set()
		self._rx_buffer = bytearray()
		self._handler = None
		# Advertising du service (services=[_UART_UUID] est indispensable pour que le central identifie le service)
		self._payload = ble_advertising.advertising_payload(name=name, services=[_UART_UUID])
		self._advertise()
		
		# Affiche l'adresse MAC de l'objet
		dummy, byte_mac = self._ble.config('mac')
		hex_mac = hexlify(byte_mac) 
		print("Adresse MAC : %s" %hex_mac.decode("ascii"))
		

	# Interruption pour gérer les réceptions
	def irq(self, handler):
		self._handler = handler

	# Surveille les connexions afin d'envoyer des notifications
	def _irq(self, event, data):

		# Si un central se connecte
		if event == _IRQ_CENTRAL_CONNECT:
			conn_handle, _, _ = data
			self._connections.add(conn_handle)
			print("Nouvelle connexion", conn_handle)

		# Si un central se déconnecte
		elif event == _IRQ_CENTRAL_DISCONNECT:
			conn_handle, _, _ = data
			print("Déconnecté", conn_handle)
			if conn_handle in self._connections:
				self._connections.remove(conn_handle)
			# Redémarre l'advertising pour permettre de nouvelles connexions
			self._advertise()

		# Lorsqu'un client écrit dans une caractéristique exposée par le serveur
		# (gestion des évènements de recéption depuis le central)
		elif event == _IRQ_GATTS_WRITE:
			conn_handle, value_handle = data
			if conn_handle in self._connections and value_handle == self._rx_handle:
				self._rx_buffer += self._ble.gatts_read(self._rx_handle)
				if self._handler:
					self._handler()
	
	# Appelée pour vérifier s'il y a des messages en attente de lecture dans RX
	def any(self):
		return len(self._rx_buffer)

	# Retourne les catactères reçus dans RX
	def read(self, sz=None):
		if not sz:
			sz = len(self._rx_buffer)
		result = self._rx_buffer[0:sz]
		self._rx_buffer = self._rx_buffer[sz:]
		return result

	# Ecrit dans TX un message à l'attention du central
	def write(self, data):
		for conn_handle in self._connections:
			self._ble.gatts_notify(conn_handle, self._tx_handle, data)

	# Mets fin à la connexion au port série simulé
	def close(self):
		for conn_handle in self._connections:
			self._ble.gap_disconnect(conn_handle)
		self._connections.clear()

	# Pour démarrer l'advertising, précise qu'un central pourra se connecter au périphérique
	def _advertise(self, interval_us=500000):
		self._ble.gap_advertise(interval_us, adv_data=self._payload, connectable = True)

	# Est-ce que le périphérique est connecté à un central ?
	def is_connected(self):
		return len(self._connections) > 0


# Programme principal
def demo():

	print("Périphérique BLE")

	# Pause d'une seconde pour laisser à l'I2C le temps de s'initialiser
	import time
	time.sleep_ms(1000)

	# Instanciation du BLE
	ble = bluetooth.BLE()
	uart = BLEUART(ble)

	# Gestionnaire de l'évènement de réception
	def on_rx():
		print("Données reçues du central : ", uart.read().decode().strip())

	# Réception (asynchrone) des données (ie réaction aux écritures du central dans RX).
	uart.irq(handler=on_rx)

	# Structure de gestion des erreurs pour gérer les interruptions du clavier
	try:
		while True:
		
			# Conversion en texte des valeurs renvoyées par les capteurs
			stemp = str(random.uniform(0, 10))

			# Affichage sur le port série de l'USB USER
			print(stemp)

			if uart.is_connected():

				# On concatène les données :
				data = stemp

				# On les envoie au central (ie on les notifie dans TX):
				uart.write(data)

				print("Données envoyées au central : " + data)

			# Temporisation de 5 secondes
			time.sleep_ms(2000)

	# Si l'utilisateur appuie sur CTRL+C
	except KeyboardInterrupt:
		pass # On ferme la connexion avant de quitter

	# Ferme l'UART actif
	uart.close()

# Si le nom du script est "main", exécute la fonction "demo()"
if __name__ == "__main__":
	demo()