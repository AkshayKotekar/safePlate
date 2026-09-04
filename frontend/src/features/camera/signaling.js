export function openSignalingSocket(sessionId, role, handlers) {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/api/camera/signal/${sessionId}/${role}`);

  ws.onopen = () => handlers.onOpen?.();
  ws.onclose = () => handlers.onClose?.();
  ws.onerror = (e) => handlers.onError?.(e);
  ws.onmessage = (evt) => {
    const message = JSON.parse(evt.data);
    handlers.onMessage?.(message);
  };

  return {
    send: (message) => {
      if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(message));
    },
    close: () => ws.close(),
  };
}

export const RTC_CONFIG = {
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
};
