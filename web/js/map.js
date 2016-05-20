loader.addModule('map', 'B', function (canvas, B) {
	"use strict";

	/**
	 * Module to manage the game map
	 */

	var cellDimensions = 10;

	/**
	 * Map construct. Build the level, set the objects and the frame information
	 */
	function Map (graph) {
		var map = {
			graph: graph
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
