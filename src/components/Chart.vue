<template>
	<div>
		<canvas :id="id" />
	</div>
</template>
<script>
import Chart from 'chart.js'
import zoom from 'chartjs-plugin-zoom'

export default {
	name: 'Chart',

	props: {
		id: {
			type: String,
			required: true,
		},

		title: {
			type: String,
			default: ''
		},

		datasets: {
			type: Array,
			required: true,
		},
	},

	watch: {
		datasets: {
			handler() {
				this.update()
			},
			deep: true,
		},
	},


	data() {
		return {
			datasets_length: 0,
			ch: null,

			mounted: false,
		}
	},

	mounted() {
		if (this.datasets.length == 0) {
			return;
		}

		this.init()

		this.mounted = true
	},
	methods: {
		init() {
			// Get data
			let type = this.datasets[0]['type']
			let label = this.datasets[0]['label']
			let labels = [...this.datasets[0]['labels']]
			let data = [...this.datasets[0]['data']]
			let color = String(this.datasets[0]['color'][0]) + ', ' +
				String(this.datasets[0]['color'][1]) + ', ' +
				String(this.datasets[0]['color'][2])

			// Save data length
			this.datasets_length = this.datasets.length

			// Register ZOOM plugin
			Chart.plugins.register({
				zoom
			})

			// Create chart
			const ctx = document.getElementById(this.id)
			this.ch = new Chart(ctx, {
				type: type,
				data: {
					labels: labels,
					datasets: [{
						label: label,
						data: data,
						backgroundColor: 'rgba(' + color + ', .1)',
						borderColor: 'rgba(' + color + ', 1)',
						borderWidth: 1,
						pointRadius: 0 // disable for a single dataset
					}]
				},
				options: {
					elements: {
						line: {
							tension: 0 // disables bezier curves
						}
					},
					normalized: true,
					aspectRatio: 1.5,
					animation: false,
					title: {
						display: true,
						text: this.title
					},
					scales: {
						y: {
							beginAtZero: true
						}
					},
					plugins: {
						zoom: {
							pan: {
								enabled: true,
								mode: 'xy',
							},

							zoom: {
								enabled: true,
								mode: 'xy',
							}
						}
					}
				},
			})
		},

		append() {
			if (this.mounted == false) {
				this.init()
				this.mounted = true

				return
			}

			// Get index
			let idx = this.datasets.length - 1

			// Get data
			let label = this.datasets[idx]['label']
			let data = [...this.datasets[idx]['data']]
			let color = String(this.datasets[idx]['color'][0]) + ', ' +
				String(this.datasets[idx]['color'][1]) + ', ' +
				String(this.datasets[idx]['color'][2])

			// Set new length
			this.datasets_length = this.datasets.length

			// Add data to dataset
			this.ch.data.datasets.push({
				label: label,
				data: data,
				backgroundColor: 'rgba(' + color + ', .2)',
				borderColor: 'rgba(' + color + ', 1)',
				borderWidth: 1,
				pointRadius: 0 // disable for a single dataset
			})

			// Invoke update
			this.ch.update()
		},

		remove() {
			// Determine removed index
			let idx = this.ch.data.datasets.length - 1

			for (var i = 0; i < this.datasets.length; i++) {
				if (this.ch.data.datasets[i]['label'] != this.datasets[i]['label']) {
					idx = i
					break
				}
			}

			this.ch.data.datasets.splice(idx, 1)

			// Set new length
			this.datasets_length = this.datasets.length

			// Invoke update
			this.ch.update();
		},

		update() {
			if (this.datasets.length > this.datasets_length) {
				this.append()
			} else if (this.datasets.length < this.datasets_length) {
				this.remove()
			}
		}
	},
}
</script>