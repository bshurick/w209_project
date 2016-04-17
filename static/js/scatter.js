
var scatterplot = function(data, target) {

	var margin = {top: 20, right: 20, bottom: 30, left: 40},
    	width = 850 - margin.left - margin.right,
    	height = 350 - margin.top - margin.bottom;
	
	// setup x 
	var xValue = function(d) { return Math.round(d.score*100); }, // data -> value
	    xScale = d3.scale.linear().range([0, width]), // value -> display
	    xMap = function(d) { return xScale(xValue(d)); }, // data -> display
	    xAxis = d3.svg.axis().scale(xScale).orient("bottom");

	// setup y
	var yValue = function(d) { return Math.round(d.disagree_score*100); }, // data -> value
	    yScale = d3.scale.linear().range([height, 0]), // value -> display
	    yMap = function(d) { return yScale(yValue(d)); }, // data -> display
	    yAxis = d3.svg.axis().scale(yScale).orient("left");
	
	// setup fill color
	var cValue = function(d) { return d.state; },
    	color = d3.scale.category20();
	
	var totalValue = function(d) { return Math.round(+d.total); };

	var svg = d3.select(target).append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var tooltip = d3.tip()
	    .attr("class", "tooltip")
	    .offset([-10,0])	
		.html(function(d) {
			return "<strong>" + d.state + "</strong><br/> (Agree: " + xValue(d) +
                        "%, Disagree: " + yValue(d) + "%)<br/># Responses: " + totalValue(d);
		});
	 svg.call(tooltip);
	
	  // don't want dots overlapping axis, so add in buffer to data domain
	  xScale.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
	  yScale.domain([d3.min(data, yValue)-1, d3.max(data, yValue)+1]);

	  // x-axis
	  svg.append("g")
	      .attr("class", "x axis")
	      .attr("transform", "translate(0," + height + ")")
	      .call(xAxis)
	    .append("text")
	      .attr("class", "label")
	      .attr("x", width)
	      .attr("y", -6)
	      .style("text-anchor", "end")
	      .text("% Agreed");

	  // y-axis
	  svg.append("g")
	      .attr("class", "y axis")
	      .call(yAxis)
	    .append("text")
	      .attr("class", "label")
	      .attr("transform", "rotate(-90)")
	      .attr("y", 6)
	      .attr("dy", ".71em")
	      .style("text-anchor", "end")
	      .text("% Disagreed");

	  // draw dots
	  svg.selectAll(".dot")
	      .data(data)
	    .enter().append("circle")
	      .attr("class", "dot")
	      .attr("r", function(d) { return Math.sqrt(totalValue(d)) + 'px' } )
	      .attr("cx", xMap)
	      .attr("cy", yMap)
	      .style("fill", function(d) { return color(cValue(d));}) 
	      .on("mouseover", tooltip.show)
	      .on("mouseout", tooltip.hide);
	  
}
