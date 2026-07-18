import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// SVG icon helper for custom markers
const createCustomIcon = (color, type) => {
  let svgContent = "";
  if (type === "origin_port") {
    // Oil Rig
    svgContent = `<svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2"><path d="M12 2L2 22h20L12 2zM12 5v13M8 12h8M6 16h12"/></svg>`;
  } else if (type === "destination_port") {
    // Anchor
    svgContent = `<svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2"><path d="M12 5v14M5 12h14M12 19c-3.3 0-6-2.7-6-6M18 13c0 3.3-2.7 6-6 6"/></svg>`;
  } else if (type === "refinery") {
    // Factory
    svgContent = `<svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2"><path d="M2 20h20M17 16v-6l-5 3v-3l-5 3v7h10z"/></svg>`;
  } else if (type === "tanker") {
    // Ship
    svgContent = `<svg class="w-6 h-6 rotate-45" viewBox="0 0 24 24" fill="${color}" stroke="${color}" stroke-width="1"><path d="M2 17l4-10h12l4 10H2zM6 7l6-4 6 4M12 3v4"/></svg>`;
  } else {
    // Alert checkpoint
    svgContent = `<svg class="w-7 h-7 animate-pulse" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2"><path d="M12 9v4M12 17h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>`;
  }

  return L.divIcon({
    html: `<div class="flex items-center justify-center p-1 bg-slate-900 bg-opacity-70 rounded-full border border-slate-700 shadow-lg">${svgContent}</div>`,
    className: "custom-leaflet-icon",
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });
};

export default function DigitalTwinMap({ mapData, recommendedRoutePath }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const routeLayerGroupRef = useRef(null);
  const markerLayerGroupRef = useRef(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Create Leaflet map instance centered near India/Indian Ocean
    const map = L.map(mapContainerRef.current, {
      center: [17.0, 52.0],
      zoom: 4,
      minZoom: 3,
      maxZoom: 9,
    });

    // Dark theme map layer from CartoDB
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: "abcd",
      maxZoom: 20,
    }).addTo(map);

    mapInstanceRef.current = map;
    routeLayerGroupRef.current = L.layerGroup().addTo(map);
    markerLayerGroupRef.current = L.layerGroup().addTo(map);

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update map contents when data changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const routeGroup = routeLayerGroupRef.current;
    const markerGroup = markerLayerGroupRef.current;

    if (!map || !mapData) return;

    // Clear previous layers
    routeGroup.clearLayers();
    markerGroup.clearLayers();

    const { nodes, edges, inland_routes, tankers, blocked_nodes } = mapData;

    // 1. Draw base edges (shipping lanes)
    edges.forEach((edge) => {
      L.polyline([edge.from_coords, edge.to_coords], {
        color: "#334155",
        weight: 1.5,
        dashArray: "4, 6",
        opacity: 0.6,
      }).addTo(routeGroup);
    });

    // 2. Draw inland connections (port-to-refinery)
    inland_routes.forEach((route) => {
      L.polyline([route.port_coords, route.refinery_coords], {
        color: route.pipeline_available ? "#10b981" : "#eab308",
        weight: 2,
        opacity: 0.7,
      }).addTo(routeGroup);
    });

    // 3. Draw nodes
    nodes.forEach((node) => {
      const isBlocked = blocked_nodes.includes(node.name);
      let color = "#38bdf8"; // default cyber-blue

      if (node.type === "refinery") color = "#10b981"; // green
      else if (node.type === "origin_port") color = "#f97316"; // orange
      else if (isBlocked) color = "#ef4444"; // red (blocked)
      else if (node.type === "checkpoint") color = "#a855f7"; // purple

      const icon = createCustomIcon(color, isBlocked ? "checkpoint" : node.type);
      
      let popupContent = `<div class="p-2 min-w-[200px] text-slate-100">
        <h4 class="font-bold text-sm text-brand-400 border-b border-slate-700 pb-1 mb-2">${node.name}</h4>
        <p class="text-xs mb-1"><span class="text-slate-400">Type:</span> ${node.type.toUpperCase()}</p>
        <p class="text-xs mb-1"><span class="text-slate-400">Base Risk Score:</span> ${node.base_risk}/100</p>`;

      // Custom attributes based on type
      if (node.info) {
        Object.entries(node.info).forEach(([key, val]) => {
          const label = key.replace("_", " ").toUpperCase();
          popupContent += `<p class="text-xs mb-1"><span class="text-slate-400">${label}:</span> ${val}</p>`;
        });
      }

      if (isBlocked) {
        popupContent += `<div class="mt-2 text-xs font-bold text-red-400 flex items-center gap-1">
          <svg class="w-4 h-4 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          ACTIVE ROUTE BLOCKAGE
        </div>`;
      }

      popupContent += `</div>`;

      L.marker([node.lat, node.lng], { icon })
        .bindPopup(popupContent)
        .addTo(markerGroup);

      // Draw red highlight circle for blocked nodes
      if (isBlocked) {
        L.circle([node.lat, node.lng], {
          color: "#ef4444",
          fillColor: "#ef4444",
          fillOpacity: 0.15,
          radius: 120000,
        }).addTo(routeGroup);
      }
    });

    // 4. Draw active tankers
    tankers.forEach((tanker) => {
      const icon = createCustomIcon("#38bdf8", "tanker");
      const capacity_m = (tanker.capacity / 1_000_000).toFixed(1);
      
      const popupContent = `<div class="p-2 text-slate-100">
        <h4 class="font-bold text-sm text-brand-400 border-b border-slate-700 pb-1 mb-1">${tanker.name}</h4>
        <p class="text-xs"><span class="text-slate-400">Class:</span> ${tanker.class}</p>
        <p class="text-xs"><span class="text-slate-400">Capacity:</span> ${capacity_m}M barrels</p>
        <p class="text-xs"><span class="text-slate-400">ETA to Destination:</span> ${tanker.eta_days} days</p>
        <p class="text-xs"><span class="text-slate-400">Status:</span> ${tanker.is_available ? "Charter Ready" : "In Transit"}</p>
      </div>`;

      L.marker([tanker.lat, tanker.lng], { icon })
        .bindPopup(popupContent)
        .addTo(markerGroup);
    });

    // 5. Draw currently optimized route overlay
    if (recommendedRoutePath && recommendedRoutePath.length > 0) {
      const coords = [];
      recommendedRoutePath.forEach((nodeName) => {
        const found = nodes.find((n) => n.name === nodeName);
        if (found) coords.push([found.lat, found.lng]);
      });

      if (coords.length > 0) {
        // Glowing shadow line
        L.polyline(coords, {
          color: "#0ea5e9",
          weight: 7,
          opacity: 0.3,
        }).addTo(routeGroup);

        // Core active line
        L.polyline(coords, {
          color: "#38bdf8",
          weight: 4,
          opacity: 0.9,
          dashArray: "1, 10",
          className: "animate-dash", // Custom css class if custom animation needed
        }).addTo(routeGroup);

        // Pan to fit the route path
        map.fitBounds(L.polyline(coords).getBounds(), { padding: [50, 50] });
      }
    }
  }, [mapData, recommendedRoutePath]);

  return (
    <div className="w-full h-full relative overflow-hidden rounded-xl border border-cyber-border">
      <div ref={mapContainerRef} className="w-full h-full" style={{ height: "450px" }} />
      <div className="absolute bottom-4 right-4 z-[1000] glass-panel p-3 rounded-lg text-xs flex flex-col gap-1.5 border border-slate-700">
        <h5 className="font-semibold text-slate-300 border-b border-slate-700 pb-1 mb-1">LEGEND</h5>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 bg-orange-500 rounded-full inline-block border border-orange-400"></span>
          <span>Supplier Origin Port</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 bg-blue-500 rounded-full inline-block border border-blue-400"></span>
          <span>Indian Import Port</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 bg-green-500 rounded-full inline-block border border-green-400"></span>
          <span>Indian Refinery</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 bg-purple-500 rounded-full inline-block border border-purple-400"></span>
          <span>Sea Transit Checkpoint</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300 text-red-400 font-bold">
          <span className="w-3 h-3 bg-red-600 rounded-full inline-block animate-pulse border border-red-500"></span>
          <span>Blocked Risk Zone</span>
        </div>
        <div className="h-px bg-slate-700 my-1"></div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-6 h-0.5 bg-green-500 inline-block"></span>
          <span>Pipeline Connection</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-6 h-0.5 bg-yellow-500 inline-block"></span>
          <span>Rail Freight</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-6 h-0.5 bg-cyan-400 inline-block shadow-[0_0_8px_#22d3ee]"></span>
          <span>Selected Shipping Route</span>
        </div>
      </div>
    </div>
  );
}
