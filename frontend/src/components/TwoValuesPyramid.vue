<template>
  <div :id="containerID.replace('#', '')"/>
</template>

<script>
import * as d3 from 'd3'

const componentName = 'TwoValuesPyramid'

export default {
  name: componentName,
  data() {
    return {
      axes: {leftX: Selection, rightX: Selection, y: Selection},
      rootGroup: Selection,
      titleText: Selection,
      pointersRect: Selection,
      tooltipRect: undefined,
      tooltipLabels: {left: Selection, right: Selection},
      dataLabels: {left: Selection, right: Selection},
      dataIndex: 0,
      formatPercentage: (d) => `${d}%`
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
    tickNumberPercentages: {type: Number, required: false, default: undefined},
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
      const leftScaleX = d3.scaleLinear()
          .domain(expandMaxExtent(d3.extent(this.dataXY.map(d => d.percentage)), 0.15))
          .range([this.innerWidth * 0.5, 0])
          .nice()
      const rightScaleX = d3.scaleLinear()
          .domain(expandMaxExtent(d3.extent(this.dataXY.map(d => d.percentage)), 0.15))
          .range([this.innerWidth * 0.5, this.innerWidth])
          .nice()
      const scaleY = d3.scaleBand()
          .domain(this.dataXY.map(d => d.x))
          .range([this.innerHeight, 0])
          .padding(0.06)
      return {leftX: leftScaleX, rightX: rightScaleX, y: scaleY}
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
    const axesX = addAxesX(this.rootGroup, this.scales.leftX, this.scales.rightX, this.innerWidth, this.innerHeight,
        this.margin.bottom, this.labeledAxes.x, this.formatPercentage, this.tickNumberPercentages)
    this.axes.leftX = axesX.left
    this.axes.rightX = axesX.right
    this.axes.y = addAxisY(this.rootGroup, this.scales.y, this.innerWidth, this.innerHeight, this.margin.left, this.labeledAxes.y, this.formatX, this.tickNumberX)
    this.titleText = addTitle(this.rootGroup, this.title, this.innerWidth, this.height, this.margin)
    this.pointersRect = addPointersRect(this.rootGroup, this.innerWidth, this.innerHeight)
    addLeftRightBars(this.rootGroup, this.scales, this.labeledData, this.labeledColors, 0)
    this.tooltipRect = addTooltipRect(this.rootGroup, this.innerWidth)
    this.tooltipLabels = addTooltipLabels(this.rootGroup, this.scales.rightX, this.labeledColors)
    bindTooltipRectWithLabels(this.pointersRect, this.tooltipRect, this.tooltipLabels, this.scales.y, this.margin.top,
        this.formatY, this.labeledData[0][1], this.labeledData[1][1], this.dataIndex, (i) => this.dataIndex = i)
    this.dataLabels = addDataLabels(this.rootGroup, this.innerWidth, this.margin.top, this.labeledData, this.labeledColors)
  },
  methods: {
    updateLineChart() {
      this.axes.leftX.transition().duration(this.transitionDuration).call(axisBottom(this.scales.leftX, this.formatPercentage, this.tickNumberPercentages))
      this.axes.rightX.transition().duration(this.transitionDuration).call(axisBottom(this.scales.rightX, this.formatPercentage, this.tickNumberPercentages))
      this.axes.y.transition().duration(this.transitionDuration).call(axisLeft(this.scales.y, this.formatX, this.tickNumberPercentages))
      addLeftRightBars(this.rootGroup, this.scales, this.labeledData, this.labeledColors, this.transitionDuration)
      bindTooltipRectWithLabels(this.pointersRect, this.tooltipRect, this.tooltipLabels, this.scales.y, this.margin.top,
          this.formatY, this.labeledData[0][1], this.labeledData[1][1], this.dataIndex, (i) => this.dataIndex = i)
      updateDataLabels(this.dataLabels, this.labeledData, this.labeledColors)
    },
  }
}

function addPointersRect(group, width, height) {
  return group.append('rect')
      .attr('width', width)
      .attr('height', height)
      .classed('pointersRect', true)
}

function expandMaxExtent(extent, percentage) {
  const expandValue = (extent[1] - extent[0]) * percentage
  return [extent[0], extent[1] + expandValue]
}

function addRootGroup(containerID, width, height, margin) {
  return d3.select(containerID)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
}

function addAxesX(group, leftScaleX, rightScaleX, width, height, marginBottom, labelX, tickFormatX, tickNumber) {
  const leftAxisX = group.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(axisBottom(leftScaleX, tickFormatX, tickNumber))
      .attr('class', 'unselectable')

  const rightAxisX = group.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(axisBottom(rightScaleX, tickFormatX, tickNumber))
      .attr('class', 'unselectable')

  rightAxisX.append('text')
      .attr('x', width)
      .attr('y', marginBottom - 2)
      .attr('fill', 'black')
      .attr('text-anchor', 'end')
      .text(`${labelX}`)

  return {left: leftAxisX, right: rightAxisX}
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

function addAxisY(group, scaleY, width, height, marginLeft, labelY, tickFormatX, tickNumberX) {
  const axisY = group.append('g')
      .call(axisLeft(scaleY, tickFormatX, tickNumberX))
      .attr('class', 'unselectable')

  axisY.append('text')
      .attr('x', -marginLeft)
      .attr('y', -9)
      .attr('fill', 'black')
      .attr('text-anchor', 'start')
      .text(`↑ ${labelY}`)

  return axisY
}

function axisLeft(scale, tickFormat, tickNumber) {
  let axis = d3.axisLeft(scale)
  if (tickFormat) {
    axis = axis.tickFormat(tickFormat)
  }
  if (tickNumber) {
    axis = axis.ticks(tickNumber)
  }

  return axis
}

function addTitle(group, title, innerWidth) {
  return group.append('text')
      .attr('x', innerWidth * 0.5)
      .attr('y', -7)
      .classed('unselectable charTitle', true)
      .text(title)
}

function addLeftRightBars(group, scales, labeledData, labeledColors, duration) {
  const overData = [[], []]
  const labeledOverData = []
  labeledOverData.push([labeledData[0][0], overData[0]])
  labeledOverData.push([labeledData[1][0], overData[1]])
  labeledData[0][1].forEach((d, i) => {
    const overPercentage = d.percentage - labeledData[1][1][i].percentage
    overData[0].push({x: d.x, percentage: d.percentage, overPercentage: overPercentage > 0 ? overPercentage : 0})
    overData[1].push({
      x: labeledData[1][1][i].x,
      percentage: labeledData[1][1][i].percentage,
      overPercentage: overPercentage < 0 ? -overPercentage : 0
    })
  })

  for (let [i, direction] of [[0, 'left'], [1, 'right']]) {
    addBars(group, scales, [labeledData[i]], labeledColors, direction, duration)
    addOverBars(group, scales, [labeledOverData[i]], labeledColors, direction, duration)
    addBarsLabels(group, scales, [labeledData[i]], labeledColors, direction, duration)
  }
}

function addBars(group, scales, labeledData, labeledColors, direction, duration) {
  const barsGroupID = `#${direction}Bars`
  let barsGroupSelection = group.selectAll(barsGroupID).data(labeledData)
  barsGroupSelection.enter()
      .append('g')
      .attr('id', barsGroupID.replace('#', ''))
      .attr('fill', ([label,]) => labeledColors[label])
  barsGroupSelection.exit().remove()

  barsGroupSelection = group.selectAll(barsGroupID).data(labeledData)
  const barsSelection = barsGroupSelection.selectAll('rect').data(([, data]) => data)
  barsSelection.enter()
      .append('rect')
      .classed('unselectable', true)
      .merge(barsSelection)
      .transition()
      .duration(duration)
      .attr('width', d => scales.rightX(d.percentage) - scales.rightX(0))
      .attr('height', scales.y.bandwidth())
      .attr('x', d => direction === 'left' ? scales.leftX(d.percentage) - 0.2 : scales.rightX(0) + 0.2)
      .attr('y', d => scales.y(d.x))
  barsSelection.exit().remove()
}

function addBarsLabels(group, scales, labeledData, labeledColors, direction, duration) {
  const barsLabelsGroupID = `#${direction}BarsLabels`
  let barsLabelsGroupSelection = group.selectAll(barsLabelsGroupID).data(labeledData)
  barsLabelsGroupSelection.enter()
      .append('g')
      .attr('id', barsLabelsGroupID.replace('#', ''))
      .attr('fill', ([label,]) => labeledColors[label])
      .attr('font-size', '11x')
  barsLabelsGroupSelection.exit().remove()

  barsLabelsGroupSelection = group.selectAll(barsLabelsGroupID).data(labeledData)
  const barLabelsSelection = barsLabelsGroupSelection.selectAll('text').data(([, data]) => data)
  barLabelsSelection.enter()
      .append('text')
      .classed('unselectable', true)
      .style('text-anchor', direction === 'left' ? 'end' : 'start')
      .merge(barLabelsSelection)
      .transition()
      .duration(duration)
      .attr('x', d => direction === 'left' ? scales.leftX(d.percentage) - 3 : scales.rightX(d.percentage) + 3)
      .attr('y', d => scales.y(d.x) + scales.y.bandwidth() * 0.65)
      .text(d => `${d.percentage.toFixed(1)}%`)
  barLabelsSelection.exit().remove()
}

function addOverBars(group, scales, labeledData, labeledColors, direction, duration) {
  const overBarsGroupID = `#${direction}OverBars`
  let overBarsGroupSelection = group.selectAll(overBarsGroupID).data(labeledData)
  overBarsGroupSelection.enter()
      .append('g')
      .attr('id', overBarsGroupID.replace('#', ''))
      .attr('fill', ([label,]) => labeledColors[`over${label}`])
  overBarsGroupSelection.exit().remove()

  overBarsGroupSelection = group.selectAll(overBarsGroupID).data(labeledData)
  const overBarsSelection = overBarsGroupSelection.selectAll('rect').data(([, data]) => data)
  overBarsSelection.enter()
      .append('rect')
      .classed('unselectable', true)
      .merge(overBarsSelection)
      .transition()
      .duration(duration)
      .attr('width', d => scales.rightX(d.overPercentage) - scales.rightX(0))
      .attr('height', scales.y.bandwidth())
      .attr('x', d => direction === 'left' ? scales.leftX(d.percentage) - 0.2 : scales.rightX(d.percentage - d.overPercentage) + 0.2)
      .attr('y', d => scales.y(d.x))
  overBarsSelection.exit().remove()
}

function addTooltipRect(group, width) {
  return group.append('rect')
      .attr('x', 1)
      .attr('width', width - 2)
      .classed('unselectable tooltipRect', true)
}

function addTooltipLabels(group, rightScale, colors) {
  const left = addTooltipLabel(group, rightScale, Object.values(colors)[0], 'left')
  const right = addTooltipLabel(group, rightScale, Object.values(colors)[1], 'right')
  return {left, right}
}

function addTooltipLabel(group, rightScale, color, direction) {
  return group.append('text')
      .attr('x', direction === 'left' ? rightScale(0) - 6 : rightScale(0) + 6)
      .attr('y', 0)
      .attr('opacity', 0)
      .attr('fill', color)
      .style('text-anchor', direction === 'left' ? 'end' : 'start')
      .classed('unselectable', true)
}

function bindTooltipRectWithLabels(pointersRect, rect, labels, scaleY, biasY, formatY, leftData, rightData, dataIndex, onMouseMove) {
  labels.left.text(formatY ? formatY(leftData[dataIndex].y) : leftData[dataIndex].y)
  labels.right.text(formatY ? formatY(rightData[dataIndex].y) : leftData[dataIndex].y)
  pointersRect.on('mouseover', () => {
    rect.style('opacity', 1)
        .attr('height', scaleY.step())
    labels.left.style('opacity', 1)
    labels.right.style('opacity', 1)
  })
      .on('mousemove', (event) => {
        const i = d3.max([0, Math.round((event.layerY - biasY) / scaleY.step()) - 1])
        const dataIndex = leftData.length - i - 1
        onMouseMove(dataIndex)
        rect.attr('y', scaleY.step() * i)

        labels.left.text(formatY ? formatY(leftData[dataIndex].y) : leftData[dataIndex].y)
            .attr('y', (scaleY.step() * i) + (scaleY.step() * 0.7))

        labels.right.text(formatY ? formatY(rightData[dataIndex].y) : leftData[dataIndex].y)
            .attr('y', (scaleY.step() * i) + (scaleY.step() * 0.7))
      })
      .on('mouseout', () => {
        rect.style('opacity', 0)
        labels.left.style('opacity', 0)
        labels.right.style('opacity', 0)
      })
}

function addDataLabels(group, width, marginTop, labeledData, labeledColors) {
  const leftLabel = addDataLabel(group, width, marginTop, 'left')
  const rightLabel = addDataLabel(group, width, marginTop, 'right')
  const labels = {left: leftLabel, right: rightLabel}
  updateDataLabels(labels, labeledData, labeledColors)
  return labels
}

function addDataLabel(group, width, marginTop, direction) {
  return group.append('text')
      .attr('y', marginTop + 20)
      .attr('x', direction === 'left' ? width * 0.2 : width * 0.8)
      .classed('unselectable dataLabel', true)
}

function updateDataLabels(labels, labeledData, labeledColors) {
  labels.left.style('fill', labeledColors[labeledData[0][0]])
      .text(labeledData[0][0])
  labels.right.style('fill', labeledColors[labeledData[1][0]])
      .text(labeledData[1][0])
}
</script>

<style>
.tooltipRect {
  opacity: 0;
  fill: white;
}

.dataLabel {
  text-anchor: middle;
  font-size: 25px;
}
</style>