import { p1, p2, initializeGame, dblSideClick, stopGame} from "./pong.js";
import {handleEventDownMulti, handleEventUpMulti} from "./event.js";
import { csrftoken, refreshToken, setSocket, socket} from "../main.js"

export let isHost = false;

export let GameMode;
//let buttons = [];
let handlers = [null, startOnlineGame, startAIGame, startTournament];

export let p1Image, p2Image = null;
export let name1 = 'p1';
export let name2 = 'p2';

export function loadGame(socket) {
    // Clear existing content in the wrapper
    document.getElementById("wrapper").innerHTML = '';
    document.getElementById("wrapper").className = 'wrap-content';
    
    // Create the game container
    var gameContainer = document.createElement('div');
    gameContainer.className = 'game-container';
    gameContainer.id = 'game-container';
    
    var canvas = document.createElement('canvas');
    canvas.id = 'canvasContainer';
    gameContainer.appendChild(canvas);
    
    const countersContainer = document.createElement('div');
    countersContainer.id = "countersDiv";
    countersContainer.className = 'counters-container';

    // Set the innerHTML of the counters container
    if (socket) {
        countersContainer.innerHTML = `
        <img style="border-radius: 50%; width: 50px; height: 50px; margin-right: 10px;" src="${p2Image}">
        <div id="p2Counter" class="counters">0</div>
        <img style="border-radius: 50%; width: 50px; height: 50px; margin-right: 10px;" src="${p1Image}">
        <div id="p1Counter" class="counters">0</div>
        `
    }
    else {
        countersContainer.innerHTML = `
        <b>P1 Counter</b>
        <div id="p1Counter" class="counters">0</div>
        <b>P2 Counter</b>
        <div id="p2Counter" class="counters">0</div>
        `;
    }
    // Append gameContainer and countersContainer to the wrapper
    document.getElementById("wrapper").appendChild(gameContainer);
    document.getElementById("wrapper").appendChild(countersContainer);
    
    // Create the game buttons container
    let gameButtons = document.createElement("div");
    gameButtons.className = "ctn-game-buttons";
    gameButtons.id = "gameButtons";
    
    // Create and append the game buttons
    const button = document.createElement('button');
    button.id = 'startGameButtonLocal';
    button.innerText = 'Lancer une partie en local';

    if (!socket) {
        // Create the stop button and append it to gameContainer
        var stopButton = document.createElement('button');
        stopButton.id = 'stopGame';
        stopButton.className = 'pause-button';
        stopButton.textContent = 'Stop';
        gameContainer.appendChild(stopButton);
    }
    let button2 = button.cloneNode(true);
    button2.innerText = "Lancer une partie contre l'IA";
    button2.id = 'startGameButtonAI';
    button2.addEventListener('click', () => startAIGame(socket));
    
    let button3 = button.cloneNode(true);
    button3.innerText = "Lancer une partie en ligne";
    button3.id = 'startGameButtonOnline';
    button3.addEventListener('click', () => startOnlineGame(socket, null));
    
    let button4 = button.cloneNode(true);
    button4.innerText = "Tournoi";
    button4.id = 'startTournament';
    button4.addEventListener('click', () => startTournament(socket));
        
    gameButtons.appendChild(button);
    gameButtons.appendChild(button2);
    gameButtons.appendChild(button3);
    gameButtons.appendChild(button4);

    // Append the game buttons container to the wrapper
    document.getElementById("wrapper").appendChild(gameButtons);
    
    if (socket) disableButtons();
    //else enableButtons();

    // Initialize the game
    initializeGame(socket, 1);//1=normal
}

function startAIGame(socket) {
    if (socket) {
        socket.close();
        setSocket(null);
    }
    disableButtons();
    initializeGame(null, 2);//2=IA
}

function disableButtons() {
    let i = 0;
    let buttons = document.querySelectorAll(".ctn-game-buttons button");
    buttons.forEach(button => {button.disabled = true;})    
    buttons.forEach((button, i) => {button.removeEventListener('onclick', handlers[i++]);})
}

export function startOnlineGame(socket, friend) {
    if (socket){
        socket.close();
        setSocket(null);
    }
    GameMode = "Online Game";
    
    let token = document.getElementById('token-div').getAttribute('data-token');
    if (!token) {token = refreshToken();}
    let sockaddr;
    if (friend) sockaddr = `wss://${location.hostname}:8443/ws/game/?token=${token}&?friend=${friend}`;
    else sockaddr = `wss://${location.hostname}:8443/ws/game/?token=${token}`;
    socket = new WebSocket(sockaddr);
    setSocket(socket);

    document.getElementById('wrapper').innerHTML = `<div id="loadingAnimation" style="display: none; color: white">
    <p>Loading... Waiting for another player to join</p>
    <!-- Add your spinner or animation here -->
    </div>`;
    
    document.getElementById('loadingAnimation').style.display = 'block'; // Show loading animation

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
        document.getElementById('loadingAnimation').style.display = 'none'; // Hide loading animation on error
    };
    
    socket.onmessage = function(messageEvent) {
        const data = JSON.parse(messageEvent.data);
        if (data.message.includes('host_status'))
            isHost = data.isHost;
        if (data.message.includes('The game is starting!')) {

            p1Image = data.player1_image;
            p2Image = data.player2_image;
            name1 = data.player1_name;
            name2 = data.player2_name;
            let anim = document.getElementById('loadingAnimation');
            if (anim)
                anim.style.display = 'none';
            if (isHost) {
                document.addEventListener('keydown', (event) => handleEventDownMulti(event, p1));
                document.addEventListener('keyup', (event) => handleEventUpMulti(event,p1));
            }
            else {
                document.addEventListener('keydown', (event) => handleEventDownMulti(event, p2));
                document.addEventListener('keyup', (event) => handleEventUpMulti(event,p2));
            }
            document.getElementById('wrapper').innerHTML = '';
            loadGame(socket);
        }
        if (data.type == 'stop_game') {
            dblSideClick();
            socket.close();
            setSocket(null);
        }
    };


    window.addEventListener('beforeunload', function() {
        if (socket) {
            // this.document.getElementById('wrapper').innerHTML = '';
            socket.close();
            setSocket(null);
        }
    });
}

function startTournament(socket, buttons) {
     if (socket) {
         socket.close();
         setSocket(null);
     }
    createTournamentView();
}

function createTournamentView() {
    GameMode = "Tournament";

    document.getElementById("wrapper").innerHTML = '';

    let tournamentContainer = document.createElement('div');
    tournamentContainer.className = 'tournament-container';

    let tournamentForm = document.createElement('form');
    tournamentForm.id = 'tournamentForm';

    let label = document.createElement('label');
    label.htmlFor = 'tournamentName';
    label.innerText = 'UserName:';
    label.style.padding = '4px 10px';
    label.style.background = '#111';
    label.style.color = '#fff';
    label.style.fontSize = '12px';
    label.style.borderRadius = '5px';
    label.style.boxShadow = 'rgba(0, 0, 0, 0.24) 0px 3px 8px';

    let input = document.createElement('input');
    input.type = 'text';
    input.id = 'tournamentName';
    input.name = 'tournamentName';
    input.style.marginTop = '10px';
    input.style.padding = '5px';

    let submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.innerText = 'Join Tournament';
    submitButton.style.marginTop = '10px';
    submitButton.style.padding = '4px 10px';
    submitButton.style.background = '#111';
    submitButton.style.color = '#fff';
    submitButton.style.fontSize = '12px';
    submitButton.style.borderRadius = '5px';
    submitButton.style.boxShadow = 'rgba(0, 0, 0, 0.24) 0px 3px 8px';

    let errorMessage = document.createElement('div');
    errorMessage.className = 'error-message';

    tournamentForm.appendChild(label);
    tournamentForm.appendChild(input);
    tournamentForm.appendChild(submitButton);
    tournamentForm.appendChild(errorMessage);

    let style = document.createElement('style');
    style.innerHTML = `
        input.error {
            border: 2px solid red;
            animation: shake 0.3s;
        }
        @keyframes shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            50% { transform: translateX(5px); }
            75% { transform: translateX(-5px); }
            100% { transform: translateX(0); }
        }
        .error-message {
            color: red;
            margin-top: 10px;
        }
    `;
    document.head.appendChild(style);

    tournamentContainer.appendChild(tournamentForm);

    document.getElementById("wrapper").appendChild(tournamentContainer);

    function resetAnimation(element) {
        element.style.animation = 'none';
        element.offsetHeight;
        element.style.animation = '';
    }

    tournamentForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        let playerName = input.value;
        errorMessage.innerText = '';
        input.classList.remove('error');
        const response  = await $.ajax({
            type: "GET",
            dataType: "json",
            url: "/get_tournames/",
            headers: {
                'X-CSRFToken': csrftoken
            },
        });

        const tourNames = response.tour_names;

        if (playerName === '' || /\s/.test(playerName) || !playerName.match(/\S/)) {
            input.classList.add('error');
            errorMessage.innerText = 'Username cannot be empty or contain spaces or invalid characters.';
            errorMessage.style.color = 'red';
            resetAnimation(input);
        }
        else if (nameTaken(playerName, tourNames)) {
            input.classList.add('error');
            errorMessage.innerText = 'Username is already taken.';
            errorMessage.style.color = 'red';
            resetAnimation(input);
        }
        else if (playerName.length < 4 || playerName.length > 20) {
            input.classList.add('error');
            errorMessage.innerText = 'Username must be between 4 and 20 char';
            errorMessage.style.color = 'red';
            resetAnimation(input);
        }
        else {
            errorMessage.innerText = 'Tournament joined successfully!';
            errorMessage.style.color = 'green';
            waitForPlayers(playerName);
        }
    }); 
}

function nameTaken(playerName, tourNames) {
    return tourNames.some((tourName) => {
        if (tourName === playerName) {
            return true;
        }
        return false;
    });
}

let plCount;
let tourSocket;

export function TourMessageHandler(event){
    const data = JSON.parse(event.data);
    let docWrapper = document.getElementById('wrapper');

    if (data.type === 'host_status'){
        isHost = data.isHost;
    }

    if (data.type === 'addButton') {addButton(data.players, data.ready)}

    if (data.type === 'adding_player') {
        const player = data.player;
        showPlayer(docWrapper, {
            'TourName': player[0],
            'image': player[2],
            'connected': player[1]});
        addButton(data.players, data.ready)
    }

    if (data.type === 'name_taken') {
        createTournamentView();
    }

    if (data.type === 'removing_player') {
        const player = data.player;
        const member = document.getElementById(player);
        let tmp = document.getElementById('start_button');
        if (member) {
            member.remove();
            plCount--;
        }

        if (!data.ready && tmp) tmp.remove();

    }

    if (data.type === 'joining_tournament') {
        const players = data.players;
        players.forEach(player => {showPlayer(docWrapper, player, data.inRoom, tourSocket)});
    }

    if (data.type === 'start_game') {
        p1Image = data.player1_image;
        p2Image = data.player2_image;

        name1 = data.player1_name;
        name2 = data.player2_name;
        docWrapper.innerHTML = "";
        if (isHost) {
            document.addEventListener('keydown', (event) => handleEventDownMulti(event, p1));
            document.addEventListener('keyup', (event) => handleEventUpMulti(event,p1));
        }
        else {
            document.addEventListener('keydown', (event) => handleEventDownMulti(event, p2));
            document.addEventListener('keyup', (event) => handleEventUpMulti(event,p2));
        }
        loadGame(tourSocket);
    }
    if (data.type === 'tourWinner') {
        tourSocket.close();
        loadGame(null);
    }

    if (data.type === 'nextTour') {
        docWrapper.innerHTML = '';
        data.players.forEach(player => showPlayer(docWrapper, player, data.inRoom, tourSocket));
    }
}

function waitForPlayers(PlayerName) {
    if (socket) {
        socket.close();
        setSocket(null);
    }
    let docWrapper = document.getElementById('wrapper');
    docWrapper.innerHTML = '';
    let token = document.getElementById('token-div').getAttribute('data-token');
    if (!token) {token = refreshToken();}
    const sockaddr = `wss://${location.hostname}:8443/ws/tournament/?token=${token}`;
    tourSocket = new WebSocket(sockaddr);
    setSocket(tourSocket);

    plCount = 0;

    tourSocket.onerror = function(event){
       loadGame(null);
    }

    tourSocket.onclose = function(event){
       window.cancelAnimationFrame(window.animeId);
       document.getElementById('wrapper').innerHTML = "";
       setSocket(null);
    }
    
    window.addEventListener('beforeunload', function() {
        if (tourSocket) {
            tourSocket.close();
            setSocket(null);
        }
    });

    tourSocket.onopen = function(event){
       tourSocket.send(JSON.stringify({
           'type': 'adding_player',
           'playername': PlayerName,

       }));
    }

    tourSocket.onmessage = TourMessageHandler;
}

export function resetList(players, inRoom) {
    
    let docWrapper = document.getElementById('wrapper');
    docWrapper.innerHTML = "";
    players.forEach(player => {showPlayer(docWrapper, player, inRoom)});
    // addButton(players, inRoom);Only when backend is ready
}

function addButton(players, ready) {
    if (players.length <= 1) return ;

    const player = document.getElementById(players[1].TourName);
    let tmp = document.getElementById('start_button');
    
    if (ready) {
        if (tmp) tmp.remove();
        const startButton = document.createElement('button');
        startButton.id = "start_button";
        startButton.innerText = 'Start Game';
        startButton.style.display = 'block';
        startButton.style.margin = '10px auto';
        startButton.onclick = function() {
            tourSocket.send(JSON.stringify({'type': 'starting_game'}));
        };
        player.append(startButton);
    }
    else 
        if (tmp) tmp.remove();
}

function showPlayer(docWrapper, player) {
    plCount++;
    const member = document.createElement('li');
    member.id = player.TourName;
    member.style.color = 'white';
    member.style.display = 'flex';
    member.style.alignItems = 'center';
    member.style.marginBottom = '10px';
    member.innerHTML = `
    <img style="border-radius: 50%; width: 50px; height: 50px; margin-right: 10px;" src="${player.image}">
    ${player.TourName}
    <div class="status-indicator">
    <svg height="20" width="20" xmlns="http://www.w3.org/2000/svg">
    <circle r="5" cx="10" cy="10" fill="${player.connected ? 'green' : 'red'}" />
    </svg>
    </div>
    `;
    docWrapper.append(member);
}
