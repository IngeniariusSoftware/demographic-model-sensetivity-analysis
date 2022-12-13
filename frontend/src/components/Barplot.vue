<template>
  <div :id="containerID.replace('#', '')"/>
  <div class="unselectable flex justify-center" :style="`padding-left: ${margin.left}px; margin-top: -20px`">
    <div v-for="(color, label) in labeledColors" :key="label">
      <div class="legendColorCircle" :style="`background: ${color}`"/>
      <label class="unselectable legendLabel">{{ label }}</label>
    </div>
  </div>
</template>


<script>
import * as d3 from 'd3'

const componentName = 'Barplot'

export default {
  name: componentName,
  data() {
    return {
      axes: {x: Selection, y: Selection},
      rootGroup: Selection,
      titleText: Selection,
    }
  },
  props: {
    title: {type: String, required: true},
    id: {type: String, required: true},
    labeledData: {type: Object, required: true},
    labeledColors: {type: Object, required: true},
    margin: {type: Object, required: true},
    width: {type: Number, required: true},
    height: {type: Number, required: true},
    labeledAxes: {type: Object, required: true},
    transitionDuration: {type: Number, required: false, default: 1000},
    tickNumberX: {type: Number, required: false, default: undefined},
    tickNumberY: {type: Number, required: false, default: undefined},
    formatX: {type: Function, required: false, default: undefined},
    formatY: {type: Function, required: false, default: undefined},
  },
  computed: {
    containerID() {
      return `#${componentName}Container${this.id}`
    },
    innerWidth() {
      return this.width - this.margin.left - this.margin.right
    },
    innerHeight() {
      return this.height - this.margin.top - this.margin.bottom
    },
    dataXY() {
      return this.labeledData.reduce((result, [, data]) => result.concat(data), [])
    },
    scales() {
      const scaleX = d3.scaleBand()
          .range([this.innerWidth, 0])
          .domain(this.dataXY.map(d => d.x))
          .padding(0.2)
      const scaleY = d3.scaleLinear()
          .domain(d3.extent(this.dataXY.map(d => d.y).concat(0)))
          .range([this.innerHeight, 0])
      return {x: scaleX, y: scaleY}
    },
  },
  watch: {
    labeledData() {
      this.updateLineChart()
    },
    title() {
      this.titleText.text(this.title)
    }
  },
  mounted() {
    this.rootGroup = addRootGroup(this.containerID, this.width, this.height, this.margin)
    this.titleText = addTitle(this.rootGroup, this.title, this.innerWidth, this.height, this.margin)
    this.axes.x = addAxisX(this.rootGroup, this.scales.x, this.innerWidth, this.innerHeight, this.margin.bottom, this.labeledAxes.x, this.formatX, this.tickNumberX)
    this.axes.y = addAxisY(this.rootGroup, this.scales.y, this.innerWidth, this.innerHeight, this.margin.left, this.labeledAxes.y, this.formatY, this.tickNumberY)
    addBars(this.rootGroup, this.scales, this.labeledData, this.labeledColors, 0)
  },
  methods: {
    updateLineChart() {
      this.axes.x.transition().duration(this.transitionDuration).call(axisBottom(this.scales.x, this.formatX, this.tickNumberX))
      this.axes.y.transition().duration(this.transitionDuration).call(axisLeft(this.scales.y, this.formatY, this.tickNumberY))
      addBars(this.rootGroup, this.scales, this.labeledData, this.labeledColors, this.transitionDuration)
    },
  }
}

function addRootGroup(containerID, width, height, margin) {
  return d3.select(containerID)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
}

function addTitle(group, title, innerWidth) {
  return group.append('text')
      .attr('x', innerWidth * 0.5)
      .attr('y', -7)
      .classed('unselectable charTitle', true)
      .text(title)
}

function addAxisX(group, scaleX, width, height, marginBottom, labelX, tickFormatX, tickNumber) {
  const axisX = group.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(axisBottom(scaleX, tickFormatX, tickNumber))
      .attr('class', 'unselectable')

  axisX.append('text')
      .attr('x', width)
      .attr('y', marginBottom - 2)
      .attr('fill', 'black')
      .attr('text-anchor', 'end')
      .text(`${labelX} →`)

  return axisX
}

function axisLeft(scaleY, tickFormatY, tickNumber) {
  let axis = d3.axisLeft(scaleY)
  if (tickFormatY) {
    axis = axis.tickFormat(tickFormatY)
  }
  if (tickNumber) {
    axis = axis.ticks(tickNumber)
  }

  return axis
}

function axisBottom(scale, tickFormat, tickNumber) {
  let axis = d3.axisBottom(scale)
  if (tickFormat) {
    axis = axis.tickFormat(tickFormat)
  }
  if (tickNumber) {
    axis = axis.ticks(tickNumber)
  }

  return axis
}


function addAxisY(group, scaleY, width, height, marginLeft, labelY, tickFormatY, tickNumber) {
  const axisY = group.append('g')
      .call(axisLeft(scaleY, tickFormatY, tickNumber))
      .attr('class', 'unselectable')

  axisY.append('text')
      .attr('x', -marginLeft)
      .attr('y', -9)
      .attr('fill', 'black')
      .attr('text-anchor', 'start')
      .text(`↑ ${labelY}`)

  return axisY
}

function addBars(group, scales, labeledData, labeledColors, duration) {
  const barsGroupID = '#bars'
  let barsGroupsSelection = group.selectAll(barsGroupID).data(labeledData)
  barsGroupsSelection.enter()
      .append('g')
      .attr('id', barsGroupID.replace('#', ''))
      .attr('fill', d => labeledColors[d[0]])
  barsGroupsSelection.exit().remove()

  barsGroupsSelection = group.selectAll(barsGroupID)
  const barsSelection = barsGroupsSelection.selectAll('rect').data(([, data]) => data)
  barsSelection.enter()
      .append('rect')
      .merge(barsSelection)
      .transition()
      .duration(duration)
      .attr('x', d => scales.x(d.x))
      .attr('width', scales.x.bandwidth())
      .attr('height', d => scales.y(0) - scales.y(d.y))
      .attr('y', d => scales.y(d.y))
  barsSelection.exit().remove()
}

</script>

<style>
</style>