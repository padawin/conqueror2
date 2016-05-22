loader.executeModule('main',
'B', 'canvas', 'camera', 'screenSize', 'map',
function (B, canvas, camera, screenSize, map) {
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
		fps,
		STATES = {
			SOCKET_NOT_SUPPORTED: -1,
			MAIN_MENU: 0,
			GAME_ON_WAIT_FOR_PLAYER: 1,
			GAME_ON_WAIT_TO_PLAY: 2,
			GAME_ON_WAIT_FOR_TURN: 3,
			GAME_FINISHED: 4
		},
		currentState;

	/**
	 * Method to adapt the canvas dimensions to the screen and the camera to the
	 * canvas
	 */
	function resize (dimensions) {
		canvas.resize(dimensions);
		camera.w = canvas.getWidth();
		camera.h = canvas.getHeight();
	}

	function drawErrorScreen (error) {
		canvas.drawRectangle(0, 0, canvas.getWidth(), canvas.getHeight(), 'black');
		canvas.drawText(
			error,
			canvas.getWidth() / 2 - 50,
			200,
			'white'
		);
	}

	/**
	 * Method to draw the main menu
	 */
	function drawMainMenu () {
		canvas.drawRectangle(0, 0, canvas.getWidth(), canvas.getHeight(), 'black');
		canvas.drawText(
			'Click to start the game',
			canvas.getWidth() / 2 - 50,
			200,
			'white'
		);
	}

	/**
	 * Method to draw the wait screen when the player is waiting for an
	 * opponent
	 */
	function drawWaitScreen () {
		canvas.canvas.width = canvas.getWidth();
		canvas.drawText(
			'Waiting for a player to join',
			canvas.getWidth() / 2 - 50,
			200,
			'black'
		);
	}

	/**
	 * Main draw method. Draws the sky, the map and its objects
	 */
	function drawGame () {
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

			if (currentState == STATES.SOCKET_NOT_SUPPORTED) {
				drawErrorScreen('Socket not supported');
			}
			else if (currentState == STATES.MAIN_MENU) {
				drawMainMenu();
			}
			else if (currentState == STATES.GAME_ON_WAIT_FOR_PLAYER) {
				drawWaitScreen();
			}
			else if (~[STATES.GAME_ON_WAIT_FOR_TURN, STATES.GAME_ON_WAIT_TO_PLAY].indexOf(currentState)) {
				if (m) {
					m.update();
					camera.update();
					drawGame();
				}
			}
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
			if (currentState == STATES.MAIN_MENU) {
				currentState = STATES.GAME_ON_WAIT_FOR_PLAYER;
				startGame();
			}
			else if (currentState == STATES.GAME_ON_WAIT_TO_PLAY) {
				console.log('handle play click');
				m.click(camera.toWorldCoords({x: mouseX, y: mouseY}));
			}
		});
	}

	/**
	 * Method executed when clicking on the main menu
	 */
	function startGame () {
		console.log('start game');
		var ws = new WebSocket("ws://localhost:8888/ws");
		ws.onopen = function(evt) {
			ws.send(JSON.stringify({messageType: 'CLIENT_JOINED'}));
		};
		ws.onmessage = function (evt) {
			var data = JSON.parse(evt.data);
			console.log(data);
			switch (data.type) {
				case 'PLAYER_JOINED':
					console.log('player joined');
					break;
				 case 'PLAYER_LEFT':
					console.log('player left');
					break;
				case 'PLAYER_TURN':
					console.log('your turn');
					currentState = STATES.GAME_ON_WAIT_TO_PLAY;
					break;
				case 'GAME_MAP':
					console.log('map received');
					currentState = STATES.GAME_ON_WAIT_FOR_TURN;
					m = map(data.map);
					break;
				default:
					console.log('unknown message:');
					console.log(data);
			}
		};
		ws.onclose = function() {};
	}

	resize(screenSize.get());


	if ("WebSocket" in window) {
		currentState = STATES.MAIN_MENU;
	}
	else {
		currentState = STATES.SOCKET_NOT_SUPPORTED;
	}

	/**
	 * Event fired when the window is resized
	 */
	B.Events.on('resize', null, resize);

	initEvents();
	timePreviousFrame = Date.now();
	lastCalledTime = Date.now();
	fpsAccu = 0;

	mainLoop();
});
