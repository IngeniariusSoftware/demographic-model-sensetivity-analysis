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
      <label>Population {{ country }} {{ yearExtent }} in thousands</label>
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
      <q-btn round color="primary" :icon="isPlaying ? 'pause' : 'play_arrow' " @click="isPlaying = !isPlaying"/>
      <q-space/>
      <q-select
          outlined
          use-input
          input-debounce="0"
          @filter="onFilter"
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
import {FiveYearAges} from "@/data/FiveYearAges";

export default {
  name: 'PopulationTable',
  props: {
    country: {type: undefined, required: true},
    countries: {type: Array, required: true},
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
    this.countryOptions = this.countries
    this.selectedYear = this.year
    this.selectedCountry = this.country
    setInterval(this.increaseYear, 1200)
  },
  watch: {
    year() {
      this.selectedYear = this.year
    },
    selectedYear() {
      this.$emit('yearSelected', this.selectedYear)
    },
    selectedCountry() {
      this.$emit('countrySelected', this.selectedCountry)
    },
  },
  computed: {
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
        format: value => value < 10.0 ? value.toFixed(3) : Math.round(value).toLocaleString('fr-FR', {maximumFractionDigits: 3}),
        sortable: true
      }))
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
          this.selectedYear = this.maxYear
          this.isPlaying = false
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
