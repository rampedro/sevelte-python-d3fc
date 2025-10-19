<script lang="ts">
	import { onMount } from 'svelte';
	import maplibregl from 'maplibre-gl';
	import { API_BASE_URL } from '$lib/config';

	let mapContainer: HTMLDivElement;
	let map: maplibregl.Map;
	let cities: any[] = [];
	let loading = true;
	let error = '';

	async function fetchCities() {
		try {
			const response = await fetch(`${API_BASE_URL}/api/cities`);
			if (!response.ok) throw new Error('Failed to fetch cities data');
			const data = await response.json();
			cities = data;
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
			loading = false;
		}
	}

	onMount(async () => {
		await fetchCities();

		if (!cities.length && !error) return;

		map = new maplibregl.Map({
			container: mapContainer,
			style: {
				version: 8,
				sources: {
					'raster-tiles': {
						type: 'raster',
						tiles: [
							'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
						],
						tileSize: 256,
						attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
					}
				},
				layers: [
					{
						id: 'simple-tiles',
						type: 'raster',
						source: 'raster-tiles',
						minzoom: 0,
						maxzoom: 22
					}
				]
			},
			center: [0, 20],
			zoom: 1.5
		});

		map.on('load', () => {
			if (cities.length > 0) {
				addCitiesLayer();
			}
		});

		return () => {
			map?.remove();
		};
	});

	function addCitiesLayer() {
		// Add cities data as a source
		map.addSource('cities', {
			type: 'geojson',
			data: {
				type: 'FeatureCollection',
				features: cities.map(city => ({
					type: 'Feature',
					properties: {
						name: city.name,
						population: city.population,
						country: city.country
					},
					geometry: {
						type: 'Point',
						coordinates: [city.longitude, city.latitude]
					}
				}))
			}
		});

		// Add circle layer for cities
		map.addLayer({
			id: 'cities-circle',
			type: 'circle',
			source: 'cities',
			paint: {
				'circle-radius': [
					'interpolate',
					['linear'],
					['get', 'population'],
					1000000, 8,
					20000000, 25
				],
				'circle-color': [
					'interpolate',
					['linear'],
					['get', 'population'],
					1000000, '#3b82f6',
					10000000, '#ef4444',
					20000000, '#dc2626'
				],
				'circle-opacity': 0.7,
				'circle-stroke-width': 2,
				'circle-stroke-color': '#ffffff'
			}
		});

		// Note: Text labels removed to avoid font loading issues
		// City names will be shown in popups instead

		// Add popup on click
		map.on('click', 'cities-circle', (e) => {
			const properties = e.features![0].properties;
			const coordinates = (e.features![0].geometry as any).coordinates.slice();

			// Create popup
			new maplibregl.Popup()
				.setLngLat(coordinates)
				.setHTML(`
					<div style="font-family: sans-serif;">
						<h3 style="margin: 0 0 8px 0; color: #333;">${properties!.name}</h3>
						<p style="margin: 4px 0; color: #666;"><strong>Country:</strong> ${properties!.country}</p>
						<p style="margin: 4px 0; color: #666;"><strong>Population:</strong> ${properties!.population.toLocaleString()}</p>
					</div>
				`)
				.addTo(map);
		});

		// Change cursor on hover
		map.on('mouseenter', 'cities-circle', () => {
			map.getCanvas().style.cursor = 'pointer';
		});

		map.on('mouseleave', 'cities-circle', () => {
			map.getCanvas().style.cursor = '';
		});
	}
</script>

<div class="map-container">
	<h2>World Cities Map</h2>
	<p>Interactive map showing major world cities with population-based sizing</p>
	
	{#if loading}
		<div class="loading">Loading cities data...</div>
	{:else if error}
		<div class="error">
			<p>Error loading data: {error}</p>
			<p>Make sure the Python backend is running on http://localhost:8002</p>
			<button on:click={fetchCities}>Retry</button>
		</div>
	{:else}
		<div class="map-wrapper">
			<div bind:this={mapContainer} class="map"></div>
			<div class="legend">
				<h4>Population</h4>
				<div class="legend-item">
					<div class="legend-circle small"></div>
					<span>&lt; 10M</span>
				</div>
				<div class="legend-item">
					<div class="legend-circle medium"></div>
					<span>10M - 15M</span>
				</div>
				<div class="legend-item">
					<div class="legend-circle large"></div>
					<span>&gt; 15M</span>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.map-container {
		width: 100%;
	}

	.map-container h2 {
		margin: 0 0 8px 0;
		color: #333;
	}

	.map-container p {
		margin: 0 0 20px 0;
		color: #666;
	}

	.loading, .error {
		text-align: center;
		padding: 40px;
		color: #666;
	}

	.error {
		color: #ef4444;
	}

	.error button {
		margin-top: 10px;
		padding: 8px 16px;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}

	.map-wrapper {
		position: relative;
		height: 500px;
		border-radius: 8px;
		overflow: hidden;
		box-shadow: 0 4px 12px rgba(0,0,0,0.15);
	}

	.map {
		width: 100%;
		height: 100%;
	}

	.legend {
		position: absolute;
		top: 10px;
		right: 10px;
		background: rgba(255, 255, 255, 0.9);
		padding: 10px;
		border-radius: 6px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
		min-width: 100px;
	}

	.legend h4 {
		margin: 0 0 8px 0;
		font-size: 14px;
		color: #333;
	}

	.legend-item {
		display: flex;
		align-items: center;
		margin: 4px 0;
		font-size: 12px;
		color: #666;
	}

	.legend-circle {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		margin-right: 8px;
		border: 1px solid #ffffff;
	}

	.legend-circle.small {
		background: #3b82f6;
		width: 8px;
		height: 8px;
	}

	.legend-circle.medium {
		background: #ef4444;
		width: 12px;
		height: 12px;
	}

	.legend-circle.large {
		background: #dc2626;
		width: 16px;
		height: 16px;
	}
</style>