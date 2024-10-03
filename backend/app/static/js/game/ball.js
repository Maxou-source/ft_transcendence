import { setSocket } from "../main.js";
import { isHost, resetList, TourMessageHandler} from "./loadGame.js"
import { ball , stopGame, context, tournamentWinner, dblSideClick} from "./pong.js";

// let xpos, ypos, dx, dy;

// dx = 0;
// dy = 1;
// xpos = 2;
// ypos = 3;

export class Ball {
	constructor(xpos, ypos, radius, color, text, speed, canvas, p1, p2, socket) {
		this.xpos = xpos;
		this.ypos = ypos;
		this.radius = radius;
		this.color = color;
		this.text = text;
		this.speed = speed;

		this.dx = 1 * speed;
		this.dy = 1 * speed;

		this.canvas = canvas;
		this.p1 = p1;
		this.p2 = p2;

		this.moving = true;
		this.socket = socket;
		if (this.socket){
			this.socket.onmessage = function(event) {
				const data = JSON.parse(event.data);
				if (data.type === 'ball_update') 
					ball.updateFromServer(data, context);
				else if (data.type === 'stop_game') {
					stopGame(data.message);
				}
				else if (data.type === 'pad_update')
				{
					if (data.player === 'p2')
						p2.ypos = data.ypos;
					else
						p1.ypos = data.ypos;
				}
				else if (data.type === 'nextTour') {
					resetList(data.players, data.ready)
					socket.onmessage = TourMessageHandler;
				}
				else if (data.type === 'tourWinner') {
					tournamentWinner();
					socket.send(JSON.stringify({'type': 'disconnect', 'message': 'tourWinner'}));
					setSocket(null);
				}
			}
		}
        this.reset();
	}

	draw(context)
	{
		context.beginPath();

		context.strokeStyle = this.color;
		context.textAlign = "center";
		context.textBaseLine = "middle";
		context.fillStyle = "#000000";
		context.arc(this.xpos, this.ypos, this.radius, 0, Math.PI * 2, false);
		context.fill();
		context.strokeStyle = this.color;
		context.stroke();
		context.closePath();
	}

	intersectP1() {
        return (
            this.xpos - this.radius <= this.p1.xpos + this.p1.padWidth &&
            this.ypos >= this.p1.ypos &&
            this.ypos <= this.p1.ypos + this.p1.padHeight
        );
    }

	intersectP2() {
        return (
            this.xpos + this.radius >= this.p2.xpos &&
            this.ypos >= this.p2.ypos &&
            this.ypos <= this.p2.ypos + this.p2.padHeight
        );
    }

	serObj() {
		return {"p1" : {"xpos": this.p1.xpos,
						"ypos": this.p1.ypos,
						"padWidth": this.p1.padWidth,
						"padHeight": this.p1.padHeight},

				"p2" : {"xpos": this.p2.xpos,
						"ypos": this.p2.ypos,
						"padWidth": this.p2.padWidth,
						"padHeight": this.p2.padHeight},

				"ball" : {"xpos": this.xpos,
						"ypos": this.ypos,
						"dx": this.dx,
						"dy": this.dy,
						"radius": this.radius,
						"canvas_height": this.canvas.height,
						"speed": this.speed},
				
				"canvas" : {"width": this.canvas.width,
							"height": this.canvas.height},

				"type": "ball_update"
		};
	}

    move() {
        let newX = this.xpos + this.dx * this.speed * 0.3;
        let newY = this.ypos + this.dy * this.speed * 0.3;

        [this.p1, this.p2].forEach(paddle => {
            let res = this.collisionCheckCircleRect(paddle);
            if (((paddle === this.p1 && this.dx < 0) || (paddle === this.p2 && this.dx > 0)) && res === "mid") {
                this.dx = -this.dx; // Inverser le déplacement horizontal
            } else if (((paddle === this.p1 && this.dx < 0) || (paddle === this.p2 && this.dx > 0)) && (res === "top" || res === "bot")) {
                this.dy = -this.dy; // Inverser le déplacement vertical
            } else if (((paddle === this.p1 && this.dx < 0) || (paddle === this.p2 && this.dx > 0)) && res === "corner") {
                this.dy = -this.dy;
                this.dx = -this.dx; // Inverser à la fois le déplacement vertical et horizontal
            }
        });
        this.xpos += this.dx * this.speed * 0.3;
        this.ypos += this.dy * this.speed * 0.3;

        this.collision();
    }

    collision() {
        if (this.ypos + this.radius > this.canvas.height || this.ypos - this.radius < 0) {
            this.dy = -this.dy;
        }

        if (this.xpos + this.radius > this.canvas.width) {
            this.reset();
            this.p1.scored();
        }
        if (this.xpos - this.radius < 0) {
            this.reset();
            this.p2.scored();
        }
    }

    collisionCheckCircleRect(rect) {
        var distX = Math.abs(this.xpos - rect.xpos - rect.padWidth / 2);
        var distY = Math.abs(this.ypos - rect.ypos - rect.padHeight / 2);

        if (distX > (rect.padWidth / 2 + this.radius)) { return "false"; }
        if (distY > (rect.padHeight / 2 + this.radius)) { return "false"; }

        if (distX <= (rect.padWidth / 2)) { 
            if (this.ypos < rect.ypos - rect.padHeight / 2) {
                return ("top");
            } else if (this.ypos > rect.ypos + rect.padHeight / 2) {
                return ("bot");
            }
        }
        
        if (distY <= (rect.padHeight / 2)) {
            return ("mid");
        }

        var dx = distX - rect.padWidth / 2;
        var dy = distY - rect.padHeight / 2;
        if (dx * dx + dy * dy <= (this.radius * this.radius)) {
            return ("corner");
        }
        return "false";
    }

	async update(context)
	{
	// 	if (this.socket) {
			context.beginPath();
			context.arc(this.xpos, this.ypos, this.radius, 0, Math.PI * 2, false);
			context.fill();
			context.closePath();
		// }

		if (!this.socket) this.move();
		else {
		 	if (isHost)
		 		this.socket.send(JSON.stringify(this.serObj()));
		 	return ;
		}
		this.draw(context);
    }

    reset() {
        this.xpos = this.canvas.width / 2;
	 	this.ypos = this.canvas.height / 2;
        let angle;
        if (Math.random() < 0.5) {
            // La balle va à droite
            angle = Math.PI / 4 + Math.random() * 3 * Math.PI / 2;
        } else {
            // La balle va à gauche
            angle = (3 * Math.PI) / 4 + Math.random() * (Math.PI / 2); // Ajout d'un angle aléatoire dans l'intervalle [3π/4, 5π/4]        }
        this.dx = Math.cos(angle) * this.speed;
        this.dy = Math.sin(angle) * this.speed;
        } 
    }

	updateFromServer(data, context) {
		this.dx = data.dx;
        this.dy = data.dy;
		this.xpos = data.xpos;
		this.ypos = data.ypos;
		if (data.p1Scored) {
			this.reset();
			this.p1.scored();
		}
		else if (data.p2Scored) {
			this.reset();
			this.p2.scored();
		}
    }
}