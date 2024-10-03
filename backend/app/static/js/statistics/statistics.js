import { csrftoken } from "../main.js";

export async function goStatistics() {
	// let canvas = document.getElementById("canvasStat");
	let div = document.createElement("div");
	div.id = "tempDiv";
	let canvas = document.createElement("canvas");
	canvas.id = "canvasStat";
	canvas.class = "canvas-stat";
	canvas.style.marginLeft = "80px";
	div.appendChild(canvas);


	let title = document.createElement("p");
	title.innerHTML = "Points per game";
	title.style.color = "white";
	title.style.marginLeft = "80px";
	div.appendChild(title);

	document.getElementById("wrapper").appendChild(div);

	let context = canvas.getContext("2d");

	canvas.width = 400;
	canvas.height = 200;

	canvas.style.background = "#ddf";

	var data2 = []

	let payload = {
		"token": csrftoken
	}
    await $.ajax({
        type: "GET",
        dataType: "json",
        url: "/get_statistics/",
        data: payload,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(data) {
            if (data['response'] == "stats found.") {
                data2 = data['user_histories'];
            }
        },
        error: function(data) {
            console.error("Error:", data);
			return ;
        }
    });
	if (data2.length === 0)
		return ;
	let count = document.createElement("div");

	const start_value = data2[0]['userScore'];

	const distance = canvas.width / data2.length;
	const start_point = 0;

	context.beginPath();

	context.lineWidth = 3;
	context.strokeStyle = '#f56';

	data2.forEach( (element, index) => {
		const new_distance = start_point + (distance * (index + 1));
		context.lineTo(new_distance, 200 - (data2[index]['userScore'] * 40));
	})

	context.lineTo(canvas.width, canvas.height);
	context.lineTo(start_point, canvas.height);

	context.fillStyle = "grey";
	context.fill(); 
	context.stroke();

}
