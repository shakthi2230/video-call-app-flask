from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, join_room, leave_room, emit
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')  # Allow CORS for testing

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Create random room ID and redirect to it
@app.route('/create-room')
def create_room():
    room_id = str(uuid.uuid4())
    return redirect(f'/join/{room_id}')

# Join room via manual form
@app.route('/join-room', methods=['POST'])
def join_custom_room():
    room = request.form['room']
    return redirect(f'/join/{room}')

# Room page
@app.route('/join/<room>')
def room_view(room):
    return render_template('room.html', room=room)

# WebSocket: on user join
@socketio.on('join')
def handle_join(room):
    join_room(room)
    emit('user-joined', request.sid, room=room)  # Send socket ID to others

# WebSocket: handle WebRTC signaling
@socketio.on('offer')
def handle_offer(offer, to_sid):
    emit('offer', (offer, request.sid), room=to_sid)

@socketio.on('answer')
def handle_answer(answer, to_sid):
    emit('answer', (answer, request.sid), room=to_sid)

@socketio.on('ice-candidate')
def handle_ice(candidate, to_sid):
    emit('ice-candidate', (candidate, request.sid), room=to_sid)

# WebSocket: on disconnect
@socketio.on('disconnect')
def handle_disconnect():
    emit('user-left', request.sid, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

