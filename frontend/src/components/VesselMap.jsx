import React from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";

export default function VesselMap({ shipping }) {
  const vessels = shipping?.vessels || [];
  const chokepoints = shipping?.chokepoints || {};

  const center = [22, 58]; // roughly centered on the Arabian Sea / Hormuz approach

  return (
    <div className="map-container">
      <MapContainer center={center} zoom={4} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution="&copy; OpenStreetMap &copy; CARTO"
        />
        {Object.entries(chokepoints).map(([name, coord]) => (
          <CircleMarker
            key={name}
            center={[coord.lat, coord.lon]}
            radius={8}
            pathOptions={{ color: "#f5a623", fillColor: "#f5a623", fillOpacity: 0.6 }}
          >
            <Popup>{name.replaceAll("_", " ")}</Popup>
          </CircleMarker>
        ))}
        {vessels.map((v) => (
          <CircleMarker
            key={v.vessel_id}
            center={[v.lat, v.lon]}
            radius={5}
            pathOptions={{ color: "#4cc9f0", fillColor: "#4cc9f0", fillOpacity: 0.8 }}
          >
            <Popup>
              {v.name} ({v.vessel_id})<br />
              Route: {v.route}<br />
              Delay: {v.delay_days} days
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
