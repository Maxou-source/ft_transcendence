import { socket } from "../main.js";
import {p1, p2} from "./pong.js";

export function handleEventDownMulti(event, player) {
	if (event.key === 's' || event.key === 'S' || event.Key === 'ArrowDown')
        player.moving = 1;
	else if (event.key === 'w' || event.key === 'W' || event.key === 'z' || event.key === 'Z' || event.Key === "ArrowUp") 
		player.moving = -1;
	
    // player.socket.send(JSON.stringify(player.serObj()));
}

export function handleEventUpMulti(event, player) {
	if (event.key === 's' || event.key === 'S' || event.Key === "ArrowDown")
        player.moving = 0;
	else if (event.key === 'w' || event.key === 'W' || event.key === 'z' || event.key === 'Z' || event.Key === "ArrowUp") 
        player.moving = 0;

	// player.socket.send(JSON.stringify(player.serObj()));
}

export function handleEventDown(event) {
	if (event.key === 's' || event.key === 'S')
	{
		p1.moving = 1;
	}
	else if (event.key === 'w' || event.key === 'W' || event.key === 'z' || event.key === 'Z')
	{
		p1.moving = -1;
	}
	else if (event.key === "ArrowDown")
	{
		p2.moving = 1;
	}
	else if (event.key === "ArrowUp")
	{
		p2.moving = -1;
	}
}

export function handleEventUp(event) {
	if (event.key === 's' || event.key === 'S')
	{
		p1.moving = 0;
	}
	else if (event.key === 'w' || event.key === 'W' || event.key === 'z' || event.key === 'Z')
	{
		p1.moving = 0;
	}
	else if (event.key === "ArrowDown" )
	{
		p2.moving = 0;
	}
	else if (event.key === "ArrowUp" )
	{
		p2.moving = 0;
	}
}

export function handleEventDownAI(event)
{
	if (event.key === 's' || event.key === 'S')
	{
		p1.moving = 1;
	}
	else if (event.key === 'w' || event.key === 'W')
	{
		p1.moving = -1;
	}
	if (event.key === '-')
	{
		p2.moving = 1;
	}
	else if (event.key === '+')
	{
		p2.moving = -1;
	}
}

export function handleEventUpAI(event) {
	if (event.key === 's' || event.key === 'S' || event.key === 'w' || event.key === 'W')
		{
			p1.moving = 0;
		}
	if (event.key === '-' || event.key === '+')
	{
		p2.moving = 0;
	}
}