async function req(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  // camera / pairing
  createCameraSession: (name) => req("/api/camera/session", { method: "POST", body: JSON.stringify({ name }) }),
  getCameraSessionStatus: (id) => req(`/api/camera/session/${id}/status`),

  // barcode
  scanBarcode: (barcode) => req("/api/barcode/scan", { method: "POST", body: JSON.stringify({ barcode }) }),

  // products
  listProducts: () => req("/api/products"),
  getProduct: (id) => req(`/api/products/${id}`),
  createProduct: (data) => req("/api/products", { method: "POST", body: JSON.stringify(data) }),
  updateProduct: (id, data) => req(`/api/products/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  // ocr
  processOcr: (data) => req("/api/ocr/process", { method: "POST", body: JSON.stringify(data) }),
  confirmOcr: (data) => req("/api/ocr/confirm", { method: "POST", body: JSON.stringify(data) }),

  // hygiene
  getHygieneCategories: () => req("/api/hygiene/categories"),
  getScorecard: (restaurantId) => req(`/api/hygiene/scorecard/${restaurantId}`),
  listHygieneAssessments: (restaurantId) =>
    req(`/api/hygiene/assessments${restaurantId ? `?restaurant_id=${restaurantId}` : ""}`),

  // restaurants
  nearbyRestaurants: (locality) => req(`/api/restaurants/nearby${locality ? `?locality=${encodeURIComponent(locality)}` : ""}`),

  // sensors
  latestSensorReading: (zone) => req(`/api/sensors/latest${zone ? `?zone=${encodeURIComponent(zone)}` : ""}`),

  // events
  listEvents: () => req("/api/events"),
  createEvent: (data) => req("/api/events", { method: "POST", body: JSON.stringify(data) }),
  verifyEvent: (id, confirmed) => req(`/api/events/${id}/verify`, { method: "POST", body: JSON.stringify({ confirmed }) }),
};
