loader.addModule('map', 'B', 'graph', function (B, graph) {
	"use strict";

	/**
	 * Module to manage the game map
	 */

	var cellDimensions = 10;

	/**
	 * Map construct. Build the level, set the objects and the frame information
	 */
	function Map (mapData) {
		var map = {
			graph: graph(mapData)
		};

		map.update = function () {

		};

		map.draw = function (camera) {
			map.graph.draw(camera, cellDimensions);
		};

		return map;
	}

	return Map;
});
