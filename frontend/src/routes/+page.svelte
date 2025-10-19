<script lang="ts">
	import MapExample from '../lib/components/MapExample.svelte';
	import SalesChart from '../lib/components/SalesChart.svelte';
	import StockChart from '../lib/components/StockChart.svelte';
	import PopulationChart from '../lib/components/PopulationChart.svelte';

	let activeTab = 'map';
</script>

<svelte:head>
	<title>Svelte + Python + D3FC + MapLibre GL</title>
	<link href="https://unpkg.com/maplibre-gl@latest/dist/maplibre-gl.css" rel="stylesheet" />
</svelte:head>

<main>
	<header>
		<h1>Data Visualization Dashboard</h1>
		<p>Python Backend + Svelte Frontend + MapLibre GL + D3FC + DeckGL</p>
	</header>

	<nav>
		<button class:active={activeTab === 'map'} on:click={() => activeTab = 'map'}>
			MapLibre GL
		</button>
		<button class:active={activeTab === 'sales'} on:click={() => activeTab = 'sales'}>
			Sales Charts
		</button>
		<button class:active={activeTab === 'stocks'} on:click={() => activeTab = 'stocks'}>
			DeckGL Overlay
		</button>
		<button class:active={activeTab === 'population'} on:click={() => activeTab = 'population'}>
			Population Data
		</button>
	</nav>

	<div class="content">
		{#if activeTab === 'map'}
			<MapExample />
		{:else if activeTab === 'sales'}
			<SalesChart />
		{:else if activeTab === 'stocks'}
			<StockChart />
		{:else if activeTab === 'population'}
			<PopulationChart />
		{/if}
	</div>
</main>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
		background-color: #f5f5f5;
	}

	main {
		max-width: 1200px;
		margin: 0 auto;
		padding: 20px;
	}

	header {
		text-align: center;
		margin-bottom: 30px;
	}

	header h1 {
		color: #333;
		margin-bottom: 10px;
	}

	header p {
		color: #666;
		font-size: 16px;
	}

	nav {
		display: flex;
		justify-content: center;
		gap: 10px;
		margin-bottom: 30px;
		flex-wrap: wrap;
	}

	nav button {
		padding: 12px 24px;
		border: 2px solid #ddd;
		background: white;
		color: #333;
		border-radius: 6px;
		cursor: pointer;
		font-size: 14px;
		font-weight: 500;
		transition: all 0.2s ease;
	}

	nav button:hover {
		border-color: #007acc;
		color: #007acc;
	}

	nav button.active {
		background: #007acc;
		border-color: #007acc;
		color: white;
	}

	.content {
		background: white;
		border-radius: 8px;
		padding: 20px;
		box-shadow: 0 2px 10px rgba(0,0,0,0.1);
		min-height: 500px;
	}
</style>
