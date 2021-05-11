<template>
	<div class="app">
		<header>
			<h1>covid-19</h1>
		</header>
		<main>
			<nav>
				<input list="countries-json" v-model=iso />
				<datalist id="countries-json" />
				<ul>
					<li :style=country.style v-for="country in countries" :key=country.name @click=removeCountryByIso(country.iso)>{{country.name}}</li>
				</ul>
			</nav>
			<section>
				<article>
					<Chart id=tc title="Total cases per million" :datasets=datasets.tc />
				</article>
				<article>
					<Chart id=td title="Total deaths per million" :datasets=datasets.td />
				</article>
				<article>
					<Chart id=pv title="People vaccinated per hundred" :datasets=datasets.pv />
				</article>
				<article>
					<Chart id=fv title="People fully vaccianted per hundred" :datasets=datasets.fv />
				</article>
			</section>
		</main>
	</div>
</template>
<script>
import Chart from './components/Chart.vue'
import countries_json from './countries.json'
// import hungary from './hungary.json'

export default {
	name: 'App',

	components: {
		Chart
	},

	data() {
		return {
			api: 'https://covid.tamasfederer.com/iso.php',

			labels: [],

			datasets: {
				tc: [],
				td: [],
				pv: [],
				fv: [],
			},

			countries: [],

			iso: '',
		}
	},

	watch: {
		iso() {
			// Save iso
			let iso = this.iso

			// Add country to the country list
			let country = this.addCountryByIso(iso)

			if (country) {
				// In case of success clear input field
				this.iso = ''

				// Todo add data to the data
				this.addCountryToGraph(country)
			}
		},
	},

	created() {
		// Add hungary
		let country = this.addCountryByIso('HUN')

		// Add country
		this.addCountryToGraph(country)

		// Prepare labels
		// this.prepareLabels(hungary)

		// Add data to dataset
		// this.addDataToGraph(hungary, country)
	},

	mounted() {
		// Populate datalist
		var dataList = document.getElementById('countries-json');

		countries_json.forEach(function(item) {
			var option = document.createElement('option');

			option.text = item.name;
			option.value = item.iso;

			dataList.appendChild(option);
		});
	},

	methods: {
		addCountryByIso(iso) {
			// Check if country is in the list already
			let match = false

			for (var i = 0; i < this.countries.length; i++) {
				if (this.countries[i]['iso'] == iso) {
					match = true
					break
				}
			}

			if (match) {
				return false
			}

			// Get name
			let name = ''

			for (var j = 0; j < countries_json.length; j++) {
				if (countries_json[j]['iso'] == iso) {
					name = countries_json[j]['name']
					break
				}
			}

			if (name == '') {
				return false
			}

			// Create a style
			let r = Math.floor(Math.random() * 204) + 0
			let g = Math.floor(Math.random() * 204) + 0
			let b = Math.floor(Math.random() * 204) + 0

			let style = 'background-color: rgb(' + r + ', ' + g + ', ' + b + ')'

			// Push it to the countries
			this.countries.push({ 'name': name, 'iso': iso, 'style': style, 'r': r, 'g': g, 'b': b })

			// Return
			return { 'name': name, 'iso': iso, 'style': style, 'r': r, 'g': g, 'b': b }
		},

		removeCountryByIso(iso) {
			let match = this.countries.length
			var country

			for (var i = 0; i < this.countries.length; i++) {
				if (this.countries[i]['iso'] == iso) {
					match = i
					country = this.countries[i]
					break
				}
			}

			if (match == this.countries.length) {
				return
			}

			this.countries.splice(i, 1)

			this.removeDataFromGraph(country)
		},

		prepareLabels(response) {
			for (let key in response['data']) {
				this.labels.push(key)
			}
		},

		addDataToGraph(response, country) {
			// Add Total cases per million
			let prev_val = 0
			let tc_data = []

			for (let key in response['data']) {
				let val = parseInt(response['data'][key]['total_cases_per_million'])

				if (isNaN(val)) {
					val = prev_val
				}

				prev_val = val

				tc_data.push(val)
			}

			this.datasets.tc.push({
				'type': 'line',
				'label': country.name,
				'labels': this.labels,
				'data': tc_data,
				'color': [country.r, country.g, country.b],
			})

			// Add Total deaths per million
			prev_val = 0
			let td_data = []

			for (let key in response['data']) {
				let val = parseInt(response['data'][key]['total_deaths_per_million'])

				if (isNaN(val)) {
					val = prev_val
				}

				prev_val = val

				td_data.push(val)
			}

			this.datasets.td.push({
				'type': 'line',
				'label': country.name,
				'labels': this.labels,
				'data': td_data,
				'color': [country.r, country.g, country.b],
			})

			// Add new cases per million
			prev_val = 0
			let pv_data = []

			for (let key in response['data']) {
				let val = parseInt(response['data'][key]['people_vaccinated_per_hundred'])

				if (isNaN(val)) {
					val = prev_val
				}

				prev_val = val

				pv_data.push(val)
			}

			this.datasets.pv.push({
				'type': 'line',
				'label': country.name,
				'labels': this.labels,
				'data': pv_data,
				'color': [country.r, country.g, country.b],
			})

			// Fully vaccinated
			prev_val = 0
			let fv_data = []

			for (let key in response['data']) {
				let val = parseInt(response['data'][key]['people_fully_vaccinated_per_hundred'])

				if (isNaN(val)) {
					val = prev_val
				}

				prev_val = val

				fv_data.push(val)
			}

			this.datasets.fv.push({
				'type': 'line',
				'label': country.name,
				'labels': this.labels,
				'data': fv_data,
				'color': [country.r, country.g, country.b],
			})
		},

		removeDataFromGraph(country) {
			for (var i = 0; i < this.datasets.tc.length; i++) {
				if (this.datasets.tc[i]['label'] == country.name) {
					this.datasets.tc.splice(i, 1)
					this.datasets.td.splice(i, 1)
					this.datasets.pv.splice(i, 1)
					this.datasets.fv.splice(i, 1)
					break
				}
			}
		},

		addCountryToGraph(country) {
			let iso = country['iso']

			// Read data from API
			fetch(this.api + '?iso=' + iso)
				.then(response => response.json())
				.then(data => {
					if (this.labels.length == 0) {
						for (let key in data['data']) {
							this.labels.push(key)
						}
					}

					this.addDataToGraph(data, country)
				});
		},
	},
}
</script>
<style scoped>
/* app div */
.app {
	width: 100vw;

	display: flex;
	justify-content: center;
}

/* Header */
header {
	width: 100vw;
	height: 4rem;

	position: fixed;

	z-index: 2;

	background-color: var(--header-bg-color);
	text-align: center;
}

header h1 {
	color: var(--header-fg-color);

	text-transform: uppercase;
	font-weight: bold;
	letter-spacing: 4px;

	line-height: 4rem;
}

/* Main */
main {
	width: 100%;
	max-width: 960px;

	margin-top: 4rem;
	padding: 0rem 1rem;
}

/* Control elements */
nav {
	height: 4rem;

	padding: 1rem 0rem;
}

nav input {
	height: 2rem;
	width: 240px;

	margin-bottom: 1rem;
	padding-left: 1rem;

	border-width: 0px;
	border-radius: 32px;

	box-shadow: 0px 0px 3px black;

	transition: .2s;
}

nav input::-webkit-calendar-picker-indicator {
	display: none;
	/* remove small arrow */
}

nav input:focus {
	border-width: 0;
	border-color: var(--input-glow-color);
	box-shadow: 0px 0px 8px var(--input-glow-color);
	outline: none;

	transition: .2s;
}

/* Countries */
nav ul {
	list-style-type: none;
}

nav ul li {
	float: left;

	font-size: 12px;

	border-width: 0px;
	border-radius: 32px;

	padding: .25rem .5rem;
	margin-right: .5rem;

	color: rgb(255, 255, 255);

	transition: .2s;
}

nav ul li:hover {
	cursor: not-allowed;
	filter: blur(4px);
	transform: scale(1.1, 1.1);
	transition: .1s;
}

section {
	width: 100%;

	display: flex;
	flex-direction: row;
	flex-wrap: wrap;
}

article {
	width: 480px;
}


@media only screen and (max-width: 992px) {
	article {
		width: 100%;
	}
}
</style>