<template>
  <div>
    <div class="unselectable" style="align-self: stretch; display: flex; margin-left: 5px; margin-right: 8px">
      <a style="text-align: start; inline-size: 60px; font-size: 12px; overflow-wrap: break-word">{{
          labeledAxis.y
        }}</a>
      <label style="margin: auto;">{{ title }}</label>
    </div>
    <div :id="containerID"/>
    <div class="unselectable" style="align-self: stretch; display: flex; margin-top: 5px">
      <div style="margin-left: 42%; margin-right: auto">
        <label v-for="(color, label) in labeledColors" :key="label">
          <div class="circleLegend" :style="`background: ${color}`"/>
          <label class="labelLegend unselectable">{{ label }}</label>
        </label>
      </div>
      <a style="margin-right:15px; text-align: end; inline-size: 80px; font-size: 12px; overflow-wrap: break-word">{{
          labeledAxis.x
        }}</a>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'LineChart',
  data() {
    return {
      scale: {x: Object, y: Object},
      axis: {x: Object, y: Object},
      grid: {x: Object, y: Object},
    }
  },
  computed: {
    visibleAreaID() {
      return `${this.containerID}VisibleDefs`
    },
    visibleGroupID() {
      return `${this.containerID}VisibleGroup`
    }
  },
  props: {
    title: {type: String, required: true},
    containerID: {type: String, required: true},
    labeledData: {type: Object, required: true},
    labeledColors: {type: Object, required: true},
    labeledAxis: {type: Object, required: true},
    margin: {type: Object, required: true},
    width: {type: Number, required: true},
    height: {type: Number, required: true},
    tickNumber: {type: Number, required: true},
  },
  mounted() {
    const innerWidth = this.width - this.margin.left - this.margin.right
    const innerHeight = this.height - this.margin.top - this.margin.bottom
    const data = Object.values(this.labeledData).reduce((result, d) => result.concat(d), [])
    const group = this.createSVG(this.width, this.height, this.margin)
    this.addZoom(data, group, innerWidth, innerHeight, 1, 20)
    const result = this.addAxes(data, group, innerWidth, innerHeight, this.tickNumber)
    this.scale = result.scale
    this.axis = result.axis
    this.grid = result.grid
    const visibleArea = this.addVisibleArea(group, innerWidth, innerHeight)
    this.addLines(this.labeledData, this.labeledColors, visibleArea, this.scale.x, this.scale.y)
  },
  methods: {
    createSVG(width, height, margin) {
      return d3.select(`#${this.containerID}`)
          .append('svg')
          .attr('width', width)
          .attr('height', height)
          .append('g')
          .attr('transform', `translate(${margin.left}, ${margin.top})`)
    },
    addZoom(data, group, width, height, minZoom, maxZoom) {
      const zoom = d3.zoom()
          .scaleExtent([minZoom, maxZoom])
          .translateExtent([[0, 0], [this.width, this.height]])
          .on('zoom', this.onZoomChanged)

      group.append('rect')
          .attr('width', width)
          .attr('height', height)
          .style('fill', 'none')
          .style('pointer-events', 'all')
          .call(zoom)
    },
    onZoomChanged(event) {
      //const scaleX = event.transform.rescaleX(this.scale.x)
      const scaleY = event.transform.rescaleY(this.scale.y)
      //this.grid.x.call(this.generateGridX(scaleX, this.height, this.tickNumber))
      //this.axis.x.call(d3.axisBottom(scaleX))
      this.grid.y.call(this.generateGridY(scaleY, this.width, this.tickNumber))
      this.axis.y.call(d3.axisLeft(scaleY))
      const visibleGroup = d3.select(`#${this.visibleGroupID}`)
      visibleGroup.selectAll('circle')
          .attr('cx', d => this.scale.x(d.x))
          .attr('cy', d => scaleY(d.y))
      visibleGroup.selectAll('path')
          .attr('d', d3.line().x(d => this.scale.x(d.x)).y(d => scaleY(d.y)))
    },
    addVisibleArea(group, width, height) {
      group.append('defs')
          .append('clipPath')
          .attr('id', this.visibleAreaID)
          .append('rect')
          .attr('width', width)
          .attr('height', height)
          .attr('x', 0)
          .attr('y', 0)
      return group.append('g')
          .attr('id', this.visibleGroupID)
          .attr('clip-path', `url(#${this.visibleAreaID}`)
    },
    addAxes(data, group, width, height, tickNumber) {
      const [scaleX, axisX, gridX] = this.addAxisX(data, group, width, height, tickNumber)
      const [scaleY, axisY, gridY] = this.addAxisY(data, group, width, height, tickNumber)
      return {scale: {x: scaleX, y: scaleY}, axis: {x: axisX, y: axisY}, grid: {x: gridX, y: gridY}}
    },
    addAxisX(data, group, width, height, tickNumber) {
      const scaleX = d3.scalePoint()
          .domain(data.map(d => d.x))
          .range([0, width])

      const gridX = group.append('g')
          .attr('transform', `translate(0, ${height})`)
          .call(this.generateGridX(scaleX, height, tickNumber))
          .attr('stroke-opacity', 0.15)

      const axisX = group.append('g')
          .attr('transform', `translate(0, ${height})`)
          .call(d3.axisBottom(scaleX))
          .attr('class', 'unselectable')

      return [scaleX, axisX, gridX]
    },
    generateGridX(scaleX, height, tickNumber) {
      return d3.axisBottom(scaleX)
          .ticks(tickNumber)
          .tickFormat('')
          .tickSize(-height, 0)
    },
    addAxisY(data, group, width, height, tickNumber) {
      const scaleY = d3.scaleLinear()
          .domain(this.expandExtent(d3.extent(data.map(d => d.y)), 0.05))
          .range([height, 0])

      const gridY = group.append('g')
          .call(this.generateGridY(scaleY, width, tickNumber))
          .attr('stroke-opacity', 0.15)

      const axisY = group.append('g')
          .call(d3.axisLeft(scaleY))
          .attr('font-size', '15px')
          .attr('class', 'unselectable')
      return [scaleY, axisY, gridY]
    },
    generateGridY(scaleY, width, tickNumber) {
      return d3.axisLeft(scaleY)
          .ticks(tickNumber)
          .tickFormat('')
          .tickSize(-width, 0)
    },
    expandExtent(extent, percentage) {
      const expandValue = (extent[1] - extent[0]) * percentage * 0.5
      return [extent[0] - expandValue, extent[1] + expandValue]
    },
    addLines(labeledData, labeledColors, group, scaleX, scaleY) {
      const dotRadius = 3
      const tooltip = this.addTooltip()
      for (const [label, data] of Object.entries(labeledData)) {
        const color = labeledColors[label]
        const lineGroup = group.append('g')
        lineGroup.append('path')
            .datum(data)
            .attr('fill', 'none')
            .attr('stroke', color)
            .attr('class', 'path')
            .attr('stroke-width', 2)
            .attr('d', d3.line().x(d => scaleX(d.x)).y(d => scaleY(d.y)))
            .attr('class', 'unselectable')
        this.addDots(data, lineGroup, scaleX, scaleY, dotRadius, color)
        this.addTooltipDots(group, tooltip, data, dotRadius * 3, scaleX, scaleY)
      }
    },
    addDots(data, group, scaleX, scaleY, radius, color) {
      group.append('g')
          .selectAll('dots')
          .data(data)
          .enter()
          .append('circle')
          .attr('cx', d => scaleX(d.x))
          .attr('cy', d => scaleY(d.y))
          .attr('r', radius)
          .attr('fill', 'white')
          .attr('stroke', color)
          .attr('stroke-width', '1.5px')
    },
    addTooltipDots(group, tooltip, data, radius, scaleX, scaleY) {
      group.append('g')
          .selectAll('tooltipDots')
          .data(data)
          .enter()
          .append('circle')
          .attr('cx', d => scaleX(d.x))
          .attr('cy', d => scaleY(d.y))
          .attr('r', radius)
          .attr('fill', 'transparent')
          .style('pointer-select', 'none')
          .on('mouseover', () => tooltip.transition().duration(200).style('opacity', 1))
          .on('mousemove', (event, d) => {
            tooltip.html(`${this.labeledAxis.y}: ${d.y}<br/>${this.labeledAxis.x}: ${d.x}`)
                .style('left', `${event.layerX + 20}px`)
                .style('top', `${event.layerY - 5}px`)
          })
          .on('mouseout', () => tooltip.transition().duration(200).style('opacity', 0))
    },
    addTooltip() {
      return d3.select(`#${this.containerID}`)
          .append('div')
          .attr('class', 'unselectable')
          .style('opacity', 0)
          .style('background-color', 'white')
          .style('border', 'solid')
          .style('border-width', '2px')
          .style('border-radius', '5px')
          .style('padding', '5px')
          .style('position', 'absolute')
    }
  }
}
</script>

<style>
.labelLegend {
  margin-right: 15px;
}

.circleLegend {
  margin-right: 5px;
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #1D1D1D;
}
</style>