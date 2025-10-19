<script lang="ts">
	import { onMount } from 'svelte';
	import { MapLibre, FillExtrusionLayer } from 'svelte-maplibre-gl';
	import { DeckGLOverlay } from '@svelte-maplibre-gl/deckgl';
	import { ArcLayer } from '@deck.gl/layers';

	const NUM = 30;
	let data: { source: [number, number]; target: [number, number] }[] = [];

	onMount(() => {
		let handle = requestAnimationFrame(function updateFrame(t) {
			data = Array.from({ length: NUM }, (_, i) => {
				const O = (2 * Math.PI) / NUM;
				const r = (1.3 + Math.sin(t / 510 + i * O)) * 0.002;
				return {
					source: [139.7672, 35.6812],
					target: [139.7672 + Math.cos(t / 730 + i * O) * r, 35.6812 + Math.sin(t / 730 + i * O) * r]
				};
			});
			handle = requestAnimationFrame(updateFrame);
		});
		return () => cancelAnimationFrame(handle);
	});
</script>

<div class="deckgl-container">
	<h2 class="deckgl-title">🌏 DeckGL Overlay - Tokyo Animation</h2>
	<p class="deckgl-description">
		Interactive 3D visualization showing animated arc layers over Tokyo with 3D buildings.
		Based on the DeckGL overlay example from svelte-maplibre-gl.
	</p>
	
	<MapLibre
		class="deckgl-map"
		style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
		zoom={15}
		pitch={60}
		minZoom={4}
		bearing={-45}
		center={[139.7672, 35.6812]}
	>
		<DeckGLOverlay
			interleaved
			layers={[
				new ArcLayer({
					id: 'deckgl-arc',
					data,
					getSourcePosition: (d) => d.source,
					getTargetPosition: (d) => d.target,
					getSourceColor: [0, 255, 100],
					getTargetColor: [0, 190, 255],
					getWidth: 5
				})
			]}
		/>
		<FillExtrusionLayer
			source="carto"
			sourceLayer="building"
			minzoom={14}
			paint={{
				'fill-extrusion-color': '#aaa',
				'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 14, 0, 14.05, ['get', 'render_height']],
				'fill-extrusion-base': ['interpolate', ['linear'], ['zoom'], 14, 0, 14.05, ['get', 'render_min_height']],
				'fill-extrusion-opacity': 0.8
			}}
		/>
	</MapLibre>
	
	<div class="deckgl-info">
		<h3>🎯 Features</h3>
		<ul class="deckgl-features">
			<li>✨ Animated arc layers radiating from Tokyo center</li>
			<li>🏗️ 3D building extrusions with realistic heights</li>
			<li>🎨 Smooth color transitions and animations</li>
			<li>📐 60° pitch for enhanced 3D perspective</li>
			<li>🔄 Real-time animation using requestAnimationFrame</li>
		</ul>
	</div>
</div>

<style>
	.deckgl-container {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		padding: 24px;
		border-radius: 16px;
		box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
		backdrop-filter: blur(4px);
		border: 1px solid rgba(255, 255, 255, 0.18);
		margin: 16px 0;
	}

	.deckgl-title {
		font-size: 1.8rem;
		font-weight: 700;
		color: white;
		margin-bottom: 8px;
		text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
	}

	.deckgl-description {
		color: rgba(255, 255, 255, 0.9);
		margin-bottom: 20px;
		line-height: 1.6;
		font-size: 1rem;
	}

	:global(.deckgl-map) {
		height: 400px;
		min-height: 300px;
		border-radius: 12px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
		border: 2px solid rgba(255, 255, 255, 0.1);
		overflow: hidden;
	}

	.deckgl-info {
		margin-top: 20px;
		background: rgba(255, 255, 255, 0.1);
		padding: 16px;
		border-radius: 12px;
		backdrop-filter: blur(8px);
	}

	.deckgl-info h3 {
		color: white;
		font-size: 1.2rem;
		font-weight: 600;
		margin-bottom: 12px;
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
	}

	.deckgl-features {
		list-style: none;
		padding: 0;
		color: rgba(255, 255, 255, 0.9);
	}

	.deckgl-features li {
		padding: 6px 0;
		font-size: 0.95rem;
		line-height: 1.4;
	}

	.deckgl-features li::before {
		content: '';
		display: inline-block;
		width: 4px;
		height: 4px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.6);
		margin-right: 8px;
		vertical-align: middle;
	}

	@media (max-width: 768px) {
		.deckgl-container {
			padding: 16px;
			margin: 8px 0;
		}

		.deckgl-title {
			font-size: 1.5rem;
		}

		:global(.deckgl-map) {
			height: 300px;
		}

		.deckgl-info {
			padding: 12px;
		}
	}
</style>