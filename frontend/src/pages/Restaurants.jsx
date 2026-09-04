import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api.js";
import ScoreGauge from "../components/ScoreGauge.jsx";
import { IconLocate } from "../components/icons.jsx";

function haversineKm(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export default function Restaurants() {
  const [locality, setLocality] = useState("");
  const [restaurants, setRestaurants] = useState([]);
  const [userLocation, setUserLocation] = useState(null);
  const [locating, setLocating] = useState(false);
  const [locationError, setLocationError] = useState(null);

  async function search() {
    const results = await api.nearbyRestaurants(locality);
    setRestaurants(results);
  }

  useEffect(() => {
    search();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function useMyLocation() {
    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported by this browser.");
      return;
    }
    setLocating(true);
    setLocationError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        setLocating(false);
      },
      (err) => {
        setLocationError(
          err.code === err.PERMISSION_DENIED
            ? "Location permission denied. Enable it in your browser to sort by distance."
            : `Could not get location: ${err.message}`
        );
        setLocating(false);
      }
    );
  }

  const displayList = userLocation
    ? [...restaurants]
        .map((r) => ({
          ...r,
          distanceKm: r.latitude != null && r.longitude != null
            ? haversineKm(userLocation.lat, userLocation.lon, r.latitude, r.longitude)
            : null,
        }))
        .sort((a, b) => (a.distanceKm ?? Infinity) - (b.distanceKm ?? Infinity))
    : restaurants;

  return (
    <div>
      <h1>Restaurant Discovery</h1>
      <p className="subtitle">
        <strong>Prototype/mock data</strong> — not sourced from an official inspection database. See{" "}
        <code>app/services/restaurant_seed.py</code>.
      </p>

      <div style={{ display: "flex", gap: 10, marginBottom: 12, maxWidth: 480, flexWrap: "wrap" }}>
        <input
          placeholder="Enter locality, e.g. Baner"
          value={locality}
          onChange={(e) => setLocality(e.target.value)}
          style={{ flex: 1, minWidth: 180, background: "var(--panel2)", border: "1px solid var(--border)", color: "var(--text)", padding: "10px 12px", borderRadius: 9, fontFamily: "inherit", fontSize: 13.5 }}
        />
        <button className="btn" onClick={search}>Search</button>
        <button className="btn btn-secondary" onClick={useMyLocation} disabled={locating} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <IconLocate /> {locating ? "Locating…" : "Use My Location"}
        </button>
      </div>

      {locationError && <div style={{ color: "var(--orange)", fontSize: 13, marginBottom: 16 }}>{locationError}</div>}
      {userLocation && (
        <div className="camera-meta" style={{ marginBottom: 16 }}>
          Sorted by distance from your current location. Note: sample restaurants are all in Pune — distances may be
          large if you're elsewhere.
        </div>
      )}

      <div className="grid">
        {displayList.map((r) => (
          <Link to={`/restaurants/${r.id}`} key={r.id} style={{ color: "inherit" }}>
            <div className="card" style={{ display: "flex", gap: 16, alignItems: "center" }}>
              <ScoreGauge score={r.hygiene_score} size={64} strokeWidth={6} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 700, fontSize: 14.5 }}>{r.name}</div>
                <div className="camera-meta">{r.address} · {r.business_type}</div>
                {r.distanceKm != null && (
                  <div className="camera-meta" style={{ color: "var(--accent)", marginTop: 2 }}>
                    {r.distanceKm.toFixed(1)} km away
                  </div>
                )}
                <div className="camera-meta" style={{ marginTop: 4 }}>View scorecard &rarr;</div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
