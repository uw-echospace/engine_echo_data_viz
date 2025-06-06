// Global Variables
let allDatasets = {}; // datasetId
let allAcousticData = {};  // datasetId => acousticData
let allTrajectoryGeoJson = {}; // datasetId => geojson
let currentDatasetId = null;
let map = null;
let currentPointIndex = -1;
let currentChannelIndex = 0;
let tooltip = document.getElementById('mapTooltip');
let trajectoryGeoJson = null; // 缓存轨迹数据

const basemapStyles = {
    osm: {
        version: 8,
        sources: {
            'osm-tiles': {
                type: 'raster',
                tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© OpenStreetMap contributors'
            }
        },
        layers: [{
            id: 'osm-tiles',
            type: 'raster',
            source: 'osm-tiles'
        }]
    },
    terrain: {
        version: 8,
        sources: {
            'terrain-tiles': {
                type: 'raster',
                tiles: ['https://a.tile.opentopomap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© OpenTopoMap'
            }
        },
        layers: [{
            id: 'terrain-tiles',
            type: 'raster',
            source: 'terrain-tiles'
        }]
    },
    ocean: {
        version: 8,
        sources: {
            'ocean-tiles': {
                type: 'raster',
                tiles: ['https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}'],
                tileSize: 256,
                attribution: '© Esri Ocean Basemap'
            }
        },
        layers: [{
            id: 'ocean-tiles',
            type: 'raster',
            source: 'ocean-tiles'
        }]
    }
};

function initMap() {
    map = new maplibregl.Map({
        container: 'map',
        style: basemapStyles['osm'],
        center: [-125, 39],
        zoom: 5
    });

    map.addControl(new maplibregl.NavigationControl());

    map.on('load', function () {
        //if (allTrajectoryGeoJson.length > 0) {
        if (Object.keys(allTrajectoryGeoJson).length > 0) {    
            addTrajectoryToMap();
        }
    });
}

document.addEventListener('DOMContentLoaded', async function () {
    initMap();

    try {
        await loadDatasetList();
        await loadAcousticData();
        createDatasetCheckboxes();
        document.getElementById('loading').classList.add('hidden');
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('loading').textContent = 'Error loading data. Please refresh the page.';
    }

    setupEventListeners();
});

async function loadDatasetList() {
    const response = await fetch("/api/datasets")
    allDatasets = await response.json();
}

async function loadAcousticData() {
    for (const datasetId of allDatasets) {
        console.log(`Dataset: ${datasetId}`);
        const response = await fetch(`/api/acoustic-data?datasetId=${datasetId}`);
        if (!response.ok) {
            console.warn(`Failed to load ${datasetId}: ${response.status}`);
            continue;
        }

        const acousticData = await response.json();
        // Handle nulls
        acousticData.latitude = acousticData.latitude.map(val => val ?? -60);
        acousticData.longitude = acousticData.longitude.map(val => val ?? -40);

        allAcousticData[datasetId] = acousticData;

        const points = [];
        const { latitude, longitude, time } = acousticData;
        for (let i = 0; i < latitude.length; i++) {
            points.push({
                lat: latitude[i],
                lng: longitude[i],
                time: new Date(time[i] || '2017-07-24T00:00:00'),
                index: i
            });
        }

        allTrajectoryGeoJson[datasetId] = {
            type: 'FeatureCollection',
            features: [{
                type: 'Feature',
                geometry: {
                    type: 'LineString',
                    coordinates: points.map(p => [p.lng, p.lat])
                },
                properties: { datasetId }
            }]
        };

        addTrajectoryToMap(datasetId, points);  // 🟢 Pass datasetId
    }
}

function addTrajectoryToMap(datasetId, points) {
    if (!map || !points.length || !allTrajectoryGeoJson[datasetId]) return;

    const sourceId = `trajectory-${datasetId}`;
    const layerId = `trajectory-line-${datasetId}`;
    const pointSourceId = `trajectory-points-${datasetId}`;
    const pointLayerId = `trajectory-point-layer-${datasetId}`;

    // Random color for each dataset
    const color = '#' + intToRGB(hashCode(datasetId));

    if (!map.getSource(sourceId)) {
        map.addSource(sourceId, {
            type: 'geojson',
            data: allTrajectoryGeoJson[datasetId]
        });

        map.addLayer({
            id: layerId,
            type: 'line',
            source: sourceId,
            layout: { 'line-join': 'round', 'line-cap': 'round' },
            paint: {
                'line-color': color,
                'line-width': 3,
                'line-opacity': 0.7
            }
        });
    }

    const pointFeatures = points.map(p => ({
        type: 'Feature',
        properties: {
            index: p.index,
            time: p.time.toISOString(),
            datasetId
        },
        geometry: {
            type: 'Point',
            coordinates: [p.lng, p.lat]
        }
    }));

    const pointsGeoJson = {
        type: 'FeatureCollection',
        features: pointFeatures
    };

    if (!map.getSource(pointSourceId)) {
        map.addSource(pointSourceId, { type: 'geojson', data: pointsGeoJson });

        map.addLayer({
            id: pointLayerId,
            type: 'circle',
            source: pointSourceId,
            paint: {
                'circle-radius': 4,
                'circle-color': color,
                'circle-stroke-width': 1,
                'circle-stroke-color': '#ffffff'
            }
        });

        map.on('click', pointLayerId, handlePointClick);
        map.on('mouseenter', pointLayerId, function (e) {
            map.getCanvas().style.cursor = 'pointer';
            const coordinates = e.features[0].geometry.coordinates.slice();
            const time = new Date(e.features[0].properties.time).toLocaleString();
            tooltip.innerHTML = `<strong>Dataset:</strong> ${datasetId}\n<strong>Coordinates:</strong> ${coordinates}\n<strong>Time:</strong> ${time}`;
            tooltip.style.left = e.point.x + 'px';
            tooltip.style.top = e.point.y + 'px';
            tooltip.style.opacity = 1;
        });
        map.on('mouseleave', pointLayerId, function () {
            map.getCanvas().style.cursor = '';
            tooltip.style.opacity = 0;
        });
    }
}

function hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return hash;
}

function intToRGB(i) {
    const c = (i & 0x00FFFFFF)
        .toString(16)
        .toUpperCase();
    return "00000".substring(0, 6 - c.length) + c;
}

function switchBasemapStyle(styleKey) {
    if (!basemapStyles[styleKey]) return;

    const currentCenter = map.getCenter();
    const currentZoom = map.getZoom();

    map.setStyle(basemapStyles[styleKey]);

    const waitForStyleLoad = setInterval(() => {
        if (map.isStyleLoaded()) {
            clearInterval(waitForStyleLoad);
            map.setCenter(currentCenter);
            map.setZoom(currentZoom);
            addTrajectoryToMap();

            const startTime = document.getElementById("startTime").value;
            const endTime = document.getElementById("endTime").value;
            if (startTime && endTime) {
                highlightTrajectoryInRange(startTime, endTime);
            }
            console.log('✅ Style loaded, trajectory redrawn');
        }
    }, 100);
}

function handlePointClick(e) {
    if (e.features.length > 0) {
        const feature = e.features[0];
        const pointIndex = feature.properties.index;
        const coords = feature.geometry.coordinates;
        const timeStr = new Date(feature.properties.time).toLocaleString();

        currentPointIndex = pointIndex;
        currentDatasetId = feature.properties.datasetId;

        document.getElementById('pointInfo').classList.remove('hidden');
        document.getElementById('pointCoords').textContent = `${coords[1].toFixed(4)}, ${coords[0].toFixed(4)}`;
        document.getElementById('pointTime').textContent = timeStr;

        document.getElementById('timeSelector').classList.remove('hidden');

        const pointTime = new Date(feature.properties.time);
        const startTime = new Date(pointTime);
        const endTime = new Date(pointTime);
        startTime.setMinutes(startTime.getMinutes() - 30);
        endTime.setMinutes(endTime.getMinutes() + 30);


        fetchEchogram();
    }
}

function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

async function fetchEchogram(isTimeRange = false) {
    if (currentPointIndex < 0) return;

    const echogramDiv = document.getElementById('echogram');
    echogramDiv.innerHTML = '<div class="loading">Loading echogram...</div>';

    try {
        const channelIndex = parseInt(document.getElementById('channelSelector').value);
        const vmin = document.getElementById('vminSlider').value;
        const vmax = document.getElementById('vmaxSlider').value;

        let url = `/api/echogram?datasetId=${currentDatasetId}&pointIndex=${currentPointIndex}&channelIndex=${channelIndex}&vmin=${vmin}&vmax=${vmax}`;

        if (isTimeRange) {
            const startTime = document.getElementById('startTime').value;
            const endTime = document.getElementById('endTime').value;
            if (startTime && endTime) {
                url += `&startTime=${encodeURIComponent(startTime)}&endTime=${encodeURIComponent(endTime)}`;
            } else {
                alert('Please select both start and end times');
                return;
            }
        }

        const iframe = document.createElement('iframe');
        iframe.src = url;
        iframe.width = '100%';
        iframe.height = '100%';
        iframe.style.border = 'none';
        iframe.onload = function () {
            const loadingEl = echogramDiv.querySelector('.loading');
            if (loadingEl) loadingEl.remove();
        };

        echogramDiv.innerHTML = '';
        echogramDiv.appendChild(iframe);

    } catch (error) {
        console.error('Error fetching echogram:', error);
        echogramDiv.innerHTML = '<p class="error">Failed to load echogram. Please try again.</p>';
    }
}

function generateRangeEchogram() {
    fetchEchogram(true);
}

function setupEventListeners() {
    let debounceTimer;
    const debounceDelay = 300;

    document.getElementById('vminSlider').addEventListener('input', function (e) {
        document.getElementById('vminValue').textContent = e.target.value;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updateEchogram, debounceDelay);
    });

    document.getElementById('vmaxSlider').addEventListener('input', function (e) {
        document.getElementById('vmaxValue').textContent = e.target.value;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updateEchogram, debounceDelay);
    });

    document.getElementById('basemapSelector').addEventListener('change', function (e) {
        const selectedStyle = e.target.value;
        switchBasemapStyle(selectedStyle);
    });

    document.getElementById('channelSelector').addEventListener('change', updateEchogram);
    document.getElementById('generateRangeEchogram').addEventListener('click', generateRangeEchogram);
}

function updateEchogram() {
    if (currentPointIndex >= 0) {
        fetchEchogram();
    }
}

function createDatasetCheckboxes() {
    const container = document.getElementById('datasetCheckbox');
    allDatasets.forEach(datasetId => {
        const checkbox_container = document.createElement("div");
        checkbox_container.className = "checkbox_container";

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `dataset-checkbox-${datasetId}`;
        checkbox.value = datasetId;
        checkbox.checked = true;

        const label = document.createElement('label');
        label.htmlFor = checkbox.id;
        label.textContent = datasetId;
        label.style.marginRight = '10px';

        checkbox.addEventListener('change', () => {
            updateVisibleDatasets(getSelectedDatasetIds());
        });

        checkbox_container.appendChild(checkbox);
        checkbox_container.appendChild(label);
        container.appendChild(checkbox_container);
        container.appendChild(document.createElement('br'));
    });
}