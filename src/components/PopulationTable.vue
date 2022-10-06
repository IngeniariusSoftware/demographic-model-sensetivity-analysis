<template>
  <q-table
      dense
      :rows="rows"
      :columns="columns"
      style="width: 97vw;"
      virtual-scroll
      :rows-per-page-options="[0]"
      :virtual-scroll-sticky-size-start="48"
      hide-bottom>
    <template v-slot:top>
      <div class="column" style="min-width: 250px">
        <label>Population {{ yearExtent }}</label>
        <div class="row">
          <q-badge rounded color="pink" :label="`girls ${girlsPercentage.toFixed(1)}%`"/>
          <q-space/>
          <q-badge rounded color="steelblue" :label="`boys ${boysPercentage.toFixed(1)}%`"/>
          <q-space/>
          <q-badge rounded color="purple" :label="`fertility ${fertility}`"/>
        </div>
      </div>
      <q-space/>
      <q-slider
          :min="minYear"
          :max="maxYear"
          :step="stepYear"
          v-model="selectedYear"
          label-always
          style="max-width: 900px;
          margin-top: 25px"/>
      <q-space/>
      <q-btn
          round
          color="primary"
          :icon="isPlaying ? 'pause' : 'play_arrow'"
          @click="isPlaying = !isPlaying"/>
      <q-space/>
      <q-select
          outlined
          use-input
          input-debounce="0"
          @filter="onFilter"
          @update:model-value="onUpdate"
          style="width: 500px"
          behavior="menu"
          v-model="selectedCountry"
          :options="countryOptions"
      >
        <template v-slot:no-option>
          <q-item>
            <q-item-section class="text-grey">
              No results
            </q-item-section>
          </q-item>
        </template>
      </q-select>
    </template>
  </q-table>
</template>

<script>
import * as d3 from 'd3'
import {FiveYearAges} from "@/data/FiveYearAges"
import {fertilityAgeGroups, getBirthRates} from "@/classes/populationModel";

export default {
  name: 'PopulationTable',
  props: {
    country: {type: undefined, required: true},
    countries: {type: Array, required: true, default: Array.prototype},
    population: {type: Array, required: true},
    minYear: {type: Number, required: true},
    maxYear: {type: Number, required: true},
    stepYear: {type: Number, required: true},
    year: {type: Number, required: true}
  },
  data() {
    return {columns: [], selectedCountry: '', countryOptions: [], selectedYear: 0, isPlaying: false}
  },
  mounted() {
    this.generateColumns()
    this.selectedYear = this.year
    this.selectedCountry = this.country
    this.countryOptions = this.countries
    setInterval(this.increaseYear, 1200)
  },
  watch: {
    year() {
      this.selectedYear = this.year
    },
    selectedYear() {
      this.$emit('yearSelected', this.selectedYear)
    },
  },
  computed: {
    childrenCount() {
      return this.population[2]['0-4'] + this.population[3]['0-4']
    },
    girlsPercentage() {
      return this.population[2]['0-4'] / this.childrenCount * 100.0
    },
    boysPercentage() {
      return this.population[3]['0-4'] / this.childrenCount * 100.0
    },
    fertility() {
      const birthRates = getBirthRates(this.population[2], this.population[3])
      return ((birthRates.Male + birthRates.Female) * fertilityAgeGroups.length).toFixed(2)
    },
    rows() {
      return this.population ? this.population : []
    },
    yearExtent() {
      const extent = d3.extent(this.rows?.map(x => x.year))
      return extent[0] !== extent[1] ? extent.join('→') : extent[0]
    },
  },
  methods: {
    generateColumns() {
      this.columns = [
        {name: 'year', required: true, align: 'left', label: 'Year', field: 'year', sortable: true},
        {name: 'sex', required: true, align: 'left', label: 'Sex', field: 'sex', sortable: true},
      ]
      Object.values(FiveYearAges).forEach(age => this.columns.push({
        name: age,
        required: true,
        align: 'left',
        label: age,
        field: age,
        format: value => value.toLocaleString('fr-FR', {maximumFractionDigits: 3}),
        sortable: true
      }))
    },
    onUpdate(value) {
      if (this.countries.indexOf(value) > -1) {
        this.$emit('countrySelected', value)
      }
    },
    onFilter(value, update) {
      if (value === '') {
        update(() => {
          this.countryOptions = this.countries
        })

        return
      }

      update(() => {
        const val = value.toLowerCase()
        this.countryOptions = this.countries.filter(v => v.toLowerCase().indexOf(val) > -1)
      })
    },
    increaseYear() {
      if (this.isPlaying) {
        if (this.selectedYear === this.maxYear) {
          this.selectedYear = this.minYear
        } else if ((this.maxYear - this.selectedYear) === this.stepYear) {
          this.isPlaying = false
          this.selectedYear = this.maxYear
        } else {
          this.selectedYear += this.stepYear
        }
      }
    }
  }
}
</script>

<style>
</style>
