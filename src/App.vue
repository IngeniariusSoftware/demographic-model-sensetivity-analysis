<template>
  <PopulationTable :population="Population"/>
</template>

<script>
import PopulationTable from './components/PopulationTable.vue'
import Population from "@/assets/data";

export default {
  name: 'App',
  data() {
    return {Population}
  },
  components: {
    PopulationTable
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
