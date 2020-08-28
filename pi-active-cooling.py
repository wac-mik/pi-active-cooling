#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import sys
import psutil
import logging
from systemd.journal import JournalHandler

# Const
PIN            = 18
TEMP_FAN_START = 55 
TEMP_FAN_MAX   = 65
FAN_SPEED_MIN  = 35
    
log = logging.getLogger(__name__)

def get_pi_temperature():
    # Returns current temperature of the CPU in Celsius degree
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        return float(f.read()) / 1000

def get_cpu_usage():
    return psutil.cpu_percent()

def apply_fan_requirements(requested_fan_speed):
    # Due to hardware limitations fan cannot rotate for small values of PWM duty cycle. 
    # This method increases fan speed if requested_fan_speed is in range (0; FAN_SPEED_MIN)
    return FAN_SPEED_MIN if (requested_fan_speed > 0 and requested_fan_speed < FAN_SPEED_MIN) else requested_fan_speed

def calculate_fan_speed_based_on_temp(cpu_temperature):
    if cpu_temperature <= TEMP_FAN_START:
        calculated_fan_speed = 0
    elif cpu_temperature >= TEMP_FAN_MAX:
        calculated_fan_speed = 100
    else:
        calculated_fan_speed = round((cpu_temperature - TEMP_FAN_START) / (TEMP_FAN_MAX - TEMP_FAN_START) * 100)

    return calculated_fan_speed

def calculate_fan_speed_based_on_cpu_usage(cpu_usage):
    return 100 if cpu_usage > 95 else 0

def calculate_fan_speed():
    # Set fan_speed based on PI temperature
    cpu_temp  = get_pi_temperature()
    cpu_usage = get_cpu_usage()

    fan_speed = max(calculate_fan_speed_based_on_temp(cpu_temp), calculate_fan_speed_based_on_cpu_usage(cpu_usage))
    fan_speed = apply_fan_requirements(fan_speed)

    log.info("Temp: {:.2f}C  Cpu: {:.2f}%  Fan: {}%".format(cpu_temp, cpu_usage, fan_speed))
    
    return fan_speed

def init_fan():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(PIN, GPIO.OUT)

    fan = GPIO.PWM(PIN, 100)
    fan.start(0)

    return fan

def deinit_fan(fan):
    fan.stop()
    GPIO.cleanup()

def init_logger():
    log.setLevel(logging.INFO)
    log.addHandler(JournalHandler())
    log.addHandler(logging.StreamHandler(sys.stdout))

def run():
    init_logger()
    fan = init_fan()
    while True:
        fan.ChangeDutyCycle(calculate_fan_speed())
        time.sleep(1)
    deinit_fan(fan)

run()

