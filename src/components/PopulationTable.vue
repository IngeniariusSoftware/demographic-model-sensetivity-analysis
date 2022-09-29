<template>
  <q-table
      :title="`Population ${country} from ${yearExtent} in thousands`"
      :rows="rows"
      :columns="columns"
      style="width: 97.3vw; max-height: 390px;"
      virtual-scroll
      :rows-per-page-options="[0]"
      :virtual-scroll-sticky-size-start="48"
      hide-bottom
  />
</template>

<script>
import * as d3 from 'd3'

const FiveYearAges = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99', '100+']

export default {
  name: 'PopulationTable',
  props: {
    country: String,
    population: Array
  },
  data() {
    return {columns: [], rows: []}
  },
  mounted() {
    this.generateColumns()
    this.rows = this.population

  },
  computed: {
    yearExtent() {
      const extent = d3.extent(this.rows?.map(x => x.year))
      return extent[0] !== extent[1] ? extent.join(' to ') : extent[0]
    },
  },
  methods: {
    generateColumns() {
      this.columns = [
        {name: 'year', required: true, align: 'left', label: 'Year', field: 'year', sortable: true},
        {name: 'sex', required: true, align: 'left', label: 'Sex', field: 'sex', sortable: true},
      ]
      FiveYearAges.forEach(age => this.columns.push({
        name: age,
        required: true,
        align: 'left',
        label: age,
        field: age,
        format: value =>  value.toFixed(value < 10.0 ? 3 : 0),
        sortable: true
      }))
    },
  }
}
</script>

<style scoped>
</style>
