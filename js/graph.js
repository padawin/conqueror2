loader.addModule('graph',
'canvas', 'B',
function (canvas, B) {
	"use strict";

	/**
	 * Module to manage the game map
	 */

	var canvasContext = canvas.getContext();

	/**
	 * Map construct. Build the level, set the objects and the frame information
	 */
	function Graph (nbNodes) {
		var graph = {};

		graph.draw = function (camera) {

		};

		return graph;
	}

	return Graph;
});
