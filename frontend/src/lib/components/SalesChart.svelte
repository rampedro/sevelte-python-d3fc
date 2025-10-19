<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3-selection';
	import * as d3Scale from 'd3-scale';
	import { extent, max } from 'd3-array';
	import { timeFormat } from 'd3-time-format';
	import { format } from 'd3-format';
	import { axisBottom, axisLeft } from 'd3-axis';
	import * as fc from 'd3fc';
	import { API_BASE_URL } from '$lib/config';

	let chartContainer: HTMLDivElement;
	let salesData: any[] = [];
	let loading = true;
	let error = '';

	async function fetchSalesData() {
		try {
			const response = await fetch(`${API_BASE_URL}/api/sales`);
			if (!response.ok) throw new Error('Failed to fetch sales data');
			const data = await response.json();
			salesData = data;
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
			loading = false;
		}
	}

	onMount(async () => {
		await fetchSalesData();
		if (salesData.length > 0) {
			createBarChart();
		}
	});

	function createBarChart() {
		if (!salesData.length || !chartContainer) return;

		// Clear previous chart
		d3.select(chartContainer).selectAll('*').remove();

		const containerRect = chartContainer.getBoundingClientRect();
		const margin = { top: 20, right: 30, bottom: 60, left: 70 };
		const width = Math.max(containerRect.width, 600) - margin.left - margin.right;
		const height = 400 - margin.top - margin.bottom;

		// Process data
		const data = salesData.map(d => ({
			...d,
			month: new Date(d.month + '-01'),
			sales: +d.sales
		}));

		// Set up scales
		const xScale = d3Scale.scaleBand()
			.domain(data.map(d => d.month.toISOString()))
			.range([0, width])
			.padding(0.1);

		const yScale = d3Scale.scaleLinear()
			.domain([0, max(data, d => d.sales) || 0])
			.nice()
			.range([height, 0]);

		// Create SVG
		const svg = d3.select(chartContainer)
			.append('svg')
			.attr('width', width + margin.left + margin.right)
			.attr('height', height + margin.top + margin.bottom);

		const g = svg.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Create bars
		g.selectAll('.bar')
			.data(data)
			.enter()
			.append('rect')
			.attr('class', 'bar')
			.attr('x', d => xScale(d.month.toISOString()) || 0)
			.attr('width', xScale.bandwidth())
			.attr('y', d => yScale(d.sales))
			.attr('height', d => height - yScale(d.sales))
			.attr('fill', d => getProductColor(d.product))
			.attr('opacity', 0.8)
			.on('mouseover', function(event, d) {
				d3.select(this).attr('opacity', 1);
			})
			.on('mouseout', function(event, d) {
				d3.select(this).attr('opacity', 0.8);
			});

		// Add axes
		g.append('g')
			.attr('transform', `translate(0,${height})`)
			.call(axisBottom(xScale)
				.tickFormat(d => timeFormat('%b %Y')(new Date(d as string))));

		g.append('g')
			.call(axisLeft(yScale)
				.tickFormat(format('.0s')));

		// Add axis labels
		g.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 0 - margin.left)
			.attr('x', 0 - (height / 2))
			.attr('dy', '1em')
			.style('text-anchor', 'middle')
			.style('font-size', '12px')
			.text('Sales ($)');

		g.append('text')
			.attr('transform', `translate(${width / 2}, ${height + margin.bottom - 5})`)
			.style('text-anchor', 'middle')
			.style('font-size', '12px')
			.text('Month');
	}	function getProductColor(product: string): string {
		const colors = {
			'Laptops': '#3b82f6',
			'Phones': '#ef4444',
			'Tablets': '#10b981'
		};
		return colors[product as keyof typeof colors] || '#6b7280';
	}
</script>

<div class="sales-container">
	<h2>Sales Performance Charts</h2>
	<p>Monthly sales data visualized using D3FC bar charts</p>

	{#if loading}
		<div class="loading">Loading sales data...</div>
	{:else if error}
		<div class="error">
			<p>Error loading data: {error}</p>
			<p>Make sure the Python backend is running on http://localhost:8002</p>
			<button on:click={fetchSalesData}>Retry</button>
		</div>
	{:else}
		<div bind:this={chartContainer} class="charts-container"></div>
	{/if}
</div>

<style>
	.sales-container {
		width: 100%;
	}

	.sales-container h2 {
		margin: 0 0 8px 0;
		color: #333;
	}

	.sales-container p {
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

	.charts-container {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	:global(.charts-container svg) {
		border: 1px solid #e5e7eb;
		border-radius: 6px;
	}

	:global(.charts-container .x-axis) {
		font-size: 12px;
	}

	:global(.charts-container .y-axis) {
		font-size: 12px;
	}
</style>