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
      <a>Population {{ country }} {{ yearExtent }} in thousands</a>
      <q-space/>
      <q-select
          outlined
          use-input
          input-debounce="0"
          @popup-hide="onSelect"
          @filter="onFilter"
          style="width: 500px"
          behavior="menu"
          v-model="selectedCountry"
          :model-value="selectedCountry"
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
    country: {type: String, required: true},
    countries: {type: Array, required: true},
    population: {type: Array, required: true}
  },
  data() {
    return {columns: [], selectedCountry: '', countryOptions: []}
  },
  mounted() {
    this.generateColumns()
    this.countryOptions = this.countries
    this.selectedCountry = this.country
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
    onSelect() {
      this.$emit('countrySelected', this.selectedCountry)
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
  }
}
</script>

<style scoped>
</style>
