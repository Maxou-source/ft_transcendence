import { Canvas } from "./game/canvas.js";
import { loadGame } from "./game/loadGame.js";
import { goParams } from "./parameters/paramsMain.js";
import { createChatBox } from "./friends/friends.js";
import { goFriends } from "./friends/friends.js"
import { goStatistics } from "./statistics/statistics.js";
import { dblSideClick } from "./game/pong.js"

export let mystorage = localStorage;

export let players = 0;

var march = 0;
export var data = [];

export let socket = null;
export let chatSocket = null;

let sidebarFolded = false;

export function refreshToken() {
	const request = new XMLHttpRequest();
	request.open("GET", "/refresh_access_token/", false);
	request.send();
	if (request.status === 200) {
		const response = JSON.parse(request.responseText);
		return response.access_token;
	}
}

export function setSocket(newSocket) { socket = newSocket;}

export function getSocket() { return socket;}

export function setChatSocket(newSocket) {
    chatSocket = newSocket;
}

export function getChatSocket() {
    return chatSocket;
}

function getCookie(name) {
	let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
     
export const csrftoken = getCookie('csrftoken');

function autorefreshToken() {

	$.ajax({
		type: "POST",
		dataType: "json",
		url: "/refresh_access_token/",
		data: "code",
		headers: {
			'X-CSRFToken': csrftoken
		},
		success: function(data) {
		},
		error: function(data) {
			console.error("error refreshing access token", data);
		}
	});
}

function delay(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}
// 3600000
async function loop(){
	while (true){
		await delay(3600000);
		autorefreshToken();
	}
}

loop();

export async function showSection(section, push) {
    mystorage.setItem('previous', mystorage.getItem('state'));
    mystorage.setItem('state', `${section}`);
    const response = await fetch(`home/${section}`);
    let text = await response.text();

    let existingDivNode = document.getElementById("inserted");
    if (existingDivNode) {
        existingDivNode.innerHTML = text;
    } else {
        let divNode = document.createElement("div");
        divNode.id = "inserted";
        divNode.class = "inserted";
        divNode.innerHTML = text;
        let stateObj = { content: 'this random content'};
        if (push === true)
            history.pushState(stateObj, '', `/${section}`);
        document.getElementById("wrapper").appendChild(divNode);
    }
    return new Promise((resolve, reject) => {
        if (section === "params") {
            let wrap = document.getElementById("wrapper");
            wrap.className = "wrap-content";
            goParams();
        }
        if (section === "friends") {
            let wrap = document.getElementById("wrapper");
            wrap.className = "wrap-content";
            goFriends();
        }
        if (section === "statistics") {
            let wrap = document.getElementById("wrapper");
            wrap.className = "wrap-content-stat";
            goStatistics();
        }
        if (section === "game") {
            let wrap = document.getElementById("wrapper");
            wrap.className = "wrap-content";
            loadGame(null);
    }
        resolve();
    });
}

window.addEventListener('popstate', function(event) {
    changePage();
    showSection(mystorage.getItem('previous'), false);
});

let item = mystorage.getItem('state');
	
if (item !== 'null' && item !== 'leaderboard' && item !== 'game' && item !== 'params' && item != 'statistics' && item != 'friends')
	mystorage.setItem('state', null);
	
window.onload = function() {
	let wlocahref = window.location.href;
	if (wlocahref.includes("profile"))
		return ;
	let storedState = mystorage.getItem('state');
	if (storedState !== 'null')
	{
		showSection(storedState, true);
	}
}

function changePage() {
	dblSideClick();
	document.getElementById('wrapper').innerHTML = "";
	if (socket) {
        socket.send(JSON.stringify({"type": "disconnect", "message": "handleClickonSidebar"}));
        setSocket(null);
		// socket = null;
    }
	if (chatSocket) {
        chatSocket.close();
        setChatSocket(null);
    }
	let gameContainer = document.getElementById("game-container");
	let insertedContainer = document.getElementById("inserted");
	let gameButtons = document.getElementById("gameButtons");
	let gameCounters = document.getElementById("countersDiv");
    let statContainer = document.getElementById("tempDiv");
    let chatContainer = document.getElementById("whatever");

	gameContainer && document.getElementById("wrapper").removeChild(gameContainer);
	insertedContainer && document.getElementById("wrapper").removeChild(insertedContainer);
	gameButtons && document.getElementById("wrapper").removeChild(gameButtons);
	gameCounters && document.getElementById("wrapper").removeChild(gameCounters);
    statContainer && document.getElementById("wrapper").removeChild(statContainer);
    chatContainer && document.getElementById("wrapper").removeChild(chatContainer);
}


function handleClickOnSidebar(event, arg) {
    changePage();
    showSection(arg, true);
}
		
document.addEventListener('DOMContentLoaded', function() {
	// document.getElementById("sidebarReducer").addEventListener("click", manageSidebar);

    document.getElementById("GameAnchor").addEventListener('click', (event) => handleClickOnSidebar(event, "game"));
	document.querySelector("#GameAnchor svg").addEventListener('click', (event) => handleClickOnSidebar(event, "game"));

    document.getElementById("ParamsAnchor").addEventListener('click', (event) => handleClickOnSidebar(event, "params"));
	document.querySelector("#ParamsAnchor svg").addEventListener('click', (event) => handleClickOnSidebar(event, "params"));

    document.getElementById("StatisticsAnchor").addEventListener('click', (event) => handleClickOnSidebar(event, "statistics"));
	document.querySelector("#StatisticsAnchor svg").addEventListener('click', (event) => handleClickOnSidebar(event, "statistics"));

    document.getElementById("FriendsAnchor").addEventListener('click', (event) => handleClickOnSidebar(event, "friends"));
	document.querySelector("#FriendsAnchor svg").addEventListener('click', (event) => handleClickOnSidebar(event, "friends"));

    document.getElementById("logoutButton").addEventListener("click", function() {
		window.location.href = '/logout';
	});
	document.querySelector("#logoutButton svg").addEventListener("click", function() {
		window.location.href = '/logout';
	});
	// Add event listener for friend request buttons
    

	document.querySelectorAll('.accept-friend-request').forEach(button => {
		button.addEventListener('click', () => acceptFriendRequest(button.dataset.requestId));
	});
});
		
document.getElementById("logoutButton").addEventListener("click", function() {
	window.location.href = '/logout';
})
		
		
document.addEventListener('DOMContentLoaded', function () {
	document.getElementById("sidebarReducer").addEventListener("click", manageSidebar);
})
	
const manageSidebar = () => {
	const sidebar = document.getElementById('sidebar');
	const user = document.querySelector('.wrap-user');
	const menu = document.querySelector('.lucide.lucide-menu')
	const borders = document.querySelectorAll('.border-btm');
	const love = document.querySelector('.ctn-love');
	const links = document.querySelectorAll('.wrap-redirect');
	const redirects = document.querySelector('.wrap-redirects');
	const linksText = document.querySelectorAll('.wrap-redirect span');
	
	const width = sidebar.getBoundingClientRect().width;
	if (sidebarFolded === false) {
		sidebar.style.width = '75px'
		menu.style.position = 'static';
		menu.style.margin = '30px 0 0 0';
		love.style.display = 'none';
		redirects.style.margin = '30px 0 0 0';
		redirects.style.gap = '22px';
		user.style.display = 'none';
		for (let i = 0; borders[i]; i++)
			borders[i].style.display = 'none';
		for (let i = 0; linksText[i]; i++) {
			linksText[i].style.display = 'none';
			links[i].style.width = 'calc(100% - 20px)';
			links[i].style.justifyContent = 'center';
		}
		sidebarFolded = true;
	}
	else {
		sidebar.style.width = 'calc(350px - 55px)';
		sidebar.style.height = '100%';
		redirects.style.margin = '0 0 20px 0';
		redirects.style.gap = '5px';
		menu.style.position = 'absolute';
		menu.style.margin = '0 0 0 0';
		// sidebar.style.padding = '50px 20px 50px 35px';
		user.style.display = 'flex';
		love.style.display = 'flex';
		for (let i = 0; borders[i]; i++)
			borders[i].style.display = 'flex';
		for (let i = 0; linksText[i]; i++) {
			linksText[i].style.display = 'flex';
			links[i].style.width = 'unset';
		links[i].style.justifyContent = 'flex-start';
		}
		sidebarFolded = false;
	}
};
