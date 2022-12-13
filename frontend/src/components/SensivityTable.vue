<template>
  <q-table
      dense
      :rows="sensitivityData"
      :columns="columns"
      style="width: 97vw; max-height: 10vw"
      virtual-scroll
      :rows-per-page-options="[0]"
      :virtual-scroll-sticky-size-start="48"
      hide-bottom>
    <template v-slot:top>
      <label>Sensitivity analysis</label>
      <q-space/>
      <div class="q-pa-xs-lg">
        <q-option-group
            name="Years"
            v-model="selectedYear"
            :options="yearOptions"
            color="primary"
            @update:model-value="this.$emit('yearSelected', $event)"
            inline
        />
      </div>
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

export default {
  name: 'PopulationTable',
  props: {
    country: {type: undefined, required: true},
    countries: {type: Array, required: true, default: Array.prototype},
    year: {type: Number, required: true},
    years: {type: Array, required: true},
    sensitivityData: {type: Array, required: true},
  },
  data() {
    const columnsNames = ['fertility', 'female_percentage', '0-4_female', '5-9_female', '10-14_female', '15-19_female', '20-24_female', '25-29_female', '30-34_female', '35-39_female', '40-44_female', '45-49_female', '50-54_female', '55-59_female', '60-64_female', '65-69_female', '70-74_female', '75-79_female', '80-84_female', '85-89_female', '90-94_female', '95-99_female', '0-4_male', '5-9_male', '10-14_male', '15-19_male', '20-24_male', '25-29_male', '30-34_male', '35-39_male', '40-44_male', '45-49_male', '50-54_male', '55-59_male', '60-64_male', '65-69_male', '70-74_male', '75-79_male', '80-84_male', '85-89_male', '90-94_male', '95-99_male']
    const columns = [{name: 'years', align: 'left', label: 'years', field: 'years'}]
    columns.push(...columnsNames.map(column => {
          return {
            name: column,
            align: 'left',
            label: column,
            field: column,
            format: val => {
              if (val != null) {
                const value = JSON.parse(val)
                if (typeof value == 'number') {
                  return value.toFixed(3)
                } else {
                  return `${value[0].toFixed(3)} - ${value[1].toFixed(3)}`
                }
              } else {
                return '-'
              }
            },
            sortable: true
          }
        }
    ))
    return {columns, countryOptions: [], selectedCountry: '', yearOptions: [], selectedYear: 10,}
  },
  mounted() {
    this.selectedYear = this.year
    this.yearOptions = this.years.map(x => {
      return {label: x.toString(), value: x}
    })
    this.selectedCountry = this.country
    this.countryOptions = this.countries
  },
  computed: {
    rows() {
      return this.sensitivityData ? this.sensitivityData : []
    }
  },
  methods: {
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
    }
  }
}
</script>

<style>
</style>
