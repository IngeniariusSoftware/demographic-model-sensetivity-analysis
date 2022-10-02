<template>
  <div>
    <div :id="containerID.replace('#', '')"/>
    <div class="unselectable flex justify-center" :style="`padding-left: ${margin.left}px; margin-top: -20px`">
      <div v-for="(color, label) in labeledColors" :key="label">
        <div class="circleLegend" :style="`background: ${color}`"/>
        <label class="unselectable labelLegend">{{ label }}</label>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'LineChart',
  data() {
    return {
      axes: {x: Object, y: Object},
      grid: {x: Object, y: Object},
      rootGroup: Selection,
      visibleGroup: Selection,
      tooltipLabel: undefined,
      tooltipLines: {horizontal: undefined, vertical: undefined},
      dotsRadius: 3
    }
  },
  props: {
    title: {type: String, required: true},
    id: {type: String, required: true},
    labeledData: {type: Object, required: true},
    labeledColors: {type: Object, required: true},
    labeledAxes: {type: Object, required: true},
    margin: {type: Object, required: true},
    width: {type: Number, required: true},
    height: {type: Number, required: true},
    transitionDuration: {type: Number, required: true},
    tickNumber: {type: Number, required: false, default: 10},
    showGrid: {type: Boolean, required: false, default: true},
    tickFormatX: {type: Function, required: false, default: undefined},
    tooltipType: {type: String, required: false, default: 'dots'}
  },
  computed: {
    containerID() {
      return `#lineChartContainer${this.id}`
    },
    visibleAreaID() {
      return `#lineChartVisibleDefs${this.id}`
    },
    innerWidth() {
      return this.width - this.margin.left - this.margin.right
    },
    innerHeight() {
      return this.height - this.margin.top - this.margin.bottom
    },
    tooltipDotRadius() {
      return this.dotsRadius * 3
    },
    dataXY() {
      return Object.values(this.labeledData).reduce((result, d) => result.concat(d), [])
    },
    scales() {
      const scaleX = d3.scaleLinear()
          .domain(expandExtent(d3.extent(this.dataXY.map(d => d.x)), 0.1))
          .range([0, this.innerWidth])
      const scaleY = d3.scaleLinear()
          .domain(expandExtent(d3.extent(this.dataXY.map(d => d.y)), 0.1))
          .range([this.innerHeight, 0])
      return {x: scaleX, y: scaleY}
    },
  },
  watch: {
    labeledData() {
      this.updateLineChart(this.scales, this.transitionDuration)
    }
  },
  mounted() {
    this.rootGroup = addRootGroup(this.containerID, this.width, this.height, this.margin)
    if (this.showGrid) {
      this.grid.x = addGridX(this.rootGroup, this.scales.x, this.innerHeight, this.tickNumber)
      this.grid.y = addGridY(this.rootGroup, this.scales.y, this.innerWidth, this.tickNumber)
    }
    this.axes.x = addAxisX(this.rootGroup, this.scales.x, this.innerWidth, this.innerHeight, this.margin.bottom, this.labeledAxes.x, this.tickFormatX)
    this.axes.y = addAxisY(this.rootGroup, this.scales.y, this.innerWidth, this.innerHeight, this.margin.left, this.labeledAxes.y)
    addLegend(this.rootGroup, this.title, this.innerWidth, this.height, this.margin)
    this.addZoom(this.rootGroup, this.width, this.height, this.innerWidth, this.innerHeight, 1, 20)
    this.visibleGroup = addVisibleGroup(this.rootGroup, this.visibleAreaID, this.innerWidth, this.innerHeight)
    addLines(this.visibleGroup, this.scales, this.labeledData, this.labeledColors, 0)
    addDots(this.visibleGroup, this.scales, this.labeledData, this.labeledColors, this.dotsRadius, 0)
    this.addTooltip(this.scales)
  },
  methods: {
    addZoom(group, width, height, innerWidth, innerHeight, minZoom, maxZoom) {
      const zoom = d3.zoom()
          .scaleExtent([minZoom, maxZoom])
          .translateExtent([[0, 0], [width, height]])
          .on('zoom', this.onZoomChanged)

      group.append('rect')
          .attr('width', innerWidth)
          .attr('height', innerHeight)
          .style('fill', 'none')
          .style('pointer-events', 'all')
          .style('stroke-width', '0.1px')
          .style('stroke', 'black')
          .call(zoom)
    },
    onZoomChanged(event) {
      const scaleX = event.transform.rescaleX(this.scales.x)
      const scaleY = event.transform.rescaleY(this.scales.y)
      this.updateLineChart({x: scaleX, y: scaleY}, 0)
    },
    updateLineChart(scales, transitionDuration) {
      this.axes.x.transition().duration(transitionDuration).call(axisBottom(scales.x, this.tickFormatX))
      this.axes.y.transition().duration(transitionDuration).call(d3.axisLeft(scales.y))

      if (this.showGrid) {
        this.grid.x.call(generateGridX(scales.x, this.innerHeight, this.tickNumber))
        this.grid.y.call(generateGridY(scales.y, this.innerWidth, this.tickNumber))
      }

      addLines(this.visibleGroup, scales, this.labeledData, this.labeledColors, transitionDuration)
      addDots(this.visibleGroup, scales, this.labeledData, this.labeledColors, this.dotsRadius, transitionDuration)
      this.addTooltip(scales);
    },
    addTooltip(scales) {
      if (this.tooltipType === 'dots') {
        if (!this.tooltipLabel) {
          this.tooltipLabel = addTooltipLabel(this.containerID)
        }
        addTooltipDots(this.visibleGroup, this.tooltipLabel, scales, this.labeledData, this.labeledAxes, this.tooltipDotRadius)
      } else {
        // addTooltipLine(this.visibleGroup)
      }
    }
  }
}

function expandExtent(extent, percentage) {
  const expandValue = (extent[1] - extent[0]) * percentage * 0.5
  return [extent[0] - expandValue, extent[1] + expandValue]
}

function addRootGroup(containerID, width, height, margin) {
  return d3.select(containerID)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
}

function addGridX(group, scaleX, height, tickNumber) {
  return group.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(generateGridX(scaleX, height, tickNumber))
      .attr('stroke-opacity', 0.15)
}

function addAxisX(group, scaleX, width, height, marginBottom, labelX, tickFormatX) {
  const axisX = group.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(axisBottom(scaleX, tickFormatX))
      .attr('class', 'unselectable')

  axisX.append('text')
      .attr('x', width)
      .attr('y', marginBottom - 2)
      .attr('fill', 'black')
      .attr('text-anchor', 'end')
      .text(`${labelX} →`)

  return axisX
}

function axisBottom(scaleX, tickFormatX) {
  return tickFormatX ? d3.axisBottom(scaleX).tickFormat(tickFormatX) : d3.axisBottom(scaleX)
}

function generateGridX(scaleX, height, tickNumber) {
  return d3.axisBottom(scaleX)
      .ticks(tickNumber)
      .tickFormat('')
      .tickSize(-height, 0)
}

function addGridY(group, scaleY, width, tickNumber) {
  return group.append('g')
      .call(generateGridY(scaleY, width, tickNumber))
      .attr('stroke-opacity', 0.15)
}

function addAxisY(group, scaleY, width, height, marginLeft, labelY) {
  const axisY = group.append('g')
      .call(d3.axisLeft(scaleY))
      .attr('class', 'unselectable')

  axisY.append('text')
      .attr('x', -marginLeft)
      .attr('y', -9)
      .attr('fill', 'black')
      .attr('text-anchor', 'start')
      .text(`↑ ${labelY}`)

  return axisY
}

function generateGridY(scaleY, width, tickNumber) {
  return d3.axisLeft(scaleY)
      .ticks(tickNumber)
      .tickFormat('')
      .tickSize(-width, 0)
}

function addLegend(group, title, innerWidth) {
  group.append('text')
      .attr('x', innerWidth * 0.5)
      .attr('y', -7)
      .attr('fill', 'black')
      .attr('text-anchor', 'middle')
      .attr('font-weight', '600')
      .attr('class', 'unselectable')
      .text(title)
}

function addVisibleGroup(group, id, width, height) {
  group.append('defs')
      .append('clipPath')
      .attr('id', id.replace('#', ''))
      .append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('x', 0)
      .attr('y', 0)

  return group.append('g')
      .attr('clip-path', `url(${id})`)
}

function addLines(group, scales, labeledData, labeledColors, duration) {
  const pathSelection = group.selectAll('path').data(Object.entries(labeledData))
  pathSelection.enter()
      .append('path')
      .attr('fill', 'none')
      .attr('stroke-width', 2)
      .attr('class', 'unselectable')
      .merge(pathSelection)
      .attr('stroke', ([label,]) => labeledColors[label])
      .datum(([, data]) => data)
      .transition()
      .duration(duration)
      .attr('d', d3.line().x(d => scales.x(d.x)).y(d => scales.y(d.y)))
  pathSelection.exit().remove()
}

function addDots(group, scales, labeledData, labeledColors, radius, duration) {
  const dotsGroupID = '#dots'
  let dotsGroupsSelection = group.selectAll(dotsGroupID).data(Object.entries(labeledData))
  dotsGroupsSelection.enter()
      .append('g')
      .attr('id', dotsGroupID.replace('#', ''))
      .attr('stroke-width', '1.5px')
      .attr('stroke', ([label,]) => labeledColors[label])
      .attr('fill', 'white')
      .attr('stroke-width', '1.5px')
  dotsGroupsSelection.exit().remove()

  dotsGroupsSelection = group.selectAll(dotsGroupID).data(Object.entries(labeledData))
  const dotsSelection = dotsGroupsSelection.selectAll('circle').data(([, data]) => data)
  dotsSelection.enter()
      .append('circle')
      .merge(dotsSelection)
      .attr('r', radius)
      .transition()
      .duration(duration)
      .attr('cx', d => scales.x(d.x))
      .attr('cy', d => scales.y(d.y))
  dotsSelection.exit().remove()
}

function addTooltipDots(group, tooltip, scales, labeledData, labeledAxis, radius) {
  const tooltipDotsGroupID = '#tooltipDots'
  let tooltipDotsGroupSelection = group.selectAll(tooltipDotsGroupID).data(Object.entries(labeledData))
  tooltipDotsGroupSelection.enter()
      .append('g')
      .attr('id', tooltipDotsGroupID.replace('#', ''))
      .attr('fill', 'transparent')
      .style('pointer-select', 'none')
  tooltipDotsGroupSelection.exit().remove()

  tooltipDotsGroupSelection = group.selectAll(tooltipDotsGroupID).data(Object.entries(labeledData))
  const tooltipDotsSelection = tooltipDotsGroupSelection.selectAll('circle').data(([, data]) => data)
  tooltipDotsSelection.enter()
      .append('circle')
      .attr('r', radius)
      .merge(tooltipDotsSelection)
      .attr('cx', d => scales.x(d.x))
      .attr('cy', d => scales.y(d.y))
      .on('mouseover', () => tooltip.transition().duration(200).style('opacity', 1))
      .on('mousemove', (event, d) => {
        tooltip.html(`${labeledAxis.y}: ${d.y}<br/>${labeledAxis.x}: ${d.x}`)
            .style('left', `${event.layerX + 20}px`)
            .style('top', `${event.layerY - 5}px`)
      })
      .on('mouseout', () => tooltip.transition().duration(200).style('opacity', 0))
  tooltipDotsSelection.exit().remove()
}

function addTooltipLabel(id) {
  return d3.select(id)
      .append('div')
      .attr('class', 'unselectable')
      .style('opacity', 0)
      .style('background-color', 'white')
      .style('border', 'solid')
      .style('border-width', '2px')
      .style('border-radius', '5px')
      .style('padding', '5px')
      .style('position', 'absolute')
      .style('z-index', '100')
}
//
// function addTooltipLine(group, width, height) {
//   group.append('rect')
//       .attr('width', width)
//       .attr('height', height)
//       .style('fill', 'none')
//       .style('pointer-events', 'all')
//       .on('mousemove', (event, d) => {
//         tooltip.html(`${labeledAxis.y}: ${d.y}<br/>${labeledAxis.x}: ${d.x}`)
//             .style('left', `${event.layerX + 20}px`)
//             .style('top', `${event.layerY - 5}px`)
//       })
// }
//
// function addTooltipRect(group, width, height) {
//
// }


</script>

<style>
.labelLegend {
  margin-right: 10px;
  font-size: 14px;
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