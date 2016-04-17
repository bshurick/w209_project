
var linechart = function(target) {
	function make_y_axis() {
	    return d3.svg.axis()
		.scale(y)
		.orient("left")
		//.ticks(10)
	}

	var formatPercent = d3.format(".0%");

	var margin = {top: 20, right: 160, bottom: 30, left: 60},
	    width = 850 - margin.left - margin.right,
	    height = 500 - margin.top - margin.bottom;

	var x = d3.time.scale()
	    .range([0, width]);

	var y = d3.scale.linear()
	    .range([height, 0]);

	var color = d3.scale.category10();

	var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom");

	var yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left")
	    .tickFormat(formatPercent);

	var line = d3.svg.line()
	    .interpolate("basis")
	    .x(function(d) { return x(d.date); })
	    .y(function(d) { return y(d.violence); });

	var svg = d3.select(target).append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var parseDate = d3.time.format("%Y").parse;

	d3.csv("/static/RPD_SHI_Q_9.csv", function(error, data) {

	  if (error) throw error;
	  console.log(data)

	  color.domain(d3.keys(data[0]).filter(function(key) { return key !== "date"; }));

	  data.forEach(function(d) {
	    d.date = parseDate(d.date);
	  });

	  var regions = color.domain().map(function(name) {
	    return {
	      name: name,
	      values: data.map(function(d) {
		return {date: d.date, violence: +d[name]};
	      })
	    };
	  });

	  x.domain(d3.extent(data, function(d) { return d.date; }));

	  y.domain([
	    d3.min(regions, function(c) { return 0 }),
	    d3.max(regions, function(c) { return 1 })
	  ]);

	  svg.append("g")
	      .attr("class", "x axis")
	      .attr("transform", "translate(0," + height + ")")
	      .call(xAxis);

	  svg.append("g")
	      .attr("class", "grid")
	      .call(make_y_axis()
		  .tickSize(-width, 0, 0)
		  .tickFormat("")
	      )

	  //.text(function(d) {
	  //    return "Value = " + formatPercent(d.value)
	  //}

	  svg.append("g")
	      .attr("class", "y axis")
	      .call(yAxis)
	    .append("text")
	      .attr("transform", "translate(0,-20)")
	      .attr("y", 6)
	      .attr("dy", "1em")
	      .style("text-anchor", "right")
	      .text("% of countries, by region");

	  var region = svg.selectAll(".region")
	      .data(regions)
	    .enter().append("g")
	      .attr("class", "region");

	  region.append("path")
	      .attr("class", "line")
	      .attr("d", function(d) { return line(d.values); })
	      .style("stroke", function(d) { return color(d.name); })

	      // append a title element for a tooltip
	      // give hint to browser, whether tooltip should be for path, bar, or any element displayed
	      // browser takes care of interactivity, so developer loses flexibility
	      /*
	      .append("title")
		  .text(function(d) {
		  return "Value is " + y(d.values);
		});
	      */

	  region.append("text")
	      .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
	      .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.violence) + ")"; })
	      .attr("x", 3)
	      .attr("dy", ".35em")
	      .text(function(d) { return d.name; });

	});
}
