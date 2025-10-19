<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3-selection';
	import * as d3Scale from 'd3-scale';
	import { extent, max } from 'd3-array';
	import { format } from 'd3-format';
	import { axisBottom, axisLeft } from 'd3-axis';
	import { line, curveMonotoneX } from 'd3-shape';
	import * as fc from 'd3fc';
	import { API_BASE_URL } from '$lib/config';

	let chartContainer: HTMLDivElement;
	let populationData: any[] = [];
	let loading = true;
	let error = '';

	async function fetchPopulationData() {
		try {
			const response = await fetch(`${API_BASE_URL}/api/population`);
			if (!response.ok) throw new Error('Failed to fetch population data');
			const data = await response.json();
			populationData = data;
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
			loading = false;
		}
	}

	onMount(async () => {
		await fetchPopulationData();
		if (populationData.length > 0) {
			createPopulationCharts();
		}
	});

	function createPopulationCharts() {
		// Clear previous chart
		d3.select(chartContainer).selectAll('*').remove();

		createPopulationTrendChart();
		createGDPComparisonChart();
	}

	function createPopulationTrendChart() {
		const processedData = populationData.map(d => ({
			country: d.country,
			year: parseInt(d.year),
			population: parseInt(d.population),
			gdp_per_capita: parseFloat(d.gdp_per_capita)
		}));

		// Group by country
		const countries = ['USA', 'China', 'India', 'Germany', 'Japan'];
		const groupedData = countries.map(country => ({
			country,
			data: processedData.filter(d => d.country === country).sort((a, b) => a.year - b.year),
			color: getCountryColor(country)
		}));

		const width = 700;
		const height = 350;
		const margin = { top: 20, right: 120, bottom: 40, left: 80 };

		// Add title
		d3.select(chartContainer)
			.append('h3')
			.text('Population Trends by Country')
			.style('margin', '0 0 10px 0')
			.style('color', '#333');

		// Create SVG
		const svg = d3.select(chartContainer)
			.append('div')
			.style('margin-bottom', '30px')
			.append('svg')
			.attr('width', width)
			.attr('height', height)
			.style('background', '#f9f9f9')
			.style('border-radius', '4px')
			.style('border', '1px solid #e5e7eb');

		// Create scales
		const xScale = d3Scale.scaleLinear()
			.domain(extent(processedData, d => d.year) as [number, number])
			.range([margin.left, width - margin.right]);

		const yScale = d3Scale.scaleLinear()
			.domain([0, max(processedData, d => d.population) as number])
			.nice()
			.range([height - margin.bottom, margin.top]);

		// Create line generator
		const lineGenerator = line<any>()
			.x(d => xScale(d.year))
			.y(d => yScale(d.population))
			.curve(curveMonotoneX);

		// Create lines and points for each country
		groupedData.forEach(group => {
			// Add line
			svg.append('path')
				.datum(group.data)
				.attr('fill', 'none')
				.attr('stroke', group.color)
				.attr('stroke-width', 3)
				.attr('d', lineGenerator);

			// Add points
			svg.selectAll(`.points-${group.country.replace(/\s+/g, '-')}`)
				.data(group.data)
				.enter()
				.append('circle')
				.attr('class', `points-${group.country.replace(/\s+/g, '-')}`)
				.attr('cx', d => xScale(d.year))
				.attr('cy', d => yScale(d.population))
				.attr('r', 4)
				.attr('fill', group.color)
				.attr('stroke', '#fff')
				.attr('stroke-width', 2);
		});

		// Add axes
		const xAxis = axisBottom(xScale)
			.tickFormat(format('d') as any);
		
		const yAxis = axisLeft(yScale)
			.tickFormat(format('.2s') as any);

		svg.append('g')
			.attr('transform', `translate(0, ${height - margin.bottom})`)
			.call(xAxis)
			.style('font-size', '12px');

		svg.append('g')
			.attr('transform', `translate(${margin.left}, 0)`)
			.call(yAxis)
			.style('font-size', '12px');

		// Add axis labels
		svg.append('text')
			.attr('x', width / 2)
			.attr('y', height - 5)
			.attr('text-anchor', 'middle')
			.style('font-size', '14px')
			.style('fill', '#666')
			.text('Year');

		svg.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 15)
			.attr('x', -height / 2)
			.attr('text-anchor', 'middle')
			.style('font-size', '14px')
			.style('fill', '#666')
			.text('Population');

		// Add legend
		const legend = svg.append('g')
			.attr('transform', `translate(${width - margin.right + 10}, ${margin.top})`);

		groupedData.forEach((group, i) => {
			const legendItem = legend.append('g')
				.attr('transform', `translate(0, ${i * 25})`);

			legendItem.append('circle')
				.attr('cx', 10)
				.attr('cy', 0)
				.attr('r', 6)
				.style('fill', group.color)
				.style('stroke', '#fff')
				.style('stroke-width', '2px');

			legendItem.append('text')
				.attr('x', 25)
				.attr('y', 4)
				.text(group.country)
				.style('font-size', '12px')
				.style('fill', '#333');
		});
	}

	function createGDPComparisonChart() {
		// Get 2023 data for comparison
		const data2023 = populationData
			.filter(d => d.year === '2023')
			.map(d => ({
				country: d.country,
				gdp_per_capita: parseFloat(d.gdp_per_capita),
				population: parseInt(d.population)
			}))
			.sort((a, b) => b.gdp_per_capita - a.gdp_per_capita);

		const width = 700;
		const height = 300;
		const margin = { top: 20, right: 60, bottom: 80, left: 80 };

		// Add title
		d3.select(chartContainer)
			.append('h3')
			.text('GDP per Capita Comparison (2023)')
			.style('margin', '20px 0 10px 0')
			.style('color', '#333');

		// Create SVG
		const svg = d3.select(chartContainer)
			.append('svg')
			.attr('width', width)
			.attr('height', height)
			.style('background', '#f9f9f9')
			.style('border-radius', '4px')
			.style('border', '1px solid #e5e7eb');

		// Create scales
		const xScale = d3Scale.scaleBand()
			.domain(data2023.map(d => d.country))
			.range([margin.left, width - margin.right])
			.padding(0.2);

		const yScale = d3Scale.scaleLinear()
			.domain([0, max(data2023, d => d.gdp_per_capita) as number])
			.nice()
			.range([height - margin.bottom, margin.top]);

		// Create bars
		data2023.forEach(d => {
			const barHeight = height - margin.bottom - yScale(d.gdp_per_capita);
			
			svg.append('rect')
				.attr('x', xScale(d.country)!)
				.attr('y', yScale(d.gdp_per_capita))
				.attr('width', xScale.bandwidth())
				.attr('height', barHeight)
				.style('fill', getCountryColor(d.country))
				.style('opacity', 0.8)
				.style('rx', '3px');

			// Add value labels on bars
			svg.append('text')
				.attr('x', xScale(d.country)! + xScale.bandwidth() / 2)
				.attr('y', yScale(d.gdp_per_capita) - 5)
				.attr('text-anchor', 'middle')
				.text(`$${format(',.0f')(d.gdp_per_capita)}`)
				.style('font-size', '11px')
				.style('fill', '#333')
				.style('font-weight', 'bold');
		});

		// Add axes
		const xAxis = axisBottom(xScale);
		const yAxis = axisLeft(yScale)
			.tickFormat(format('$,.0f') as any);

		svg.append('g')
			.attr('transform', `translate(0, ${height - margin.bottom})`)
			.call(xAxis)
			.style('font-size', '12px')
			.selectAll('text')
			.attr('transform', 'rotate(-45)')
			.style('text-anchor', 'end');

		svg.append('g')
			.attr('transform', `translate(${margin.left}, 0)`)
			.call(yAxis)
			.style('font-size', '12px');

		// Add axis labels
		svg.append('text')
			.attr('x', width / 2)
			.attr('y', height - 5)
			.attr('text-anchor', 'middle')
			.style('font-size', '14px')
			.style('fill', '#666')
			.text('Country');

		svg.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 15)
			.attr('x', -height / 2)
			.attr('text-anchor', 'middle')
			.style('font-size', '14px')
			.style('fill', '#666')
			.text('GDP per Capita ($)');
	}

	function getCountryColor(country: string): string {
		const colors = {
			'USA': '#3b82f6',
			'China': '#ef4444',
			'India': '#f59e0b',
			'Germany': '#10b981',
			'Japan': '#8b5cf6'
		};
		return colors[country as keyof typeof colors] || '#6b7280';
	}
</script>

<div class="population-container">
	<h2>Population & Economic Analysis</h2>
	<p>Demographic and economic indicators visualization using D3FC</p>

	{#if loading}
		<div class="loading">Loading population data...</div>
	{:else if error}
		<div class="error">
			<p>Error loading data: {error}</p>
			<p>Make sure the Python backend is running on http://localhost:8002</p>
			<button on:click={fetchPopulationData}>Retry</button>
		</div>
	{:else}
		<div bind:this={chartContainer} class="charts-container"></div>
	{/if}
</div>

<style>
	.population-container {
		width: 100%;
	}

	.population-container h2 {
		margin: 0 0 8px 0;
		color: #333;
	}

	.population-container p {
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
		gap: 0;
	}
</style>