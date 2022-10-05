<template>
  <div>
    <div :id="containerID.replace('#', '')"/>
    <div class="unselectable flex justify-center" :style="`padding-left: ${margin.left}px; margin-top: -20px`">
      <div v-for="(color, label) in labeledColors" :key="label">
        <div class="legendColorCircle" :style="`background: ${color}`"/>
        <label class="unselectable legendLabel">{{ label }}</label>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'

const componentName = 'LineChart'

export default {
  name: componentName,
  data() {
    return {
      axes: {x: Selection, y: Selection},
      grid: {x: Selection, y: Selection},
      rootGroup: Selection,
      visibleGroup: Selection,
      tooltipLabel: undefined,
      pointersRect: undefined,
      rawSelectedX: Number,
      tooltipLines: {horizontal: undefined, vertical: Selection},
      tooltipLineLabels: {horizontalX: Selection, horizontalY: Selection}
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
    transitionDuration: {type: Number, required: false, default: 1000},
    tickNumberX: {type: Number, required: false, default: undefined},
    tickNumberY: {type: Number, required: false, default: undefined},
    showGrid: {type: Boolean, required: false, default: true},
    showDots: {type: Boolean, required: false, default: true},
    dotsRadius: {type: Number, required: false, default: 3},
    tickFormatX: {type: Function, required: false, default: undefined},
    tooltipType: {type: String, required: false, default: 'dots'},
    selectedX: {type: Number, required: false},
    zoom: {
      type: Object, required: false, default: () => {
        return {min: 1, max: 10}
      }
    }
  },
  computed: {
    containerID() {
      return `#${componentName}Container${this.id}`
    },
    visibleAreaID() {
      return `#${componentName}VisibleDefs${this.id}`
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
      return this.labeledData.reduce((result, [, data]) => result.concat(data), [])
    },
    firstDatumXY() {
      return this.labeledData[0][1]
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
      this.updateLineChart(this.scales, this.transitionDuration, this.selectedX)
    },
    selectedX() {
      this.addTooltip(this.scales, this.selectedX, this.transitionDuration)
    }
  },
  mounted() {
    this.rootGroup = addRootGroup(this.containerID, this.width, this.height, this.margin)
    if (this.showGrid) {
      this.grid.x = addGridX(this.rootGroup, this.scales.x, this.innerHeight, this.tickNumberX)
      this.grid.y = addGridY(this.rootGroup, this.scales.y, this.innerWidth, this.tickNumberY)
    }
    this.axes.x = addAxisX(this.rootGroup, this.scales.x, this.innerWidth, this.innerHeight, this.margin.bottom, this.labeledAxes.x, this.tickFormatX, this.tickNumberX)
    this.axes.y = addAxisY(this.rootGroup, this.scales.y, this.innerWidth, this.innerHeight, this.margin.left, this.labeledAxes.y, this.tickNumberY)
    addLegend(this.rootGroup, this.title, this.innerWidth, this.height, this.margin)
    this.addZoom(this.rootGroup, this.width, this.height, this.innerWidth, this.innerHeight, this.zoom.min, this.zoom.max)
    this.visibleGroup = addVisibleGroup(this.rootGroup, this.visibleAreaID, this.innerWidth, this.innerHeight)
    addLines(this.visibleGroup, this.scales, this.labeledData, this.labeledColors, 0)
    if (this.showDots) {
      addDots(this.visibleGroup, this.scales, this.labeledData, this.labeledColors, this.dotsRadius, 0)
    }
    this.addTooltip(this.scales, this.selectedX)
  },
  methods: {
    addZoom(group, width, height, innerWidth, innerHeight, minZoom, maxZoom) {
      const zoom = d3.zoom()
          .scaleExtent([minZoom, maxZoom])
          .translateExtent([[0, 0], [width, height]])
          .on('zoom', this.onZoomChanged)

      this.pointersRect = group.append('rect')
          .attr('width', innerWidth)
          .attr('height', innerHeight)
          .classed('pointersRect', true)
          .call(zoom)
    },
    onZoomChanged(event) {
      const scaleX = event.transform.rescaleX(this.scales.x)
      const scaleY = event.transform.rescaleY(this.scales.y)
      this.updateLineChart({x: scaleX, y: scaleY}, 0, this.rawSelectedX)
    },
    updateLineChart(scales, transitionDuration, currentX) {
      this.axes.x.transition().duration(transitionDuration).call(axisBottom(scales.x, this.tickFormatX, this.tickNumberX))
      this.axes.y.transition().duration(transitionDuration).call(axisLeft(scales.y, this.tickNumberY))

      if (this.showGrid) {
        this.grid.x.call(generateGridX(scales.x, this.innerHeight, this.tickNumberX))
        this.grid.y.call(generateGridY(scales.y, this.innerWidth, this.tickNumberY))
      }

      addLines(this.visibleGroup, scales, this.labeledData, this.labeledColors, transitionDuration)

      if (this.showDots) {
        addDots(this.visibleGroup, scales, this.labeledData, this.labeledColors, this.dotsRadius, transitionDuration)
      }

      this.addTooltip(scales, currentX, transitionDuration);
    },
    addTooltip(scales, currentX, transitionDuration) {
      if (this.tooltipType === 'dots') {
        if (!this.tooltipLabel) {
          this.tooltipLabel = addTooltipLabel(this.containerID)
        }
        addTooltipDots(this.visibleGroup, this.tooltipLabel, scales, this.labeledData, this.labeledColors, this.labeledAxes, this.tooltipDotRadius)
      } else if (this.tooltipType === 'lines') {
        if (!this.tooltipLines.horizontal) {
          this.tooltipLines = addTooltipLines(this.visibleGroup, this.innerWidth, this.innerHeight)
          this.tooltipLineLabels = addTooltipLineLabels(this.visibleGroup, this.innerWidth)
        }
        bindTooltipRectWithLines(this.pointersRect, this.tooltipLines, this.tooltipLineLabels, scales, this.margin.left + 8, this.firstDatumXY,
            (x) => this.rawSelectedX = x, (d) => this.$emit('xSelected', d.x), () => this.selectedX, currentX, transitionDuration)
      } else {
        console.warn(`Wrong tooltip type value: ${this.tooltipType}`)
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

function generateGridX(scaleX, height, tickNumber) {
  let grid = d3.axisBottom(scaleX)
      .tickFormat('')
      .tickSize(-height, 0)
  if (tickNumber) {
    grid = grid.ticks(tickNumber)
  }

  return grid
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

function axisBottom(scaleX, tickFormatX, tickNumber) {
  let axis = d3.axisBottom(scaleX)
  if (tickFormatX) {
    axis = axis.tickFormat(tickFormatX)
  }
  if (tickNumber) {
    axis = axis.ticks(tickNumber)
  }

  return axis
}

function addGridY(group, scaleY, width, tickNumber) {
  return group.append('g')
      .call(generateGridY(scaleY, width, tickNumber))
      .attr('stroke-opacity', 0.15)
}

function generateGridY(scaleY, width, tickNumber) {
  let grid = d3.axisLeft(scaleY)
      .tickFormat('')
      .tickSize(-width, 0)
  if (tickNumber) {
    grid = grid.ticks(tickNumber)
  }

  return grid
}

function addAxisY(group, scaleY, width, height, marginLeft, labelY, tickNumber) {
  const axisY = group.append('g')
      .call(axisLeft(scaleY, tickNumber))
      .attr('class', 'unselectable')

  axisY.append('text')
      .attr('x', -marginLeft)
      .attr('y', -9)
      .attr('fill', 'black')
      .attr('text-anchor', 'start')
      .text(`↑ ${labelY}`)

  return axisY
}

function axisLeft(scaleY, tickNumber) {
  let axis = d3.axisLeft(scaleY)
  if (tickNumber) {
    axis = axis.ticks(tickNumber)
  }

  return axis
}

function addLegend(group, title, innerWidth) {
  group.append('text')
      .attr('x', innerWidth * 0.5)
      .attr('y', -7)
      .classed('unselectable charTitle', true)
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
  const pathSelection = group.selectAll('path').data(labeledData)
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
  let dotsGroupsSelection = group.selectAll(dotsGroupID).data(labeledData)
  dotsGroupsSelection.enter()
      .append('g')
      .attr('id', dotsGroupID.replace('#', ''))
      .attr('stroke-width', '1.5px')
      .attr('stroke', ([label,]) => labeledColors[label])
      .attr('fill', 'white')
  dotsGroupsSelection.exit().remove()

  dotsGroupsSelection = group.selectAll(dotsGroupID).data(labeledData)
  const dotsSelection = dotsGroupsSelection.selectAll('circle').data(([, data]) => {
    return data
  })
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

function addTooltipDots(group, tooltip, scales, labeledData, labeledColors, labeledAxis, radius) {
  const tooltipDotsGroupID = '#tooltipDots'
  let tooltipDotsGroupSelection = group.selectAll(tooltipDotsGroupID).data(labeledData)
  tooltipDotsGroupSelection.enter()
      .append('g')
      .attr('id', tooltipDotsGroupID.replace('#', ''))
      .attr('fill', 'transparent')
      .style('pointer-select', 'none')
  tooltipDotsGroupSelection.exit().remove()

  tooltipDotsGroupSelection = group.selectAll(tooltipDotsGroupID).data(labeledData)
  const tooltipDotsSelection = tooltipDotsGroupSelection.selectAll('circle').data(([label, data]) => data.map(d => {
    return {x: d.x, y: d.y, color: labeledColors[label]}
  }))
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
            .style('border-color', d.color)
      })
      .on('mouseout', () => tooltip.transition().duration(200).style('opacity', 0))
  tooltipDotsSelection.exit().remove()
}

function addTooltipLabel(id) {
  return d3.select(id)
      .append('div')
      .classed('unselectable tooltipLabel', true)
}

function addTooltipLines(group, width, height) {
  const groupLines = group.append('g')
      .classed('strokeLinesGroup', true)
  const horizontal = appendLine(groupLines, 0, 100, width, 100)
  const vertical = appendLine(groupLines, 100, 0, 100, height)
  return {horizontal, vertical}
}

function appendLine(group, x1, y1, x2, y2) {
  return group.append('line')
      .attr('x1', x1)
      .attr('y1', y1)
      .attr('x2', x2)
      .attr('y2', y2)
}

function addTooltipLineLabels(group, width) {
  const groupLabels = group.append('g')
  const horizontalLabelX = groupLabels.append('text')
      .style('text-anchor', 'end')
      .attr('x', width - 5)
  const horizontalLabelY = groupLabels.append('text')
      .style('text-anchor', 'end')
      .attr('x', width - 5)
  return {horizontalX: horizontalLabelX, horizontalY: horizontalLabelY}
}

function bindTooltipRectWithLines(rect, lines, labels, scales, biasX, data, onMouseMove, onClick, selectedXFunc, currentX, transitionDuration) {
  arrangeTooltipLines(lines, labels, scales, getDatumFromX(data, currentX), transitionDuration)
  rect.on('mousemove', (event) => {
    onMouseMove(getDatumFromMouseX(scales.x, event.layerX, data, biasX).x)
    arrangeTooltipLines(lines, labels, scales, getDatumFromMouseX(scales.x, event.layerX, data, biasX))
  })
      .on('click', (event) => onClick(getDatumFromMouseX(scales.x, event.layerX, data, biasX)))
      .on('mouseout', () => arrangeTooltipLines(lines, labels, scales, getDatumFromX(data, selectedXFunc())))
}

function getDatumFromMouseX(scaleX, mouseX, data, biasX) {
  const rawX = scaleX.invert(mouseX - biasX)
  return getDatumFromX(data, rawX)
}

function getDatumFromX(data, rawX) {
  const i = d3.bisector(d => d.x).center(data, rawX)
  return data[i]
}

function arrangeTooltipLines(lines, labels, scales, data, transitionDuration = 0) {
  lines.horizontal
      .transition()
      .duration(transitionDuration)
      .attr('y1', scales.y(data.y))
      .attr('y2', scales.y(data.y))
  lines.vertical
      .transition()
      .duration(transitionDuration)
      .attr('x1', scales.x(data.x))
      .attr('x2', scales.x(data.x))
  labels.horizontalY
      .transition()
      .duration(transitionDuration)
      .attr('y', scales.y(data.y) - 7)
      .text(data.y)
  labels.horizontalX
      .transition()
      .duration(transitionDuration)
      .attr('y', scales.y(data.y) + 18)
      .text(data.x)

}
</script>

<style>
.legendLabel {
  margin-right: 10px;
  font-size: 14px;
}

.legendColorCircle {
  margin-right: 5px;
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #1D1D1D;
}

.tooltipLabel {
  opacity: 0;
  background-color: white;
  border: 2px solid;
  border-radius: 5px;
  padding: 5px;
  position: absolute;
  z-index: 100;
}

.strokeLinesGroup {
  stroke-dasharray: 1 2;
  stroke-width: 1px;
  pointer-events: none;
  stroke: black;
}
</style>