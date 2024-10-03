export class Canvas {
	constructor(width, height, color, containerId) {
		this.width = width;
		this.height = height;
		this.color = color;
		this.containerId = containerId;

		this.canvas = document.getElementById(containerId);

		this.canvas.width = this.width;
		this.canvas.height = this.height;

		this.canvas.style.background = color;
		// let context 
	}
}
