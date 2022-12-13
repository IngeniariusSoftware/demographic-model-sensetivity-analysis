<template>
  <div :id="containerID.replace('#', '')"/>
</template>

<script>
import * as d3 from 'd3'

const componentName = 'Treemap'

export default {
  name: componentName,
  data() {
    return {
      rootGroup: Selection,
      titleText: Selection,
      treemap: Selection,
      treemapRoot: Selection,
    }
  },
  props: {
    title: {type: String, required: true},
    id: {type: String, required: true},
    data: {type: Object, required: true},
    labeledColors: {type: Object, required: true},
    margin: {type: Object, required: true},
    width: {type: Number, required: true},
    height: {type: Number, required: true},
    transitionDuration: {type: Number, required: false, default: 1000},
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
      return this.data.reduce((result, [, data]) => result.concat(data), [])
    },
  },
  watch: {
    data() {
      this.updateLineChart()
    },
    title() {
      this.titleText.text(this.title)
    }
  },
  mounted() {
    this.rootGroup = addRootGroup(this.containerID, this.width, this.height, this.margin)
    this.titleText = addTitle(this.rootGroup, this.title, this.innerWidth, this.height, this.margin)
    this.treemap = addTreemap(this.innerWidth, this.innerHeight)
    this.treemapRoot = addRootToTreemap(this.treemap, this.data)
    addTreeNodes(this.rootGroup, this.treemapRoot, this.labeledColors, 0)
  },
  methods: {
    updateLineChart() {
      this.treemapRoot = addRootToTreemap(this.treemap, this.data)
      addTreeNodes(this.rootGroup, this.treemapRoot, this.labeledColors, this.transitionDuration)
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

function addTreemap(width, height) {
  return d3.treemap()
      .size([width, height])
      .padding(4)
      .round(true);
}

function addRootToTreemap(treemap, data) {
  let root = d3.stratify().parentId(d => d.parentID)(data)
  root.sum(d => d.value)
      .sort((a, b) => b.height - a.height || b.value - a.value)
  treemap(root)
  return root
}

function addTreeNodes(group, root, labeledColors, duration) {
  const treemapGroupID = '#treemap'
  let treemapGroupSelection = group.selectAll(treemapGroupID).data([root])
  treemapGroupSelection.enter()
      .append('g')
      .attr('id', treemapGroupID.replace('#', ''))
      .classed('unselectable', true)
      .style('pointer-select', 'none')
  treemapGroupSelection.exit().remove()

  treemapGroupSelection = group.selectAll(treemapGroupID)
  addTreeRects(treemapGroupSelection, root, labeledColors, duration)
  addTreeRectsLabels(treemapGroupSelection, root, duration)
  addTreeRectsValues(treemapGroupSelection, root, duration)
}

function addTreeRects(groups, root, labeledColors, duration) {
  const rectsGroupID = '#rects'
  let rectsGroupsSelection = groups.selectAll(rectsGroupID).data([root])
  rectsGroupsSelection.enter()
      .append('g')
      .attr('id', rectsGroupID.replace('#', ''))
  rectsGroupsSelection.exit().remove()

  rectsGroupsSelection = groups.selectAll(rectsGroupID)
  const rectsSelection = rectsGroupsSelection.selectAll('rect').data(root.leaves())
  rectsSelection.enter()
      .append('rect')
      .style('stroke', 'black')
      .merge(rectsSelection)
      .transition()
      .duration(duration)
      .style('fill', d => labeledColors[d.data.parentID])
      .attr('x', d => d.x0)
      .attr('y', d => d.y0)
      .attr('width', d => d.x1 - d.x0)
      .attr('height', d => d.y1 - d.y0)
  rectsSelection.exit().remove()
}

function addTreeRectsLabels(groups, root, duration) {
  const labelsGroupID = '#labels'
  let labelsGroupsSelection = groups.selectAll(labelsGroupID).data([root])
  labelsGroupsSelection.enter()
      .append('g')
      .attr('id', labelsGroupID.replace('#', ''))
  labelsGroupsSelection.exit().remove()

  labelsGroupsSelection = groups.selectAll(labelsGroupID)
  const labelsSelection = labelsGroupsSelection.selectAll('text').data(root.leaves())
  labelsSelection.enter()
      .append('text')
      .attr('fill', 'white')
      .style('white-space', 'pre-line')
      .merge(labelsSelection)
      .text(d => d.data.id)
      .transition()
      .duration(duration)
      .attr('font-size', d => fontSize(d))
      .attr('x', d => (d.x0 + (d.x1 - d.x0) * 0.03))
      .attr('y', d => d.y0 + ((d.y1 - d.y0) * 0.03) + fontSize(d))
  labelsSelection.exit().remove()
}

function addTreeRectsValues(groups, root, duration) {
  const valuesGroupID = '#values'
  let valuesGroupsSelection = groups.selectAll(valuesGroupID).data([root])
  valuesGroupsSelection.enter()
      .append('g')
      .attr('id', valuesGroupID.replace('#', ''))
  valuesGroupsSelection.exit().remove()

  valuesGroupsSelection = groups.selectAll(valuesGroupID)
  const valuesSelection = valuesGroupsSelection.selectAll('text').data(root.leaves())
  valuesSelection.enter()
      .append('text')
      .attr('fill', 'white')
      .merge(valuesSelection)
      .text(d => d.value.toFixed(3))
      .transition()
      .duration(duration)
      .attr('font-size', d => fontSize(d) * 0.9)
      .attr('x', d => (d.x0 + (d.x1 - d.x0) * 0.03))
      .attr('y', d => d.y0 + ((d.y1 - d.y0) * 0.03) + fontSize(d) * 2.2)
  valuesSelection.exit().remove()
}

function fontSize(d) {
  return 100 * (1.0 - (1.0 / (1.0 + (3.0 * d.value))))
}

</script>

<style>
</style>