from flask import Flask, Response, request
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import cv2
import os
import threading
import time
from datetime import datetime

app = Flask(__name__)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in (17, 27, 23, 24, 18, 25):
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
pwm_a = GPIO.PWM(18, 1000)
pwm_b = GPIO.PWM(25, 1000)
pwm_a.start(0)
pwm_b.start(0)

speed = 50
press_cooldown = 0.5
last_press_time = 0

picam2 = Picamera2()
picam2.start()
os.makedirs("mvlmnav_room", exist_ok=True)
image_count = 0
capturing = False

def drive(a1, a2, b1, b2, duty_a, duty_b, secs=0.3):
    GPIO.output(17, a2); GPIO.output(27, a1)
    GPIO.output(23, b2); GPIO.output(24, b1)
    pwm_a.ChangeDutyCycle(duty_a); pwm_b.ChangeDutyCycle(duty_b)
    time.sleep(secs)
    pwm_a.ChangeDutyCycle(0); pwm_b.ChangeDutyCycle(0)
    GPIO.output(17, GPIO.LOW); GPIO.output(27, GPIO.LOW)
    GPIO.output(23, GPIO.LOW); GPIO.output(24, GPIO.LOW)

def can_move():
    global last_press_time
    now = time.time()
    if now - last_press_time < press_cooldown:
        return False
    last_press_time = now
    return True

def capture_images():
    global image_count, capturing
    while image_count < 100 and capturing:
        frame = picam2.capture_array()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        path = f"mvlmnav_room/img_{ts}.jpg"
        cv2.imwrite(path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        image_count += 1
        print(f"[{image_count}/100] {path}")
        if image_count >= 100:
            capturing = False
            break
        time.sleep(1)

def get_frame():
    while True:
        frame = picam2.capture_array()
        frame = cv2.resize(frame, (320, 240))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

html = '''
<html>
<head>
<style>
body { font-family: Arial; margin: 0; background: #20b2aa; }
.container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
h1 { color: #fff; margin: 15px 0; font-size: 28px; }
.camera { width: 320px; height: 240px; border: 4px solid #fff; border-radius: 8px; }
.status { color: #fff; margin-top: 20px; font-size: 18px; font-weight: bold; }
.progress { color: #ffff00; margin-top: 10px; font-size: 16px; font-weight: bold; }
.collect-btn { background: #d9534f; width: 260px; margin-top: 20px; padding: 14px; font-size: 16px; color: #fff; border: none; cursor: pointer; border-radius: 6px; font-weight: bold; }
.collect-btn.active { background: #00cc00; color: #000; }
.speed-control { margin-top: 20px; display: flex; align-items: center; gap: 15px; color: #fff; font-weight: bold; }
.controls { display: grid; grid-template-columns: repeat(3, 80px); gap: 10px; margin-top: 25px; }
button { padding: 12px; font-size: 16px; background: #0a7a73; color: #fff; border: none; cursor: pointer; border-radius: 6px; font-weight: bold; }
button:active { transform: scale(0.95); }
</style>
</head>
<body>
<div class="container">
<h1>MVLMNAV Manual</h1>
<img src="/video_feed" class="camera">
<div class="status">Images: <span id="count">0</span>/100</div>
<div class="progress" id="progress"></div>
<button class="collect-btn" id="collectBtn" onclick="toggleCollect()">START COLLECTING</button>
<div class="speed-control">
<label>Speed:</label>
<input type="range" min="10" max="100" value="50" id="speedSlider" oninput="updateSpeed(this.value)">
<span id="speedValue">50%</span>
</div>
<div class="controls">
<div></div>
<button onclick="moveBot('/forward')">W</button>
<div></div>
<button onclick="moveBot('/left')">A</button>
<button onclick="moveBot('/backward')">S</button>
<button onclick="moveBot('/right')">D</button>
</div>
</div>
<script>
let isCollecting = false;
function toggleCollect() {
    isCollecting = !isCollecting;
    fetch('/collect?start=' + (isCollecting ? '1' : '0'));
    document.getElementById('collectBtn').textContent = isCollecting ? 'STOP COLLECTING' : 'START COLLECTING';
    document.getElementById('collectBtn').classList.toggle('active');
}
function updateSpeed(val) {
    document.getElementById('speedValue').textContent = val + '%';
    fetch('/setspeed?speed=' + val);
}
function moveBot(dir) { fetch(dir); }
setInterval(() => {
    fetch('/getcount').then(r => r.json()).then(data => {
        document.getElementById('count').textContent = data.count;
        document.getElementById('progress').textContent = data.count + '%';
        if (data.count >= 100) {
            document.getElementById('progress').textContent = 'COMPLETE';
            document.getElementById('collectBtn').disabled = true;
            isCollecting = false;
        }
    });
}, 500);
document.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (k === 'w') moveBot('/forward');
    if (k === 'a') moveBot('/left');
    if (k === 's') moveBot('/backward');
    if (k === 'd') moveBot('/right');
});
</script>
</body>
</html>
'''

@app.route('/video_feed')
def video_feed():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/collect')
def collect():
    global capturing, image_count, capture_thread
    start = request.args.get('start') == '1'
    if start and not capturing:
        image_count = 0
        capturing = True
        threading.Thread(target=capture_images, daemon=True).start()
    elif not start:
        capturing = False
    return 'OK'

@app.route('/setspeed')
def setspeed():
    global speed
    speed = int(request.args.get('speed', 50))
    return 'OK'

@app.route('/forward')
def forward():
    if can_move():
        drive(GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.HIGH, speed, speed)
    return 'OK'

@app.route('/backward')
def backward():
    if can_move():
        drive(GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW, speed, speed)
    return 'OK'

@app.route('/left')
def left():
    if can_move():
        drive(GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH, speed, speed)
    return 'OK'

@app.route('/right')
def right():
    if can_move():
        drive(GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW, speed, speed)
    return 'OK'

@app.route('/getcount')
def getcount():
    return {"count": image_count}

@app.route('/')
def index():
    return html

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        pwm_a.stop(); pwm_b.stop()
        GPIO.cleanup()
(base) malharlabade@Malhars-MacBook-Air code % 
