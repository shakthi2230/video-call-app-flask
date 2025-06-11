const socket = io();
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');

let localStream;
let peer;

async function start() {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    localVideo.srcObject = localStream;

    peer = new RTCPeerConnection();

    localStream.getTracks().forEach(track => peer.addTrack(track, localStream));

    peer.ontrack = e => {
        remoteVideo.srcObject = e.streams[0];
    };

    peer.onicecandidate = e => {
        if (e.candidate) {
            socket.emit('signal', { room: ROOM_ID, candidate: e.candidate });
        }
    };

    socket.emit('join', { room: ROOM_ID });

    socket.on('user-joined', async () => {
        const offer = await peer.createOffer();
        await peer.setLocalDescription(offer);
        socket.emit('signal', { room: ROOM_ID, sdp: offer });
    });

    socket.on('signal', async data => {
        if (data.sdp) {
            await peer.setRemoteDescription(new RTCSessionDescription(data.sdp));
            if (data.sdp.type === 'offer') {
                const answer = await peer.createAnswer();
                await peer.setLocalDescription(answer);
                socket.emit('signal', { room: ROOM_ID, sdp: answer });
            }
        } else if (data.candidate) {
            await peer.addIceCandidate(new RTCIceCandidate(data.candidate));
        }
    });
}

start();
