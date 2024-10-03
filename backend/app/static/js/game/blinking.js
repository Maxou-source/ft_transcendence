export function BlinkText(txt, x, y, interval) {
	this.text = txt;
	this.x = x;
	this.y = y;
	this.interval = interval;
	this.font = "bold 100px sans-serif";
	this.color = 'green';
	this.active = false;
	this.time = 0;
	this.toggle = true;
}
  
BlinkText.prototype = {
	start: function(time) {
		this.time = time;
		this.active = true;
		this.toggle = true;
	},
	
	stop: function() {
		this.active = false;
	},
	
	render: function(ctx) {
	  if (this.active) {
		if (this.toggle) {
			ctx.font = this.font;
			ctx.fillStyle = this.color;
			ctx.fillText(this.text, this.x, this.y);
		}
		
		var time = performance.now();
		if (time - this.time >= this.interval) {
			this.time = time;
			this.toggle = !this.toggle;
		}
		}
	},

	clean: function(ctx) {
		ctx.clearRect(this.x, this.y - 100, ctx.measureText(this.text).width, 100);
	}
	
};