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
				x: Math.random() * surfaceW,
				y: Math.random() * surfaceH
			});
			nbNodes--;
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

		graph.draw = function (camera) {
			canvasContext.beginPath();
			graph.nodes.forEach(function (node) {
				var coords = camera.adapt(node);
				canvasContext.moveTo(coords.x, coords.y);
				canvasContext.arc(coords.x, coords.y, 5, 0, 2 * Math.PI, false);
			});
			canvasContext.fill();
		};

		return graph;
	}

	return Graph;
});
