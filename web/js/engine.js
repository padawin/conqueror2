loader.executeModule('main',
'B', 'canvas', 'camera', 'screenSize', 'map', 'graph',
function (B, canvas, camera, screenSize, map, graph) {
	"use strict";

	/**
	 * Main module of the game, manage the game loop.
	 */

	var debug = false,
		m,
		timePreviousFrame,
		maxFPS = 60,
		interval = 1000 / maxFPS,

		// used in debug mode
		lastCalledTime,
		fpsAccu,
		fps;

	/**
	 * Method to adapt the canvas dimensions to the screen and the camera to the
	 * canvas
	 */
	function resize (dimensions) {
		canvas.resize(dimensions);
		camera.w = canvas.getWidth();
		camera.h = canvas.getHeight();
	}

	/**
	 * Main draw method. Draws the sky, the map and its objects
	 */
	function draw () {
		canvas.canvas.width = canvas.getWidth();
		m.draw(camera, debug);
	}

	/**
	 * Method called at each frame of the game. Updates all the entities and
	 * then draw them.
	 */
	function mainLoop () {
		requestAnimationFrame(mainLoop);
		var now = Date.now(),
			delta = now - timePreviousFrame;

		// cap the refresh to a defined FPS
		if (delta > interval) {
			timePreviousFrame = now - (delta % interval);

			// calculate current fps in debug mode only
			if (debug) {
				delta = now - lastCalledTime;
				if (delta > 1000) {
					lastCalledTime = now;
					fps = fpsAccu;
					fpsAccu = 0;
				}
				else {
					fpsAccu++;
				}
			}

			m.update();
			camera.update();
			draw();
		}
	}

	function initEvents () {
		/**
		 * Event fired when the mouse is moved with the left button pressed
		 */
		B.Events.on('mousedrag', null, function (vectorX, vectorY) {
			camera.setPosition({x: camera.x - vectorX, y: camera.y - vectorY});
			camera.setSubject();
		});

		/**
		 * Event fired when the mouse is clicked
		 */
		B.Events.on('click', null, function (mouseX, mouseY) {
		});
	}

	/**
	 * Entry point of the game. Initialises the map, plugs the event and does a
	 * certain amount of mess. @TODO To be refactored
	 */
	function startGame () {
		resize(screenSize.get());

		/**
		 * Event fired when the window is resized
		 */
		B.Events.on('resize', null, resize);

		initEvents();
		timePreviousFrame = Date.now();
		lastCalledTime = Date.now();
		fpsAccu = 0;

		m = map(graph(500, 2000, 2000));
		camera.setPosition({x: 700, y: 500});
		mainLoop();
	}

	startGame();
});
