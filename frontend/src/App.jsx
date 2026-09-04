import React from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import LiveMonitoring from "./pages/LiveMonitoring.jsx";
import PhoneCamera from "./pages/PhoneCamera.jsx";
import ProductScanner from "./pages/ProductScanner.jsx";
import Products from "./pages/Products.jsx";
import Hygiene from "./pages/Hygiene.jsx";
import Restaurants from "./pages/Restaurants.jsx";
import RestaurantScorecard from "./pages/RestaurantScorecard.jsx";
import Events from "./pages/Events.jsx";
import { IconDashboard, IconCamera, IconScan, IconBox, IconShield, IconMapPin, IconBell } from "./components/icons.jsx";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", end: true, icon: IconDashboard },
  { to: "/live", label: "Live Monitoring", icon: IconCamera },
  { to: "/scanner", label: "Product Scanner", icon: IconScan },
  { to: "/products", label: "Products", icon: IconBox },
  { to: "/hygiene", label: "Hygiene", icon: IconShield },
  { to: "/restaurants", label: "Restaurants", icon: IconMapPin },
  { to: "/events", label: "Events & Evidence", icon: IconBell },
];

function Layout({ children }) {
  return (
    <div className="app-shell">
      <div className="sidebar">
        <div className="brand">SAFE<span>PLATE</span></div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              <Icon />
              {item.label}
            </NavLink>
          );
        })}
      </div>
      <div className="main">{children}</div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      {/* Phone-facing page: no desktop chrome, opened directly from the QR code */}
      <Route path="/phone/camera/:sessionId" element={<PhoneCamera />} />

      <Route path="/*" element={
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/live" element={<LiveMonitoring />} />
            <Route path="/scanner" element={<ProductScanner />} />
            <Route path="/products" element={<Products />} />
            <Route path="/hygiene" element={<Hygiene />} />
            <Route path="/restaurants" element={<Restaurants />} />
            <Route path="/restaurants/:id" element={<RestaurantScorecard />} />
            <Route path="/events" element={<Events />} />
          </Routes>
        </Layout>
      } />
    </Routes>
  );
}
