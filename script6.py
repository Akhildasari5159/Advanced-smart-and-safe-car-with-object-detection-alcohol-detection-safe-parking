import time
import smtplib
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import paho.mqtt.client as mqtt

# Initialize I2C and ADC with BCM pin numbering
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Define ADC channels
channel_sensor1 = AnalogIn(ads, ADS.P0)
channel_sensor2 = AnalogIn(ads, ADS.P1)

# Define the buzzer pin as a BCM pin
buzzer = 4  # Replace with the actual BCM pin number

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
email_address = 'your_mailid@gmail.com'
email_password = 'your_passcode'
recipient_email = 'sender_mailid@gmail.com'

# Car configuration
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
car_pins = [21, 20, 16, 12]

def send_email(message):
    subject = 'Car and Alcohol Sensor Alert'
    msg = 'Subject: Car and Alcohol Sensor Alert\n\n' + message

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(email_address, recipient_email, msg)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def stop_car():
    for pin in car_pins:
        GPIO.output(pin, GPIO.LOW)

# Set up GPIO mode and configure the buzzer pin
GPIO.setup(buzzer, GPIO.OUT)
for pin in car_pins:
    GPIO.setup(pin, GPIO.OUT)

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("ack")

def on_message(client, userdata, msg):
    h = str(msg.payload)
    print(h)
    if msg.payload.decode('utf-8') == "forward":
        print("Moving forward")
        forward()
    elif msg.payload.decode('utf-8') == "backward":
        print("Moving backward")
        backward()
    elif msg.payload.decode('utf-8') == "sb":
        print("Moving Stright_backward")
        sb()
    elif msg.payload.decode('utf-8') == "right":
        print("Moving right")
        right()
    elif msg.payload.decode('utf-8') == "hr":
        print("Moving half right")
        hr()
    elif msg.payload.decode('utf-8') == "left":
        print("Moving left")
        left()
    elif msg.payload.decode('utf-8') == "hl":
        print("Moving half left")
        hl()
    elif msg.payload.decode('utf-8') == "stop":
        print("Stop")
        stop()

client.on_connect = on_connect
client.on_message = on_message
client.connect('broker.mqtt-dashboard.com', 1883, 60)
client.loop_start()

try:
    while True:
        adcValue1 = channel_sensor1.value
        adcValue2 = channel_sensor2.value

        # Convert ADC values to alcohol levels
        mgL1 = 0.67 * adcValue1 / 32767.0  # Assuming ADS1115 is in 16-bit mode
        mgL2 = 0.67 * adcValue2 / 32767.0

        print(f"Sensor 1 Value: {adcValue1}, Alcohol Level (mg/L): {mgL1}")
        print(f"Sensor 2 Value: {adcValue2}, Alcohol Level (mg/L): {mgL2}")

        if mgL2 > 0.9:
            send_email("High Alcohol Level Detected. Car Stopped.")
            GPIO.output(buzzer, GPIO.HIGH)
            stop_car()
            time.sleep(0.3)
        elif mgL1 > 0.8:
            send_email("Alcohol Detected. Be Safe while Driving.")
            GPIO.output(buzzer, GPIO.HIGH)
            time.sleep(0.3)
        elif mgL1 < 0.5:
            send_email("No Alcohol Detected. Normal.")
            print("No Alcohol Detected. Normal.")
        else:
            print("Have a safe and happy driving")

        GPIO.output(buzzer, GPIO.LOW)
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
