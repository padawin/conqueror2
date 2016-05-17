loader.addModule('graph',
'canvas', 'B',
function (canvas, B) {
	"use strict";

	/**
	 * Module to manage the game map
	 */

	var canvasContext = canvas.getContext();

	function generate (graph, nbNodes, surfaceW, surfaceH) {
		while (nbNodes > 0) {
			graph.nodes.push({
				x: Math.floor(Math.random() * surfaceW),
				y: Math.floor(Math.random() * surfaceH)
			});
			nbNodes--;
		}

		graph.nodes.sort(function (a, b) {
			if (a.x < b.x || a.x == b.x && a.y < b.y) {
				return -1;
			}
			else if (a.x > b.x || a.x == b.x && a.y > b.y) {
				return 1;
			}
			else {
				return 0;
			}
		});
	}

	function generateDelaunay (graph, start, end) {
		if (end - start >= 3) {
			return [].concat(
				generateDelaunay(graph, start, start + Math.floor((end - start) / 2)),
				generateDelaunay(graph, start + Math.floor((end - start) / 2) + 1, end)
			);
		}
		else if (end - start == 2) {
			return [
				[graph.nodes[start], graph.nodes[start + 1]],
				[graph.nodes[start + 1], graph.nodes[start + 2]],
				[graph.nodes[start + 2], graph.nodes[start]]
			];

		}
		else {
			return [
				[graph.nodes[start], graph.nodes[start + 1]]
			];
		}
	}

	/**
	 * Map construct. Build the level, set the objects and the frame information
	 */
	function Graph (nbNodes, surfaceW, surfaceH) {
		var graph = {
			nodes: [],
			edges: []
		};

		generate(graph, nbNodes, surfaceW, surfaceH);
		graph.edges = generateDelaunay(graph, 0, nbNodes - 1);

		graph.draw = function (camera) {
			canvasContext.beginPath();
			graph.nodes.forEach(function (node) {
				var coords = camera.adapt(node);
				canvasContext.moveTo(coords.x, coords.y);
				canvasContext.arc(coords.x, coords.y, 5, 0, 2 * Math.PI, false);
			});
			graph.edges.forEach(function (edge) {
				var coordsStart = camera.adapt(edge[0]),
					coordsEnd = camera.adapt(edge[1]);
				canvasContext.moveTo(coordsStart.x, coordsStart.y);
				canvasContext.lineTo(coordsEnd.x, coordsEnd.y);
			});
			canvasContext.stroke();
			canvasContext.fill();
		};

		return graph;
	}

	return Graph;
});
