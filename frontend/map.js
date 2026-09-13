// Map Module - Leaflet.js Integration

class EmergencyMap {
    constructor() {
        this.map = null;
        this.markers = [];
        this.hospitalMarkers = [];
        this.emergencyMarker = null;
        this.defaultCoordinates = [17.3850, 78.4867]; // Hyderabad
        this.defaultZoom = 13;
    }

    initialize() {
        const mapContainer = document.getElementById('map');
        if (!mapContainer) {
            console.error('Map container not found');
            return false;
        }

        try {
            this.map = L.map('map').setView(this.defaultCoordinates, this.defaultZoom);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19
            }).addTo(this.map);

            console.log('Map initialized successfully');
            return true;
        } catch (error) {
            console.error('Error initializing map:', error);
            return false;
        }
    }

    setView(coordinates, zoom) {
        if (this.map) {
            this.map.setView(coordinates, zoom);
        }
    }

    invalidateSize() {
        if (this.map) {
            setTimeout(() => {
                this.map.invalidateSize({ animate: false });
                this.fitAllMarkers();
            }, 120);
        }
    }

    addEmergencyMarker(coordinates, popupContent) {
        if (!this.map) return;

        this.clearEmergencyMarker();

        const emergencyIcon = L.divIcon({
            className: '',
            html: '<div class="emergency-marker"><i class="fas fa-plus"></i></div>',
            iconSize: [34, 34],
            iconAnchor: [17, 17]
        });

        this.emergencyMarker = L.marker(coordinates, { icon: emergencyIcon });

        if (popupContent) {
            this.emergencyMarker.bindPopup(popupContent);
        }

        this.emergencyMarker.addTo(this.map);
    }

    addHospitalMarkers(hospitals, baseCoordinates) {
        if (!this.map) return;

        this.clearHospitalMarkers();

        const hospitalIcon = L.divIcon({
            className: '',
            html: '<div class="hospital-marker"><i class="fas fa-hospital"></i></div>',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        hospitals.forEach((hospital, index) => {
            let lat, lon, name, address;

            // Handle both structured objects and plain strings
            if (hospital && typeof hospital === 'object') {
                lat = hospital.latitude;
                lon = hospital.longitude;
                name = hospital.name || `Hospital ${index + 1}`;
                address = hospital.address || '';
            } else if (baseCoordinates) {
                // Fallback: jitter around base (legacy string hospitals)
                lat = baseCoordinates[0] + (Math.random() - 0.5) * 0.015;
                lon = baseCoordinates[1] + (Math.random() - 0.5) * 0.015;
                name = `Hospital ${index + 1}`;
                address = String(hospital);
            } else {
                lat = this.defaultCoordinates[0] + (Math.random() - 0.5) * 0.015;
                lon = this.defaultCoordinates[1] + (Math.random() - 0.5) * 0.015;
                name = `Hospital ${index + 1}`;
                address = String(hospital);
            }

            // Skip if coordinates are missing or obviously wrong
            if (lat == null || lon == null || isNaN(lat) || isNaN(lon)) return;

            const marker = L.marker([lat, lon], { icon: hospitalIcon });

            const popupContent = `
                <div class="map-popup">
                    <h4>${this.escapeHtml(name)}</h4>
                    <p>${this.escapeHtml(address)}</p>
                    <a href="https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}"
                       target="_blank" rel="noopener" class="map-popup-link">
                        <i class="fas fa-directions"></i> Get Directions
                    </a>
                </div>
            `;

            marker.bindPopup(popupContent, { maxWidth: 260 });
            marker.bindTooltip(name, { direction: 'top', offset: [0, -14] });
            marker.addTo(this.map);
            this.hospitalMarkers.push(marker);
        });

        // Fit map to show emergency marker + all hospital markers
        this.fitAllMarkers();
    }

    fitAllMarkers() {
        const allMarkers = [...this.hospitalMarkers];
        if (this.emergencyMarker) {
            allMarkers.push(this.emergencyMarker);
        }
        if (allMarkers.length > 0) {
            const group = L.featureGroup(allMarkers);
            this.map.fitBounds(group.getBounds().pad(0.15));
        }
    }

    clearHospitalMarkers() {
        this.hospitalMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.hospitalMarkers = [];
    }

    clearEmergencyMarker() {
        if (this.emergencyMarker && this.map) {
            this.map.removeLayer(this.emergencyMarker);
            this.emergencyMarker = null;
        }
    }

    clearAllMarkers() {
        this.clearHospitalMarkers();
        this.clearEmergencyMarker();
    }

    resize() {
        this.invalidateSize();
    }

    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
        this.clearAllMarkers();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Map singleton
let emergencyMap;

document.addEventListener('DOMContentLoaded', () => {
    emergencyMap = new EmergencyMap();

    // Deferred init — the map container lives inside the hidden #resultsSection,
    // so Leaflet needs it visible (or at least in DOM) to measure container size.
    // We initialize once at load so tiles/preload, then invalidateSize after the
    // container becomes visible via showResults().
    setTimeout(() => emergencyMap.initialize(), 100);

    window.addEventListener('resize', () => emergencyMap.resize());
});

// Called by app.js after WebSocket/REST results are ready
function updateMapWithEmergencyData(location, coordinates, hospitals) {
    if (!emergencyMap || !emergencyMap.map) {
        console.warn('Map not initialized');
        return;
    }

    // Ensure Leaflet recalculates size (may have been hidden until now)
    emergencyMap.invalidateSize();

    if (coordinates) {
        emergencyMap.addEmergencyMarker(
            coordinates,
            `<div class="map-popup emergency-popup"><h4>Emergency Location</h4><p>${location}</p></div>`
        );
    }

    if (hospitals && hospitals.length > 0) {
        emergencyMap.addHospitalMarkers(hospitals, coordinates);
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EmergencyMap, updateMapWithEmergencyData };
}