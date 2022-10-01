<template>
  <div class="q-pa-md row q-gutter-md">
    <PopulationTable
        :country="country"
        :countries="countries"
        :population="population"
        @countrySelected="onCountrySelected"
    ></PopulationTable>
    <q-card>
      <q-card-section>
        <LineChart
            id="1"
            title="Population pyramid"
            :labeledData="groupedPopulation"
            :labeled-colors="labeledColors"
            :labeled-axes="{x: 'Age group', y: 'Population'}"
            :margin="{top: 7, right: 10, bottom: 20, left: 54}"
            :width="579"
            :height="600"
            :tickNumber=10
            :transition-duration="1000"
        ></LineChart>
      </q-card-section>
    </q-card>
    <div>
      <div class="row q-gutter-md">
        <q-card>
          <q-card-section>
            <LineChart
                id="2"
                title="Demographic profile"
                :labeledData="groupedPopulation"
                :labeled-colors="labeledColors"
                :labeled-axes="{x: 'Age group', y: 'Population'}"
                :margin="{top: 7, right: 10, bottom: 20, left: 54}"
                :width="579"
                :height="245"
                :tickNumber="10"
                :transition-duration="1000"
            ></LineChart>
          </q-card-section>
        </q-card>
        <q-card>
          <q-card-section>
            <LineChart
                id="3"
                title="Survival rate"
                :labeledData="groupedPopulation"
                :labeled-colors="labeledColors"
                :labeled-axes="{x: 'Age group', y: 'Population'}"
                :margin="{top: 5, right: 13, bottom: 20, left: 54}"
                :width="579"
                :height="245"
                :tickNumber=10
                :transition-duration="1000"
            ></LineChart>
          </q-card-section>
        </q-card>
      </div>
      <q-card style="margin-top: 15px">
        <q-card-section>
          <LineChart
              id="4"
              title="Population"
              :labeledData="groupedPopulation"
              :labeled-colors="labeledColors"
              :labeled-axes="{x: 'Age group', y: 'Population'}"
              :margin="{top: 7, right: 10, bottom: 20, left: 54}"
              :width="1180"
              :height="240"
              :tickNumber=10
              :transition-duration="1000"
          ></LineChart>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script>
import PopulationTable from './components/PopulationTable.vue'
import LineChart from "@/components/LineChart";
import populationDataCSV from '@/data/population.csv'
import {FiveYearAges} from "@/data/FiveYearAges";

export default {
  name: 'App',
  data() {
    const indexedCountries = this.indexByCountry(populationDataCSV)
    const countries = Object.keys(indexedCountries)
    const country = countries[Math.floor(Math.random() * countries.length)]
    const ageSelect = {start: 2016, end: 2021}
    const labeledColors = {2016: 'steelblue', 2021: 'red'}
    return {populationDataCSV, country, countries, indexedCountries, ageSelect, labeledColors}
  },
  components: {
    PopulationTable,
    LineChart
  },
  computed: {
    index() {
      return this.indexedCountries[this.country]
    },
    population() {
      return this.populationDataCSV.slice(this.index.start, this.index.end).filter(x => x.year === this.ageSelect.start || x.year === this.ageSelect.end)
    },
    groupedPopulation() {
      const groupedData = {}
      this.population.forEach(d => {
        if (d.year in groupedData) {
          groupedData[d.year].forEach(group => group.y = round(group.y + d[FiveYearAges[group.x]], 3))
        } else {
          groupedData[d.year] = Array.from(Object.keys(FiveYearAges).map(age => {
            return {x: Number(age), y: round(d[FiveYearAges[age]], 3)}
          }))
        }
      })
      return groupedData
    }
  },
  methods: {
    indexByCountry(data) {
      const indexedCountry = {}
      indexedCountry[data[0].country] = {start: 0}
      indexedCountry[data[data.length - 1].country] = {end: data.length}
      for (let i = 1; i < data.length; i++) {
        const lastCountry = data[i - 1].country
        const currentCountry = data[i].country
        if (currentCountry !== lastCountry) {
          indexedCountry[lastCountry].end = i
          indexedCountry[currentCountry] = {start: i}
        }
      }
      return indexedCountry
    },
    onCountrySelected(selectedCountry) {
      this.country = selectedCountry
    }
  },
}

function round(float_number, number_of_decimals) {
  return parseFloat(float_number.toFixed(number_of_decimals))
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
