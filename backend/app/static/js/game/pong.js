import { Ball } from "./ball.js";
import { PlayerPad } from "./playerPad.js";
import { Canvas } from "./canvas.js";
import {handleEventUpAI, handleEventDownAI, handleEventDown, handleEventUp, handleEventDownMulti, handleEventUpMulti} from "./event.js";
import { BlinkText } from "./blinking.js";
import { isHost , GameMode, name1, name2} from "./loadGame.js";
import { setSocket, getSocket} from "../main.js";

export let start = false;
export let pause = false;
export let stop = false;

export let counterp1;
export let counterp2;

var canvasWidth = 900;
var canvasHeight = 500;

var winnerText = new BlinkText("", 450, 250, 500);

let canvas;
export let context;

export let p1;
export let p2;

export let ball;

export function updateGame() {
	if (stop)
	{
		stop = false;
		document.removeEventListener('keydown', handleEventDown);
		document.removeEventListener('keyup', handleEventUp);
		document.removeEventListener('keydown', handleEventDownAI);
		document.removeEventListener('keyup', handleEventUpAI);
		document.removeEventListener('keydown', handleEventDownMulti);
		document.removeEventListener('keyup', handleEventUpMulti);
		return ;
	}
	// if (data && data.type === 'move') {
    //     if (data.player === 1) {
    //         p1.moving = data.direction;
    //     } else if (data.player === 2) {
    //         p2.moving = data.direction;
    //     }
    // }
	context.clearRect(0,0, canvasWidth, canvasHeight);
	if (!p1.socket || !p2.socket) {
		p1.move(p1.moving, ball);
		p2.move(p2.moving, ball);
	}
	else {
		if (isHost)
		{
			p1.move(p1.moving, ball);
		}
		else
			p2.move(p2.moving, ball);
	}
	p1.update(context);
	p2.update(context);
	ball.update(context);
	if (!stop) 
		window.animeId = window.requestAnimationFrame(updateGame);
	else{
		stop = false;
		return ;
	}
}

export function StartGameLocal() {
	gameMode = 'Local';
	document.removeEventListener('keydown', handleEventDownAI);
	document.removeEventListener('keyup', handleEventUpAI);
	document.addEventListener('keydown', handleEventDown);
	document.addEventListener('keyup', handleEventUp);
	updateGame();
}

function resetGame(counterp1, counterp2) {
	winnerText.stop();
	p1.ypos = 200;
	p2.ypos = 200;
	p1.score = 0;
	p2.score = 0;
	ball.reset();
	// start = false;
	
	if (counterp1 && counterp2) {
		counterp1.innerHTML = p1.score+"";
		counterp2.innerHTML = p2.score+"";
	}
}

export function determineWinner(p1, p2) {
	if (p1.socket && p2.socket && GameMode !== 'Local') {
		let obj = {"type": "update_winner", "date": new Date(), "mode": GameMode};
		let p1obj = { ...obj, userScore: p1.score, otherScore: p2.score, opponent: p2.player };
		let p2obj = { ...obj, userScore: p2.score, otherScore: p1.score, opponent: p1.player };
		
		if (isHost && getSocket()){
			p1.socket.send(JSON.stringify(p1obj));
		}
		else if (getSocket()){
			p2.socket.send(JSON.stringify(p2obj));
		}
	}
	let result = "DRAW";
    if (p1.score > p2.score)
        result = p1.player + " WINS";
    else if (p2.score > p1.score)
        result = p2.player + " WINS";
    if (p1.score > 4 || p2.score > 4 || stop === true)
    {
        stop = true;
        return result;
    }
    return -1;
}

export function printOutWinner(p1, p2, type) {
	context.clearRect(0, 0, canvasWidth, canvasHeight);
	if (type != 'handleClickonSidebar')
    	winnerText.text = determineWinner(p1, p2);
	resetGame(counterp1, counterp2);
    winnerText.start(performance.now());

	winnerText.render(context);
	
    // let startTime = performance.now();
    // function loop() {
	// 	context.clearRect(0, 0, canvasWidth, canvasHeight);
    //     winnerText.render(context);

    //     let currentTime = performance.now();
    //     let elapsedTime = currentTime - startTime;

    //     if (elapsedTime < 2500) {
    //         requestAnimationFrame(loop);
    //     }
    // }

    // requestAnimationFrame(loop);
}

function countDown(callback) {
    let count = 3;
    const countdownInterval = setInterval(() => {
        context.clearRect(0, 0, canvasWidth, canvasHeight);
        context.font = '48px Arial';
        // context.fillStyle = 'white';
        context.textAlign = 'center';
        context.fillText(count > 0 ? count : 'GO!', canvasWidth / 2, canvasHeight / 2);
        
        if (count === 0) {
            clearInterval(countdownInterval);
            setTimeout(() => {
                context.clearRect(0, 0, canvasWidth, canvasHeight); // Clear the GO! text
                callback(); // Start the game after the countdown
            }, 1000);
        }
        count--;
    }, 1000);
}

export function dblSideClick(){
	if (start) {
		stop = true;
		start = false;
	}
}

export function tournamentWinner() {
	stop = true;
	start = false;
	context.clearRect(0,0, canvasWidth, canvasHeight);
	
	winnerText.clean(context);
	// winnerText.text = '';
	// winnerText.render(context);

	// winnerText.text = "YOU WON THE TOURNAMENT";
	winnerText.text = '🏆';

	resetGame(document.getElementById('counterp1'), document.getElementById('counterp2'));
    
	winnerText.start(performance.now());
	winnerText.render(context);
}

export function stopGame(type) {
	// statePrint('stopGame:pong.js:176');
	stop = true;
	start = false;
	counterp1 = document.getElementById('p1Counter');
	counterp2 = document.getElementById('p2Counter');
	if (counterp1 && counterp2) {
		printOutWinner(p1, p2);
	}
}

export function initializeGame(socket, playGame) {
	//stop = false;
	// start = true;
	window.animeId = 0;
	canvas = new Canvas(canvasWidth, canvasHeight, "#ff8", 'canvasContainer');
	context = canvas.canvas.getContext("2d");

	counterp1 = document.getElementById('p1Counter');
	counterp2 = document.getElementById('p2Counter');
	p1 = new PlayerPad(20, 200, 5, canvas, counterp1, socket, name1);
	if (playGame == 1)
		p2 = new PlayerPad(canvasWidth - 30, 200, 5, canvas, counterp2, socket, name2);
	else
		p2 = new PlayerPad(canvasWidth - 30, 200, 5, canvas, counterp2, socket, "AI");
	// statePrint('DJSHFBDJSHK');
	ball = new Ball(450, 250, 20, "black", 1, 4, canvas, p1, p2, socket);

	ball.draw(context);
	p1.draw(context);
	p2.draw(context);
	
	if (!socket) {
		// document.getElementById("stopGame").addEventListener("click", function() {stopGame('event')});
		document.getElementById("startGameButtonLocal").addEventListener("click", function() {
			if (!start){
				if (socket) {
					socket.close();
					setSocket(null);
				}
				start = true;
				document.removeEventListener('keydown', handleEventDownAI);
				document.removeEventListener('keyup', handleEventUpAI);
				document.addEventListener('keydown', handleEventDown);
				document.addEventListener('keyup', handleEventUp);
				resetGame(counterp1, counterp2);
				updateGame();
				//initializeGame(socket, 1);
			}
		});
		document.getElementById("startGameButtonAI").addEventListener("click", function() {
			if (!start){
				if (socket) {
					socket.close();
					setSocket(null);
				}
				start = true;
				document.removeEventListener('keydown', handleEventDown);
				document.removeEventListener('keyup', handleEventUp);
				document.addEventListener('keydown', handleEventDownAI);
				document.addEventListener('keyup', handleEventUpAI);
				p2.init();
				resetGame(counterp1, counterp2);
				updateGame();
			}
		});
	}
    if (socket) {
        countDown(() => {
			start = true;
            updateGame();
        });
    }
}

export function isRGB(value)
{
    const rgbRegex = /^rgb\(\s*(?:[01]?\d{1,2}|2[0-4]\d|25[0-5])\s*,\s*(?:[01]?\d{1,2}|2[0-4]\d|25[0-5])\s*,\s*(?:[01]?\d{1,2}|2[0-4]\d|25[0-5])\s*\)$/;
    return rgbRegex.test(value);
}
