(base) malharlabade@Malhars-MacBook-Air code % cat      web_control.py

from gpiozero import DigitalOutputDevice, PWMOutputDevice
from flask import Flask, Response, request
from picamera2 import Picamera2
import cv2
app = Flask(__name__)
IN1 = DigitalOutputDevice(17)
IN2 = DigitalOutputDevice(27)
IN3 = DigitalOutputDevice(23)
IN4 = DigitalOutputDevice(24)
ENA = PWMOutputDevice(18, frequency=1000)
ENB = PWMOutputDevice(25, frequency=1000)
speed = 0.75
picam2 = Picamera2()
picam2.start()
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
body { font-family: Arial; margin: 0; padding: 0; background: #20b2aa; }
.container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
h1 { color: #fff; margin: 20px 0; font-size: 28px; }
.camera { width: 320px; height: 240px; border: 4px solid #fff; border-radius: 8px; }
.speed-control { margin-top: 25px; display: flex; align-items: center; gap: 15px; }
.speed-control label { color: #fff; font-weight: bold; }
.speed-control input { width: 200px; }
.speed-value { color: #fff; font-weight: bold; min-width: 40px; }
.controls { display: grid; grid-template-columns: repeat(3, 80px); gap: 10px; margin-top: 25px; }
button { padding: 12px; font-size: 16px; background: #0a7a73; color: #fff; border: none; cursor: pointer; border-radius: 6px; font-weight: bold; }
button:hover { background: #086960; }
button:active { transform: scale(0.95); }
</style>
</head>
<body>
<div class="container">
<h1>COLLAB02</h1>
<img src="/video_feed" class="camera">
<div class="speed-control">
<label>Speed:</label>
<input type="range" min="0" max="255" value="191" id="speedSlider" oninput="updateSpeed(this.value)">
<span class="speed-value" id="speedValue">191</span>
</div>
<div class="controls">
<div></div>
<button onmousedown="fetch('/backward')" onmouseup="fetch('/stop')">Up</button>
<div></div>
<button onmousedown="fetch('/left')" onmouseup="fetch('/stop')">Left</button>
<button onmousedown="fetch('/forward')" onmouseup="fetch('/stop')">Down</button>
<button onmousedown="fetch('/right')" onmouseup="fetch('/stop')">Right</button>
</div>
</div>
<script>
function updateSpeed(val) {
    document.getElementById('speedValue').textContent = val;
    fetch('/setspeed?speed=' + val);
}
</script>
</body>
</html>
'''
@app.route('/video_feed')
def video_feed():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/setspeed')
def setspeed():
    global speed
    speed = int(request.args.get('speed', 191)) / 255.0
    return 'OK'
@app.route('/forward')
def forward():
    IN1.on(); IN2.off(); IN3.on(); IN4.off()
    ENA.value = speed; ENB.value = speed
    return 'OK'
@app.route('/left')
def left():
    IN1.on(); IN2.off(); IN3.on(); IN4.off()
    ENA.value = speed * 0.5; ENB.value = speed
    return 'OK'
@app.route('/backward')
def backward():
    IN1.off(); IN2.on(); IN3.off(); IN4.on()
    ENA.value = speed; ENB.value = speed
    return 'OK'
@app.route('/right')
def right():
    IN1.on(); IN2.off(); IN3.off(); IN4.on()
    ENA.value = speed; ENB.value = speed * 0.5
    return 'OK'
@app.route('/stop')
def stop():
    ENA.value = 0; ENB.value = 0
    return 'OK'
@app.route('/')
def index():
    return html
app.run(host='0.0.0.0', port=5000)
(base) malharlabade@Malhars-MacBook-Air code % 
