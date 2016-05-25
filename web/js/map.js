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

		map.click = function (playerId, coords) {
			coords = pixelsToCoords(coords);
			var node = map.graph.getNode(coords),
				neighbours,
				nbAlliedNeighbours = 0, nbEnemyNeighbours = 0;

			if (node && node.owned_by === null) {
				neighbours = map.graph.getNeighbours(coords);
				neighbours.forEach(function (neighbour) {
					var neighbour = map.graph.getNode(neighbour);
					if (neighbour.owned_by !== null) {
						if (neighbour.owned_by === playerId) {
							nbAlliedNeighbours++;
						}
						else {
							nbEnemyNeighbours++;
						}
					}
				});

				return nbAlliedNeighbours > nbEnemyNeighbours ? coords : null;
			}

			return null;
		};

		map.draw = function (camera) {
			map.graph.draw(camera, cellDimensions);
		};

		return map;
	}

	return Map;
});
