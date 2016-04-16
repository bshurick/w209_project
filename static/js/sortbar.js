
// eventually read data automatically via .csv function

var sortbar = function(data, location, button) {

  function change() {
    clearTimeout(sortTimeout);

    // Copy-on-write since tweens are evaluated after a delay.
    var x0 = x.domain(data.sort(this.checked
        ? function(a, b) { return b.Weighted_Pct - a.Weighted_Pct; }
        : function(a, b) { return d3.ascending(a.Category, b.Category); })
        .map(function(d) { return d.Category; }))
        .copy();

    svg.selectAll('.bar_chart2')
        .sort(function(a, b) { return x0(a.Category) - x0(b.Category); });

    var transition = svg.transition().duration(750),
        delay = function(d, i) { return i * 50; };

    transition.selectAll('.bar_chart2')
        .delay(delay)
        .attr("x", function(d) { return x0(d.Category); });

    transition.select(".x.axis")
        .call(xAxis)
      .selectAll("g")
        .delay(delay);
  }

var margin = {top: 20, right: 20, bottom: 20, left: 50},
    width = 900- margin.left - margin.right,
    height = 350 - margin.top - margin.bottom;

var formatPercent = d3.format(".0%");

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1, 1);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(formatPercent);

var svg = d3.select(location).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    data.forEach(function(d) {
    d.Weighted_Pct = +d.Weighted_Pct;
  });

  x.domain(data.map(function(d) { return d.Category; }));
  // y.domain([0, d3.max(data, function(d) { return d.Weighted_Pct; })]);
  y.domain([0, 1]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Weighted_Pct");

  svg.selectAll(location)
      .data(data)
    .enter().append("rect")
      .attr("class", "bar_chart2")
      .attr("x", function(d) { return x(d.Category); })
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.Weighted_Pct); })
      .attr("height", function(d) { return height - y(d.Weighted_Pct); });

  d3.select(button).on("change", change);

  var sortTimeout = setTimeout(function() {
    d3.select(button).property("checked", true).each(change);
  }, 2000);

}
