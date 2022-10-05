<template>
  <div class="q-pa-md row q-gutter-md">
    <PopulationTable
        :country="selectedCountry"
        :countries="countries"
        :population="countryPopulationYearSelect"
        :min-year="minYear"
        :max-year="maxYear"
        :year="selectedYear"
        :step-year="stepYear"
        @countrySelected="selectedCountry = $event"
        @yearSelected="selectedYear = $event"
    ></PopulationTable>
    <q-card>
      <q-card-section style="padding: 8px">
        <TwoValuesPyramid
            id="1"
            :title="`Population pyramid ${selectedYear}`"
            :labeledData="countryPopulationPyramidData"
            :labeled-colors="femaleMaleLabeledColors"
            :labeled-axes="{x: 'Total Percentage', y: 'Age group'}"
            :margin="{top: 17, right: 12, bottom: 32, left: 26}"
            :width="579"
            :height="660"
            :tick-number-x="5"
            :tick-format-x="x => `${x}%`"
        ></TwoValuesPyramid>
      </q-card-section>
    </q-card>
    <div>
      <div class="row q-gutter-md">
        <q-card>
          <q-card-section style="padding: 8px">
            <LineChart
                id="2"
                title="Demographic profile"
                :labeledData="countryDemographicProfileData"
                :labeled-colors="demographicProfileLabeledColors"
                :labeled-axes="{x: 'Age group', y: 'Population'}"
                :margin="margin"
                :width="600"
                :height="304"
            ></LineChart>
          </q-card-section>
        </q-card>
        <q-card>
          <q-card-section style="padding: 8px">
            <LineChart
                id="3"
                :title="`Survival rate ${this.ageSelect.start}→${this.ageSelect.end}`"
                :labeledData="countrySurvivalRateData"
                :labeled-colors="femaleMaleLabeledColors"
                :labeled-axes="{x: 'Age group', y: 'Survival rate'}"
                :margin="margin"
                :width="600"
                :height="304"
                :tick-number-x="20"
            ></LineChart>
          </q-card-section>
        </q-card>
      </div>
      <q-card style="margin-top: 15px">
        <q-card-section style="padding: 8px">
          <LineChart
              id="4"
              title="Population"
              :labeledData="countryPopulationGroupByYearData"
              :labeled-colors="populationLabeledColors"
              :labeled-axes="{x: 'Year', y: 'Population'}"
              :margin="margin"
              :width="1220"
              :height="310"
              :show-grid="false"
              :tick-format-x="d => d"
              :show-dots="false"
              :selected-x="selectedYear"
              tooltip-type="lines"
              @xSelected="selectedYear = $event"
              :tick-number-x="11"
          ></LineChart>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script>
import PopulationTable from './components/PopulationTable.vue'
import LinesChart from "@/components/LinesChart";
import populationDataCSV from '@/data/population.csv'
import {FiveYearAges} from "@/data/FiveYearAges";
import TwoValuesPyramid from "@/components/TwoValuesPyramid";

export default {
  name: 'App',
  data() {
    const indexedCountries = this.indexByCountry(populationDataCSV)
    const countries = Object.keys(indexedCountries)
    const selectedCountry = countries[Math.floor(Math.random() * countries.length)]
    const stepYear = 5
    const ageSelect = {start: 2016, end: 2021}
    const margin = {top: 17, right: 12, bottom: 32, left: 54}
    const maxYear = 2021
    const minYear = maxYear - (Math.floor((maxYear - populationDataCSV[0].year) / stepYear) * stepYear)
    const selectedYear = minYear
    return {populationDataCSV, selectedCountry, countries, indexedCountries, ageSelect, margin, selectedYear, stepYear, minYear, maxYear}
  },
  components: {
    TwoValuesPyramid,
    PopulationTable,
    LineChart: LinesChart
  },
  computed: {
    index() {
      return this.indexedCountries[this.selectedCountry]
    },
    demographicProfileLabeledColors() {
      return {[this.ageSelect.start]: 'orange', [this.ageSelect.end]: 'red'}
    },
    populationLabeledColors() {
      return {[this.selectedCountry]: 'green'}
    },
    femaleMaleLabeledColors() {
      return {Female: '#ee7989', Male: '#4682B4', overFemale: '#c7223b', overMale: '#0d4979'}
    },
    countryPopulation() {
      return this.populationDataCSV.slice(this.index.start, this.index.end)
    },
    countryPopulationYearSelect() {
      return this.countryPopulation.filter(x => x.year === this.ageSelect.start || x.year === this.ageSelect.end)
    },
    countryPopulationPyramidData() {
      const data = this.countryPopulation.filter(x => x.year === this.selectedYear)
      let population = 0
      const femaleData = Array.from(Object.entries(FiveYearAges).map(([key, value]) => {
        population += data[0][value]
        return {x: Number(key), y: round(data[0][value], 3), percentage: 0.0}
      }))
      const maleData = Array.from(Object.entries(FiveYearAges).map(([key, value]) => {
        population += data[1][value]
        return {x: Number(key), y: round(data[1][value], 3), percentage: 0.0}
      }))
      femaleData.forEach(d => d.percentage = round(d.y / population * 100.0, 3))
      maleData.forEach(d => d.percentage = round(d.y / population * 100.0, 3))
      return [['Female', femaleData], ['Male', maleData]]
    },
    countryDemographicProfileData() {
      const groupedData = {}
      this.countryPopulationYearSelect.forEach(d => {
        if (d.year in groupedData) {
          groupedData[d.year].forEach(group => group.y = round(group.y + d[FiveYearAges[group.x]], 3))
        } else {
          groupedData[d.year] = Array.from(Object.entries(FiveYearAges).map(([key, value]) => {
            return {x: Number(key), y: round(d[value], 3)}
          }))
        }
      })

      return Object.entries(groupedData)
    },
    countryPopulationGroupByYearData() {
      const data = []
      for (let i = this.countryPopulation.length - 2; i > 0; i -= 10) {
        let yearPopulation = 0
        const female = this.countryPopulation[i]
        const male = this.countryPopulation[i + 1]
        Object.values(FiveYearAges).forEach(age => yearPopulation += male[age] + female[age])
        data.push({x: this.countryPopulation[i].year, y: round(yearPopulation, 3)})
      }

      data.reverse()
      return [[this.selectedCountry, data]]
    },
    countrySurvivalRateData() {
      const femaleYearStart = this.countryPopulationYearSelect[0]
      const femaleYearEnd = this.countryPopulationYearSelect[2]
      const maleYearStart = this.countryPopulationYearSelect[1]
      const maleYearEnd = this.countryPopulationYearSelect[3]
      const femaleData = Array.from(Object.values(FiveYearAges).map((age, i, ages) => {
        return {x: parseInt(age), y: getSurvivalRate(femaleYearStart[age], femaleYearEnd[ages[i + 1]])}
      }))
      femaleData.pop()
      const maleData = Array.from(Object.values(FiveYearAges).map((age, i, ages) => {
        return {x: parseInt(age), y: getSurvivalRate(maleYearStart[age], maleYearEnd[ages[i + 1]])}
      }))
      maleData.pop()
      return [['Female', femaleData], ['Male', maleData]]
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
  },
}

function getSurvivalRate(start, end) {
  const value = end / start
  return isNaN(value) ? 0.0 : round(value, 3)
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

.pointersRect {
  fill: none;
  pointer-events: all;
  /*noinspection CssNonIntegerLengthInPixels*/
  stroke-width: 0.2px;
  stroke: black;
}

.charTitle {
  text-anchor: middle;
  font-weight: 600;
}

</style>
