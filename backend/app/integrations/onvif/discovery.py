"""STUB — future ONVIF device discovery/configuration (Milestone 37). Not every
CCTV device supports ONVIF; RTSP/manual configuration remain the fallback
(spec §36). Not used by the phone-camera MVP.
"""


def discover_onvif_devices() -> list[dict]:
    raise NotImplementedError("ONVIF discovery is future work — see spec §36, Milestone 37")
