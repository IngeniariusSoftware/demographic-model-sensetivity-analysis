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
            :title="`${selectedDataLabel} population pyramid ${selectedYear}`"
            :labeledData="countryPopulationPyramidData"
            :labeled-colors="femaleMalePyramidLabeledColors"
            :labeled-axes="{x: 'Total Percentage', y: 'Age group'}"
            :margin="{top: 17, right: 12, bottom: 32, left: 34}"
            :width="width * 0.33"
            :height="height * 0.7"
            :tick-number-percentages="5"
            :format-x="x => FiveYearAges[x]"
            :format-y="y => Number(y).toLocaleString('fr-FR', {maximumFractionDigits: 3})"
        ></TwoValuesPyramid>
      </q-card-section>
    </q-card>
    <div>
      <div class="row q-gutter-md">
        <q-card>
          <q-card-section style="padding: 8px">
            <LinesChart
                id="2"
                title="Demographic profile"
                :labeledData="countryDemographicProfileData"
                :labeled-colors="demographicProfileLabeledColors"
                :labeled-axes="{x: 'Age group', y: 'Population'}"
                :margin="margin"
                :width="width * 0.3"
                :height="height * 0.32"
                :format-y="y => Number(y).toLocaleString('fr-FR', {maximumFractionDigits: 3})"
                :format-x="x => FiveYearAges[x]"
            ></LinesChart>
          </q-card-section>
        </q-card>
        <q-card>
          <q-card-section style="padding: 8px">
            <LinesChart
                id="3"
                :title="`Survival rate ${this.ageSelect.start}→${this.ageSelect.end}`"
                :labeledData="countrySurvivalRatesData"
                :labeled-colors="femaleMaleLabeledColors"
                :labeled-axes="{x: 'Age group', y: 'Survival rate'}"
                :margin="{top: 17, right: 12, bottom: 32, left: 27}"
                :width="width * 0.3"
                :height="height * 0.32"
                :format-x="x => FiveYearAges[x]"
            ></LinesChart>
          </q-card-section>
        </q-card>
      </div>
      <q-card style="margin-top: 15px">
        <q-card-section style="padding: 8px">
          <LinesChart
              id="4"
              title="Population"
              :labeledData="countryPopulationGroupByYearData"
              :labeled-colors="populationLabeledColors"
              :labeled-axes="{x: 'Year', y: 'Population'}"
              :margin="margin"
              :width="width * 0.6"
              :height="height * 0.32"
              :show-grid="false"
              :format-x="x => x"
              :format-y="y => Number(y).toLocaleString('fr-FR', {maximumFractionDigits: 3})"
              :show-dots="false"
              :selected-x="selectedYear"
              :selected-label="selectedDataLabel"
              tooltip-type="lines"
              @xSelected="selectedYear = $event"
              @labelSelected="selectedDataLabel = $event"
              :tick-number-x="20"
          ></LinesChart>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script>
import PopulationTable from './components/PopulationTable.vue'
import LinesChart from "@/components/LinesChart"
import populationDataCSV from '@/data/population.csv'
import {FiveYearAges} from "@/data/FiveYearAges"
import TwoValuesPyramid from "@/components/TwoValuesPyramid"
import {round, getSurvivalRate, predict} from '@/classes/populationModel'

export default {
  name: 'App',
  data() {
    const indexedCountries = this.indexByCountry(populationDataCSV)
    const countries = Object.keys(indexedCountries)
    const selectedCountry = countries[Math.floor(Math.random() * countries.length)]
    const stepYear = 5
    const ageSelect = {start: 2016, end: 2021}
    const margin = {top: 17, right: 12, bottom: 32, left: 80}
    const maxYear = 2096
    const minYear = maxYear - (Math.floor((maxYear - populationDataCSV[0].year) / stepYear) * stepYear)
    const selectedYear = minYear
    const selectedDataLabel = 'My'
    const yearStart = populationDataCSV[0].year
    return {
      populationDataCSV,
      selectedCountry,
      countries,
      indexedCountries,
      ageSelect,
      margin,
      selectedYear,
      stepYear,
      minYear,
      maxYear,
      selectedDataLabel,
      yearStart,
      FiveYearAges,
      width: window.innerWidth,
      height: window.innerHeight
    }
  },
  components: {
    TwoValuesPyramid,
    PopulationTable,
    LinesChart
  },
  computed: {
    index() {
      return this.indexedCountries[this.selectedCountry]
    },
    demographicProfileLabeledColors() {
      return {[this.ageSelect.start]: 'orange', [this.ageSelect.end]: 'red'}
    },
    populationLabeledColors() {
      return {'My': 'green', 'United Nations': '#800049'}
    },
    femaleMaleLabeledColors() {
      return {Female: '#ee7989', Male: '#4682B4'}
    },
    femaleMalePyramidLabeledColors() {
      return {Female: '#ee7989', Male: '#4682B4', overFemale: '#c7223b', overMale: '#0d4979'}
    },
    UNCountryPopulation() {
      return this.populationDataCSV.slice(this.index.start, this.index.end)
    },
    myCountryPopulation() {
      const indexEnd = this.index.start + ((this.ageSelect.end - this.yearStart) / this.stepYear * 2)
      const estimatedData = this.populationDataCSV.slice(this.index.start, indexEnd + 2)
      return estimatedData.concat(this.predictedData)
    },
    countryPopulationYearSelect() {
      return this.countryPopulationAtYear(this.UNCountryPopulation, this.ageSelect.start)
          .concat(this.countryPopulationAtYear(this.UNCountryPopulation, this.ageSelect.end))
    },
    countryPopulationPyramidData() {
      const data = this.countryPopulationAtYear(this.selectedDataLabel === 'My' ? this.myCountryPopulation : this.UNCountryPopulation, this.selectedYear)
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
          groupedData[d.year].forEach(group => group.y = group.y + d[FiveYearAges[group.x]])
        } else {
          groupedData[d.year] = Array.from(Object.entries(FiveYearAges).map(([key, value]) => {
            return {x: Number(key), y: d[value]}
          }))
        }
      })

      return Object.entries(groupedData)
    },
    countryPopulationGroupByYearData() {
      const groupedData = []
      const dataNames = ['My', 'United Nations']
      dataNames.forEach(dataName => {
        const data = dataName === 'My' ? this.myCountryPopulation : this.UNCountryPopulation
        const result = []
        for (let i = 0; i < data.length; i += 2) {
          let yearPopulation = 0
          const female = data[i]
          const male = data[i + 1]
          Object.values(FiveYearAges).forEach(age => yearPopulation += male[age] + female[age])
          result.push({x: data[i].year, y: round(yearPopulation, 3)})
        }

        groupedData.push([dataName, result])
      })

      return groupedData
    },
    countrySurvivalRatesData() {
      const femaleYearStartData = this.countryPopulationYearSelect[0]
      const femaleYearEndData = this.countryPopulationYearSelect[2]
      const maleYearStartData = this.countryPopulationYearSelect[1]
      const maleYearEndData = this.countryPopulationYearSelect[3]
      const survivalRate = [[], []]

      Object.values(FiveYearAges).forEach((age, i, ages) => {
        if (i < ages.length - 1) {
          survivalRate[0].push({
            x: parseInt(age),
            y: getSurvivalRate(femaleYearStartData[age], femaleYearEndData[ages[i + 1]], true)
          })
          survivalRate[1].push({
            x: parseInt(age),
            y: getSurvivalRate(maleYearStartData[age], maleYearEndData[ages[i + 1]], true)
          })
        }
      })

      return [['Female', survivalRate[0]], ['Male', survivalRate[1]]]
    },
    predictedData() {
      return predict(this.countryPopulationYearSelect, this.maxYear)
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
    countryPopulationAtYear(data, year) {
      const index = (year - this.yearStart) / this.stepYear * 2

      return data.slice(index, index + 2)
    }
  },
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
