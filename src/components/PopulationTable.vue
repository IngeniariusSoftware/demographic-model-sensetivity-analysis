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
          style="max-width: 1400px;
          margin-top: 25px"/>
      <q-space/>
      <q-btn
          round
          color="primary"
          :icon="isPlaying ? 'pause' : 'play_arrow'"
          @click="isPlaying = !isPlaying"/>
      <q-space/>
    </template>
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="year" :props="props">{{ props.row.year }}</q-td>
        <q-td key="sex" :props="props">{{ props.row.sex }}</q-td>
        <q-td key="0-4" :props="props"> {{
            Number(props.row['0-4']).toLocaleString('fr-FR', {maximumFractionDigits: 3})
          }}
          <q-popup-edit v-model="props.row['0-4']" title="Update 0-4" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="5-9" :props="props"> {{
            Number(props.row['5-9']).toLocaleString('fr-FR', {maximumFractionDigits: 3})
          }}
          <q-popup-edit v-model="props.row['5-9']" title="Update 5-9" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="10-14" :props="props">
          {{ Number(props.row['10-14']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['10-14']" title="Update 10-14" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="15-19" :props="props">
          {{ Number(props.row['15-19']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['15-19']" title="Update 15-19" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="20-24" :props="props">
          {{ Number(props.row['20-24']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['20-24']" title="Update 20-24" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="25-29" :props="props">
          {{ Number(props.row['25-29']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['25-29']" title="Update 25-29" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="30-34" :props="props">
          {{ Number(props.row['30-34']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['30-34']" title="Update 30-34" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="35-39" :props="props">
          {{ Number(props.row['35-39']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['35-39']" title="Update 35-39" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="40-44" :props="props">
          {{ Number(props.row['40-44']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['40-44']" title="Update 40-44" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="45-49" :props="props">
          {{ Number(props.row['45-49']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['45-49']" title="Update 45-49" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="50-54" :props="props">
          {{ Number(props.row['50-54']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['50-54']" title="Update 50-54" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="55-59" :props="props">
          {{ Number(props.row['55-59']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['55-59']" title="Update 55-59" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="60-64" :props="props">
          {{ Number(props.row['60-64']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['60-64']" title="Update 60-64" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="65-69" :props="props">
          {{ Number(props.row['65-69']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['65-69']" title="Update 65-69" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="70-74" :props="props">
          {{ Number(props.row['70-74']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['70-74']" title="Update 70-74" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="75-79" :props="props">
          {{ Number(props.row['75-79']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['75-79']" title="Update 75-79" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="80-84" :props="props">
          {{ Number(props.row['80-84']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['80-84']" title="Update 80-84" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="85-89" :props="props">
          {{ Number(props.row['85-89']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['85-89']" title="Update 85-89" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="90-94" :props="props">
          {{ Number(props.row['90-94']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['90-94']" title="Update 90-94" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="95-99" :props="props">
          {{ Number(props.row['95-99']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['95-99']" title="Update 95-99" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
        <q-td key="100+" :props="props">
          {{ Number(props.row['100+']).toLocaleString('fr-FR', {maximumFractionDigits: 3}) }}
          <q-popup-edit v-model="props.row['100+']" title="Update 100+" buttons v-slot="scope">
            <q-input type="number" v-model.number="scope.value" dense autofocus/>
          </q-popup-edit>
        </q-td>
      </q-tr>
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
    population: {type: Array, required: true},
    minYear: {type: Number, required: true},
    maxYear: {type: Number, required: true},
    stepYear: {type: Number, required: true},
    year: {type: Number, required: true}
  },
  data() {
    return {columns: [], selectedYear: 0, isPlaying: false}
  },
  mounted() {
    this.generateColumns()
    this.selectedYear = this.year
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
        format: value => Number(value).toLocaleString('fr-FR', {maximumFractionDigits: 3}),
        sortable: true
      }))
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
