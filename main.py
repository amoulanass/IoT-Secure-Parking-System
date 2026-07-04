fom machine import Pin, SoftSPI,PWM, time_pulse_us
from mfrc522 import MFRC522
import time

# Définition des broches pour le SPI
sck = Pin(18, Pin.OUT)
copi = Pin(23, Pin.OUT)  # Controller out, peripheral in
cipo = Pin(19, Pin.OUT)  # Controller in, peripheral out
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=copi, miso=cipo)

# Définition de la broche SDA pour MFRC522
sda = Pin(21, Pin.OUT)
reader = MFRC522(spi, sda)

# Définition des broches pour les LEDs
led_rouge = Pin(22, Pin.OUT)  # Broche pour la LED rouge (non autorisé)
led_verte = Pin(2, Pin.OUT)   # Broche pour la LED verte (autorisé)

# Définition des broches pour le SPI
sck = Pin(18, Pin.OUT)
copi = Pin(23, Pin.OUT)  # Controller out, peripheral in
cipo = Pin(19, Pin.OUT)  # Controller in, peripheral out
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=copi, miso=cipo)

# Définition de la broche SDA pour MFRC522
sda = Pin(21, Pin.OUT)
reader = MFRC522(spi, sda)

# Définition de la broche pour le servomoteur
servo = PWM(Pin(5))  # Remplacez 25 par la broche PWM de votre choix
servo.freq(50)  # Fréquence standard pour servomoteurs (50 Hz)

# Configuration des broches place
led1 = Pin(12, Pin.OUT)  # LED connectée au GPIO 12
led2 = Pin(13, Pin.OUT)  # LED connectée au GPIO 13
trigger = Pin(5, Pin.OUT)  # Broche TRIG du capteur
echo = Pin(26, Pin.IN)  # Broche ECHO du capteur

# Liste des UID autorisés (exemple de 4 octets par UID)
# uid_autorises = [0x39, 0x69, 0x15, 0xB3]
   
uid_autorises = [
    [0x39, 0x69, 0x15, 0xB3],  # UID autorisé exemple
]
# Fonction pour vérifier si l'UID est dans la liste des autorisés
def est_uid_autorise(uid):
    # Si l'UID a 5 octets, on ne garde que les 4 premiers
    if len(uid) == 5:
        uid = uid[:4]  # Ne garder que les 4 premiers octets
    for autorise in uid_autorises:
        if uid == autorise:  # Comparaison des listes
            return True
    return False

# Fonction pour déplacer le servomoteur à un angle donné
def set_servo_angle(angle):
    # Convertir l'angle en cycle de travail PWM (duty cycle)
    # Les servos typiques utilisent des impulsions entre 0.5 ms (0°) et 2.5 ms (180°)
    duty = 4096 * ((0.5 + (angle / 180) * 2) / 20)
    servo.duty_u16(int(duty))

# Fonction pour vérifier si l'UID est dans la liste des autorisés
def est_uid_autorise(uid):
    # Si l'UID a 5 octets, on ne garde que les 4 premiers
    if len(uid) == 5:
        uid = uid[:4]  # Ne garder que les 4 premiers octets
    for autorise in uid_autorises:
        if uid == autorise:  # Comparaison des listes
            return True
    return False

# Fonction pour mesurer la distance
def measure_distance():
    trigger.off()  # Assurez-vous que TRIG est LOW
    time.sleep_us(2)  # Attente 2µs
    trigger.on()  # Envoyer une impulsion de 10µs
    time.sleep_us(10)
    trigger.off()

    # Mesurer la durée de l'écho
    duration = time_pulse_us(echo, 1)

    # Calculer la distance en cm
    distance = (duration * 0.0343) / 2
    return distance

while True:
   
    try:
        print('Place Card In Front Of Device To Write Unique Address')
        print('')
        # Demander à détecter une carte
        (status, tag_type) = reader.request(reader.CARD_REQIDL)
        if status == reader.OK:
            (status, raw_uid) = reader.anticoll()
            if status == reader.OK:
                print('New Card Detected')
                print('  - Tag Type: 0x%02x' % tag_type)
                print(raw_uid)
                print('  - UID: 0x%02x%02x%02x%02x' % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
               
                # Vérifier si l'UID est dans la liste des autorisés
                if est_uid_autorise(raw_uid):
                    print("Carte autorisée")
                    led_verte.on()  # Allumer la LED verte
                    led_rouge.off()  # Éteindre la LED rouge
                    # Faire tourner le servomoteur de 0° à 90°
                    set_servo_angle(60)
                else:
                    print("Carte non autorisée")
                    led_rouge.on()  # Allumer la LED rouge
                    led_verte.off()  # Éteindre la LED verte
                time.sleep(15)
       
    except KeyboardInterrupt:
        break
    dist = measure_distance()
    print("Distance: %.1f cm" % dist)
         # Allumer la LED si la distance est inférieure à 15 cm
    if dist < 15:
        led1.on()  # Allumer la LED 1
        led2.off()  # Éteindre la LED 2
    else:
        led1.off()  # Éteindre la LED 1
        led2.on()  # Allumer la LED 2
        time.sleep(1)  # Pause de 1 seconde avant la prochaine mesure

