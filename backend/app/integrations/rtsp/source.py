"""STUB — future RTSP CCTV ingestion (Milestone 36). Not used by the phone-camera
MVP. Do not implement until real CCTV hardware is available (spec §33, §58).

When implemented, RTSPSource will implement the same VideoSource interface as
PhoneWebRTCSource (app/api/camera.py's signaling flow) so the YOLO inference
pipeline (app/ai/vision) doesn't need to change at all — it will pull frames
via OpenCV/FFmpeg from an RTSP URL instead of receiving them over WebRTC.
"""


class RTSPSource:
    def __init__(self, rtsp_url: str, username: str | None = None, password: str | None = None):
        raise NotImplementedError("RTSP ingestion is future work — see spec §35, Milestone 36")
