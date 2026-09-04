import React, { useEffect, useRef, useState } from "react";
import { QRCodeSVG } from "qrcode.react";
import { api } from "../services/api.js";
import { openSignalingSocket, RTC_CONFIG } from "../features/camera/signaling.js";

export default function LiveMonitoring() {
  const [session, setSession] = useState(null);
  const [connectionState, setConnectionState] = useState("idle");
  const [sessionStatus, setSessionStatus] = useState("pending");
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const pcRef = useRef(null);
  const socketRef = useRef(null);
  const pendingCandidatesRef = useRef([]);
  const pollRef = useRef(null);

  async function generateSession() {
    setError(null);
    try {
      const s = await api.createCameraSession("Phone Camera");
      setSession(s);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    if (!session) return;
    connectViewer(session.id);
    pollRef.current = setInterval(async () => {
      try {
        const s = await api.getCameraSessionStatus(session.id);
        setSessionStatus(s.status);
      } catch {}
    }, 3000);
    return () => {
      clearInterval(pollRef.current);
      pcRef.current?.close();
      socketRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.id]);

  function connectViewer(sessionId) {
    const pc = new RTCPeerConnection(RTC_CONFIG);
    pcRef.current = pc;

    pc.ontrack = (event) => {
      if (videoRef.current) videoRef.current.srcObject = event.streams[0];
    };
    pc.onconnectionstatechange = () => setConnectionState(pc.connectionState);
    pc.onicecandidate = (event) => {
      if (event.candidate) socketRef.current?.send({ type: "ice-candidate", candidate: event.candidate });
    };

    const socket = openSignalingSocket(sessionId, "viewer", {
      onOpen: () => socket.send({ type: "request-offer" }),
      onMessage: async (message) => {
        if (message.type === "offer") {
          await pc.setRemoteDescription(new RTCSessionDescription(message.sdp));
          for (const c of pendingCandidatesRef.current) await pc.addIceCandidate(c);
          pendingCandidatesRef.current = [];
          const answer = await pc.createAnswer();
          await pc.setLocalDescription(answer);
          socket.send({ type: "answer", sdp: answer });
        } else if (message.type === "ice-candidate" && message.candidate) {
          const candidate = new RTCIceCandidate(message.candidate);
          if (pc.remoteDescription) await pc.addIceCandidate(candidate);
          else pendingCandidatesRef.current.push(candidate);
        }
      },
    });
    socketRef.current = socket;
  }

  function reconnect() {
    pcRef.current?.close();
    socketRef.current?.close();
    pendingCandidatesRef.current = [];
    connectViewer(session.id);
  }

  function resetSession() {
    clearInterval(pollRef.current);
    pcRef.current?.close();
    socketRef.current?.close();
    setSession(null);
    setConnectionState("idle");
    setSessionStatus("pending");
  }

  return (
    <div>
      <h1>Live Monitoring</h1>
      <p className="subtitle">Phone camera over WebRTC — today's video source. RTSP/ONVIF/NVR sources will plug into the same viewer later.</p>

      {error && <div style={{ color: "var(--red)", marginBottom: 16 }}>{error}</div>}

      {!session ? (
        <div className="card" style={{ maxWidth: 420 }}>
          <h2 style={{ marginTop: 0 }}>Connect Phone</h2>
          <p style={{ color: "var(--muted)", fontSize: 14 }}>
            Generate a pairing session, then scan the QR code with your phone.
          </p>
          <button className="btn" onClick={generateSession}>Generate Camera Session</button>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 20 }}>
          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
              <div>
                <span className={`status-dot ${connectionState === "connected" ? "status-live" : "status-offline"}`} />
                <strong>{session.name}</strong>{" "}
                <span className="camera-meta">session status: {sessionStatus} · webrtc: {connectionState}</span>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn btn-secondary" onClick={reconnect}>Reconnect</button>
                <button className="btn btn-secondary" onClick={resetSession}>New Session</button>
              </div>
            </div>
            <div className="camera-video-wrap" style={{ aspectRatio: "16/9" }}>
              {connectionState === "connected" ? (
                <video ref={videoRef} autoPlay playsInline style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              ) : (
                <div className="camera-placeholder">
                  Waiting for phone to connect…
                  <br />
                  Scan the QR code with your phone's camera app.
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <h2 style={{ marginTop: 0 }}>Scan to Connect</h2>
            <div style={{ background: "#fff", padding: 16, borderRadius: 8, display: "inline-block" }}>
              <QRCodeSVG value={session.phone_join_url} size={200} />
            </div>
            <div className="link-box">{session.phone_join_url}</div>

            <div className="instructions-box">
              <strong>First-time setup on the phone:</strong>
              <ol>
                <li>Connect the phone to the SAME Wi-Fi network as this computer.</li>
                <li>
                  Browsers block camera access on a plain <code>http://</code> address that isn't "localhost". On
                  Android Chrome, open <code>chrome://flags/#unsafely-treat-insecure-origin-as-secure</code>, add the
                  address above, set it to <strong>Enabled</strong>, and relaunch Chrome. (One-time setup.)
                </li>
                <li>Scan the QR code (or open the link above) and allow camera access.</li>
              </ol>
              <p style={{ color: "var(--muted)", fontSize: 12, marginTop: 8 }}>
                Alternative if you'd rather not use the Chrome flag: ask to set up a local HTTPS certificate (mkcert)
                or a tunnel (ngrok) instead — either works without the flag.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
