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
			var owner;
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

			graph.edges.forEach(function (edge) {
				var coordsStart = camera.adapt(
						adaptCoordToGridCellSize(edge[0], gridCellSize)
					),
					coordsEnd = camera.adapt(
						adaptCoordToGridCellSize(edge[1], gridCellSize)
					);
				canvasContext.moveTo(coordsStart.x, coordsStart.y);
				canvasContext.lineTo(coordsEnd.x, coordsEnd.y);
			});
			canvasContext.stroke();
		};

		graph.getNode = function (coords) {
			if (graph.nodesGrid[coords.x]) {
				return graph.nodesGrid[coords.x][coords.y];
			}
			return null;
		};

		return graph;
	}

	return Graph;
});
