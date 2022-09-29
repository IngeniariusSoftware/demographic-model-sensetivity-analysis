<template>
  <div class="q-pa-md row justify-start q-gutter-md">
    <PopulationTable :country="country" :population="this.population"/>
    <q-card class="my-card">
      <q-card-section>
        <LineChart
            container-i-d="lineChartContainer1"
            title="Demographic profile"
            :labeledData="this.groupedPopulation"
            :labeled-colors="{2016: 'red', 2021: 'steelblue'}"
            :labeled-axis="{x: 'Age group', y: 'Population'}"
            :margin="{top: 5, right: 13, bottom: 20, left: 54}"
            :width="800"
            :height="480"
            :tickNumber=10>
        </LineChart>
      </q-card-section>
    </q-card>
  </div>
</template>

<script>
import PopulationTable from './components/PopulationTable.vue'
import LineChart from "@/components/LineChart";
import PopulationData from '@/data/population.csv'

const FiveYearAges = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99', '100+']

export default {
  name: 'App',
  setup() {
    const indexedCountries = indexByArea(PopulationData)
    const country = 'Afghanistan'
    const index = indexedCountries[country]
    const population = PopulationData.slice(index.start, index.end).filter(x => x.year === 2016 || x.year === 2021)
    const groupedPopulation = groupByYearData(population)
    return {country, population, groupedPopulation, indexedCountries}
  },
  components: {
    PopulationTable,
    LineChart
  },
  methods: {}
}

function groupByYearData(data) {
  const groupedData = {}
  data.forEach(d => {
    if (d.year in groupedData) {
      groupedData[d.year].forEach(group => group.y += d[group.x])
    } else {
      groupedData[d.year] = Array.from(FiveYearAges.map(age => {
        return {x: age, y: d[age]}
      }))
    }
  })
  return groupedData
}

function indexByArea(data) {
  const indexedPlace = {}
  indexedPlace[data[0].area] = {start: 0}
  indexedPlace[data[data.length - 1].area] = {end: data.length}
  for (let i = 1; i < data.length; i++) {
    const lastPlace = data[i - 1].area
    const currentPlace = data[i].area
    if (currentPlace !== lastPlace) {
      indexedPlace[lastPlace].end = i
      indexedPlace[currentPlace] = {start: i}
    }
  }
  return indexedPlace
}

</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

label {
  font-weight: bold;
  line-height: 2;
}

.unselectable {
  pointer-events: none;
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none; /* Old versions of Firefox */
  -ms-user-select: none; /* Internet Explorer/Edge */
  user-select: none; /* Non-prefixed version, currently supported by Chrome, Edge, Opera and Firefox */
}
</style>
