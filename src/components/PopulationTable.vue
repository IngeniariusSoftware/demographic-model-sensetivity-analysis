<template>
  <div class="q-pa-md">
    <q-table
        :title="`Population of ${rows[0]?.country}`"
        :rows="rows"
        :columns="columns"
        hide-bottom
    />
  </div>
</template>

<script>
export default {
  name: 'PopulationTable',
  props: {
    population: Array
  },
  data() {
    console.log('1')
    return {columns: [], rows: []}
  },
  mounted() {
    this.columns = [
      {name: 'year', required: true, align: 'left', label: 'Year', field: 'year', sortable: true},
      {name: 'sex', required: true, align: 'left', label: 'Sex', field: 'sex', sortable: true},
      {name: 'age_0_4', required: true, align: 'left', label: '0-4', field: 'age_0_4', sortable: true},
      {name: 'age_5_9', required: true, align: 'left', label: '5-9', field: 'age_5_9', sortable: true},
      {name: 'age_10_14', required: true, align: 'left', label: '10-14', field: 'age_10_14', sortable: true},
      {name: 'age_15_19', required: true, align: 'left', label: '15-19', field: 'age_15_19', sortable: true},
      {name: 'age_20_24', required: true, align: 'left', label: '20-24', field: 'age_20_24', sortable: true},
      {name: 'age_25_29', required: true, align: 'left', label: '25-29', field: 'age_25_29', sortable: true},
      {name: 'age_30_34', required: true, align: 'left', label: '30-34', field: 'age_30_34', sortable: true},
      {name: 'age_35_39', required: true, align: 'left', label: '35-39', field: 'age_35_39', sortable: true},
      {name: 'age_40_44', required: true, align: 'left', label: '40-44', field: 'age_40_44', sortable: true},
      {name: 'age_45_49', required: true, align: 'left', label: '45-49', field: 'age_45_49', sortable: true},
      {name: 'age_50_54', required: true, align: 'left', label: '50-54', field: 'age_50_54', sortable: true},
      {name: 'age_55_59', required: true, align: 'left', label: '55-59', field: 'age_55_59', sortable: true},
      {name: 'age_60_64', required: true, align: 'left', label: '60-64', field: 'age_60_64', sortable: true},
      {name: 'age_65_69', required: true, align: 'left', label: '65-69', field: 'age_65_69', sortable: true},
      {name: 'age_70_74', required: true, align: 'left', label: '70-74', field: 'age_70_74', sortable: true},
      {name: 'age_75_79', required: true, align: 'left', label: '75-79', field: 'age_75_79', sortable: true},
      {name: 'age_80_84', required: true, align: 'left', label: '80-84', field: 'age_80_84', sortable: true},
      {name: 'age_85_89', required: true, align: 'left', label: '85-89', field: 'age_85_89', sortable: true},
      {name: 'age_90_94', required: true, align: 'left', label: '90-94', field: 'age_90_94', sortable: true},
      {name: 'age_95_99', required: true, align: 'left', label: '95-99', field: 'age_95_99', sortable: true},
      {name: 'age_100_over', required: true, align: 'left', label: '100+', field: 'age_100_over', sortable: true},
    ]
    this.rows = this.population
  }
}
</script>

<style scoped>
</style>
