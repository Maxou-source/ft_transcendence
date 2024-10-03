import { isHost } from "./loadGame.js";
import {stopGame} from "./pong.js";
import { getSocket } from "../main.js";
//import {ball} from "./pong.js";

export let num = 0;

export class PlayerPad {
	constructor(xpos, ypos, speed, canvas, counterElement, socket, player) {
		this.xpos = xpos;
		this.ypos = ypos;
		this.dy = 1 * speed;
		this.canvas = canvas;
		this.padWidth = 10;
		this.padHeight = 100;

		this.centerX = xpos + (this.padWidth / 2);
		this.centerY = ypos + (this.padHeight / 2);

		this.moving = 0;

		this.score = 0;
		this.counterElement = counterElement;
		this.socket = socket;
		this.stop = false;
		this.player = player;
		this.playGame = 0;
		this.multiplayer = 2;
		this.paddleIA = null;
		this.keyUp = 0;
		this.keyDown = 0;
		this.speed = 0;
		this.futurY = 0;
		this.ailvl = 0;
		this.currentDirection = 0;
		this.init();
	}

	init()
	{
		if (this.player === "AI")
			{
				this.playGame = 2;
				this.multiplayer = 2;
				this.paddleIA = "paddleRight1";
				this.keyUp = '+';
				this.keyDown = '-';
				this.speed = 2;
				this.futurY = this.canvas.height / 2;
				this.ailvl = this.canvas.width / 2;
				this.currentDirection = "ok";
			}
	}

	serObj()
	{
		let Obj = {"type": "pad_update",
			"pad" : { "xpos": this.xpos,
				"ypos": this.ypos,
				"padWdith": this.padWidth,
				"padHeight": this.padHeight,
				"centerY": this.centerY,
			},
			"isHost" : isHost};
		isHost ? (Obj["Player"] = "p1") : (Obj["Player"] = "p2");
		return Obj;
	}

	scored()
	{
		this.score++;
		this.counterElement.innerHTML = this.score+"";
		if (this.score > 4)
			stopGame('score');
	}

	draw(context)
	{
		context.fillStyle = this.color;
		if (this.image)
		{
			context.drawImage(this.image, this.xpos , this.ypos, this.padWidth, this.padHeight);

		}
		else
			context.fillRect(this.xpos, this.ypos, this.padWidth, this.padHeight);
        context.strokeRect(this.xpos, this.ypos, this.padWidth, this.padHeight);
	}

	async update(context)
	{
		this.centerY = this.ypos + (this.padWidth / 2);
		this.draw(context);
	}

	async multiMove(padNum)
	{
		await new Promise(resolve => {
			this.socket.onmessage = function(event){
				const data = JSON.parse(event.data);
				if (data.player === padNum) {
					this.ypos = data.ypos;
				}
			}
		})
	}

	move(direction, ball)
	{
		if (this.playGame === 2 && this.player === "AI")
		{
			this.aiMovePaddle(ball);
		}
		let tmpY = this.ypos + (this.dy * direction);
		if (tmpY >= 0 && (tmpY + this.padHeight) <= this.canvas.height)
			this.ypos = tmpY;
		if (this.socket && !this.stop && getSocket())
		{
			this.socket.send(JSON.stringify(this.serObj()));
		}
		
	}

	aiMovePaddle(ball)
    {
        let xpos = 0;
        let y = this.canvas.height / 2;
		if (ball.xpos > xpos && ball.xpos >= this.ailvl && ball.dx > 0)
		{
			xpos = ball.xpos;
			if (this.multiplayer < 4)
				y = ball.ypos; 
			else if (this.multiplayer === 4 && ball.ypos >= (this.canvas.height / 2)  - (this.padHeight / 2))
				y = (this.multiplayer === 4 && this.canvas.height / 2) - (this.padHeight / 2);
			else if (ball.ypos < (this.canvas.height / 2)  - (this.padHeight / 2))
				y = ball.ypos;
		}
        if (xpos != 0)
            this.moveThisPaddle(y);
		else
		{
			simulateKey(this.keyDown, false);
			simulateKey(this.keyUp, false);
		}
    }

	moveThisPaddle(y)
	{
		this.futurY = y;
		if (this.ypos + (this.padHeight/2) > y)
			simulateKey(this.keyUp, true);
		else if (this.ypos + (this.padHeight/2) < y)
			simulateKey(this.keyDown, true);
	}
}

function simulateKey(key, isKeyDown)
{
    const eventType = isKeyDown ? 'keydown' : 'keyup';
    const event = new KeyboardEvent(eventType, { key });
    document.dispatchEvent(event);
}