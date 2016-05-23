loader.addModule('graph',
'canvas', 'B',
function (canvas, B) {
	"use strict";

	/**
	 * Module to manage the game map
	 */

	var canvasContext = canvas.getContext(),
		ownershipColors = {
			'-1': 'black',
			'0': 'red',
			'1': 'green'
		};

	/**
	 * Map construct. Build the level, set the objects and the frame information
	 */
	function Graph (data) {
		var graph = {
			nodesGrid: data.nodesGrid,
			nodes: data.nodes,
			edges: data.edges
		};

		function adaptCoordToGridCellSize (coord, gridCellSize) {
			return {
				x: coord.x * gridCellSize + gridCellSize / 2,
				y: coord.y * gridCellSize + gridCellSize / 2
			}
		}

		graph.draw = function (camera, gridCellSize) {
			var owner, e, start;
			canvasContext.beginPath();
			for (e in graph.edges) {
				start = JSON.parse(e);
				graph.edges[e].forEach(function (end) {
					// edges contains all the edges in both ways, we
					// need do draw only half of them. let's so draw
					// only those starting with the smallest coordinates
					if (start.x < end.x || start.x == end.x && start.y < end.y) {
						var coordsStart = camera.adapt(
								adaptCoordToGridCellSize(start, gridCellSize)
							),
							coordsEnd = camera.adapt(
								adaptCoordToGridCellSize(end, gridCellSize)
							);
						canvasContext.moveTo(coordsStart.x, coordsStart.y);
						canvasContext.lineTo(coordsEnd.x, coordsEnd.y);
					}
				});
			}
			canvasContext.stroke();

			graph.nodes.forEach(function (node) {
				var coords = camera.adapt(
					adaptCoordToGridCellSize(node, gridCellSize)
				);

				canvasContext.beginPath();
				canvasContext.moveTo(coords.x, coords.y);
				owner = graph.nodesGrid[node.x][node.y]['owned_by'];
				canvasContext.fillStyle = ownershipColors[
					owner === null ? '-1' : owner
				];
				canvasContext.arc(coords.x, coords.y, gridCellSize / 2, 0, 2 * Math.PI, false);
				canvasContext.fill();
			});
		};

		graph.getNode = function (coords) {
			if (graph.nodesGrid[coords.x]) {
				return graph.nodesGrid[coords.x][coords.y];
			}
			return null;
		};

		graph.getNeighbours = function (coords) {
			var node = graph.getNode(coords);
			if (!node) {
				return null;
			}

			var key = JSON.stringify({x: coords.x, y: coords.y});
			return graph.edges[key];
		};

		return graph;
	}

	return Graph;
});
