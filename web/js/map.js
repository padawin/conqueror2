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

		/**
		* Convert a set of pixels in the map projection and returns the coordinates
		* of the cell in the grid
		*/
		function pixelsToCoords (coords) {
			return {
				x: ~~(coords.x / cellDimensions),
				y: ~~(coords.y / cellDimensions)
			};
		}

		map.click = function (coords) {
			coords = pixelsToCoords(coords);
			console.log(map.graph.getNode(coords));
		};

		map.draw = function (camera) {
			map.graph.draw(camera, cellDimensions);
		};

		return map;
	}

	return Map;
});
