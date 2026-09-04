import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { openSignalingSocket, RTC_CONFIG } from "../features/camera/signaling.js";

export default function PhoneCamera() {
  const { sessionId } = useParams();
  const videoRef = useRef(null);
  const pcRef = useRef(null);
  const socketRef = useRef(null);
  const pendingCandidatesRef = useRef([]);
  const [status, setStatus] = useState("Requesting camera access…");
  const [connectionState, setConnectionState] = useState("new");
  const [error, setError] = useState(null);

  useEffect(() => {
    let stream;
    let cancelled = false;

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false,
        });
      } catch (err) {
        if (!cancelled) {
          setError(
            err.name === "NotAllowedError"
              ? "Camera permission denied. Please allow camera access and reload."
              : `Camera error: ${err.message}. If this address is not localhost/https, your browser may be blocking camera access — see the connection instructions on the PC screen.`
          );
        }
        return;
      }
      if (cancelled) {
        stream.getTracks().forEach((t) => t.stop());
        return;
      }

      videoRef.current.srcObject = stream;
      setStatus("Camera ready — connecting to SafePlate…");

      const pc = new RTCPeerConnection(RTC_CONFIG);
      pcRef.current = pc;
      stream.getTracks().forEach((track) => pc.addTrack(track, stream));

      pc.onconnectionstatechange = () => {
        setConnectionState(pc.connectionState);
        if (pc.connectionState === "connected") {
          setStatus("LIVE — streaming to PC");
          socketRef.current?.send({ type: "media-active" });
        } else if (pc.connectionState === "failed" || pc.connectionState === "disconnected") {
          setStatus("Connection lost — waiting to reconnect…");
        }
      };

      pc.onicecandidate = (event) => {
        if (event.candidate) {
          socketRef.current?.send({ type: "ice-candidate", candidate: event.candidate });
        }
      };

      const socket = openSignalingSocket(sessionId, "phone", {
        onOpen: async () => {
          setStatus("Connected to SafePlate — negotiating video…");
          await sendOffer(pc, socket);
        },
        onMessage: async (message) => {
          if (message.type === "answer") {
            await pc.setRemoteDescription(new RTCSessionDescription(message.sdp));
            for (const c of pendingCandidatesRef.current) await pc.addIceCandidate(c);
            pendingCandidatesRef.current = [];
          } else if (message.type === "ice-candidate" && message.candidate) {
            const candidate = new RTCIceCandidate(message.candidate);
            if (pc.remoteDescription) await pc.addIceCandidate(candidate);
            else pendingCandidatesRef.current.push(candidate);
          } else if (message.type === "request-offer") {
            await sendOffer(pc, socket);
          }
        },
        onClose: () => setStatus("Disconnected from SafePlate — reload to retry"),
      });
      socketRef.current = socket;
    }

    async function sendOffer(pc, socket) {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      socket.send({ type: "offer", sdp: offer });
    }

    start();
    return () => {
      cancelled = true;
      stream?.getTracks().forEach((t) => t.stop());
      pcRef.current?.close();
      socketRef.current?.close();
    };
  }, [sessionId]);

  return (
    <div style={styles.wrap}>
      <div style={styles.bar}>
        <span style={{ ...styles.dot, background: connectionState === "connected" ? "#33d17a" : "#e05252" }} />
        <span>{status}</span>
      </div>
      {error ? (
        <div style={styles.errorBox}>{error}</div>
      ) : (
        <video ref={videoRef} autoPlay playsInline muted style={styles.video} />
      )}
    </div>
  );
}

const styles = {
  wrap: { display: "flex", flexDirection: "column", height: "100vh", background: "#0b0f14", color: "#e8eef5", fontFamily: "sans-serif" },
  bar: { padding: "10px 14px", display: "flex", alignItems: "center", gap: 8, background: "#101820", fontSize: 14 },
  dot: { width: 10, height: 10, borderRadius: "50%" },
  video: { flex: 1, width: "100%", objectFit: "cover", background: "#000" },
  errorBox: { padding: 24, color: "#e05252", fontSize: 15, lineHeight: 1.5 },
};
