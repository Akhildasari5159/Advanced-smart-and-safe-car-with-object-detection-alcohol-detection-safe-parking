import RPi.GPIO as GPIO
import time


# IR Sensor Configuration
sensor_ir1 = 6
sensor_ir2 = 13
sensor_ir3 = 19
sensor_ir4 = 26

# Ultrasonic Sensor Configuration
sensor_ultrasonic = 17
echo_ultrasonic = 27

buzzer_pin = 4  # Change this to your buzzer's GPIO pin

# Set up GPIO mode and initial state
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# IR Sensor Setup
sensor_pins = [sensor_ir1, sensor_ir2, sensor_ir3, sensor_ir4]
for sensor_pin in sensor_pins:
    GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Ultrasonic Sensor Setup
GPIO.setup(sensor_ultrasonic, GPIO.OUT)
GPIO.setup(echo_ultrasonic, GPIO.IN)

GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.output(buzzer_pin, GPIO.LOW)

# Function to activate the buzzer
def activate_buzzer():
    GPIO.output(buzzer_pin, GPIO.HIGH)
    time.sleep(1)  # Buzzer on for 1 second
    GPIO.output(buzzer_pin, GPIO.LOW)

# Function to measure the distance using the ultrasonic sensor
def distance_ultrasonic():
    GPIO.output(sensor_ultrasonic, True)
    time.sleep(0.00001)
    GPIO.output(sensor_ultrasonic, False)
    StartTime = time.time()
    StopTime = time.time()
    while GPIO.input(echo_ultrasonic) == 0:
        StartTime = time.time()
    while GPIO.input(echo_ultrasonic) == 1:
        StopTime = time.time()
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    return distance

try:
    while True:
        # IR Sensors
        ir_status = any(GPIO.input(sensor_pin) == GPIO.LOW for sensor_pin in sensor_pins)
        if ir_status:
            print("IR Sensor Status: object detected")
            activate_buzzer()

        # Ultrasonic Sensor
        dist_ultrasonic = distance_ultrasonic()
        print("Ultrasonic Sensor: Object is at a distance of %.1f cm" % dist_ultrasonic)

        if dist_ultrasonic < 20:
            print("Ultrasonic Sensor: Object detected!")
            activate_buzzer()

        time.sleep(0.1)  # Adjust the delay as needed
        
except KeyboardInterrupt:
    pass

#finally:
#   GPIO.cleanup()
