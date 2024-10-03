import { setSocket, csrftoken, refreshToken, chatSocket, getChatSocket, setChatSocket, showSection} from "../main.js";
import { startOnlineGame } from "../game/loadGame.js";

export async function createChatBox(receiver) {
	let token = document.getElementById('token-div').getAttribute('data-token');
	if (!token) {token = refreshToken();}
	let chatBox = document.createElement("div");
	// creating div that will contain the chat box
	chatBox.classList.add("d-flex", "flex-column", "justify-content-center", "align-items-center", "mt-3");

	const response = await fetch(`home/chatbox`);
	let text = await response.text();
	// fetching the html code that will have the chatbox

	chatBox.id = "whatever";
	// chatBox. = receiver;
	chatBox.innerHTML = text;
	document.getElementById("wrapper").appendChild(chatBox);
	document.querySelector("#csrfinput").setAttribute("value", `${csrftoken}`);
	document.querySelector("#keep").setAttribute("value", receiver);

	const sockaddr = `wss://${location.hostname}:8443/ws/chatroom/?token=${token}`;
	const newChatSocket = new WebSocket(sockaddr);

	setChatSocket(newChatSocket);
	const addReceiver = {
		"addReceiver": receiver
	};


	document.querySelector("#id_body").addEventListener('keydown', function(event) {
		if (event.key === 'Enter') {
			event.preventDefault();
			let inputValue = document.querySelector("#id_body").value;
			const message = {
				body: inputValue,
				timestamp: new Date().toISOString()
			};
			const messageJson = JSON.stringify(message);
			newChatSocket.send(messageJson);
			document.querySelector("#id_body").value = '';
		}   
	});

	document.querySelector("#playWithFriendButton").addEventListener("click", function(event) {
		newChatSocket.close();
		startOnlineGame(null, receiver);
	})

	newChatSocket.onopen = function (event) {
		newChatSocket.send(JSON.stringify(addReceiver));
		newChatSocket.onmessage = function(event) {
			let insert_messages = document.createElement("div");
			insert_messages.id = "text_messages";
			insert_messages.innerHTML = event.data;
			document.querySelector(".messages_list").appendChild(insert_messages);
		};
	}

	newChatSocket.onclose = function (event) {
		closeChatBox();
	}

	window.addEventListener('beforeunload', function() {
		if (newChatSocket)
			newChatSocket.close();
		});
	return newChatSocket;
}

async function closeChatBox() {
	document.getElementById('wrapper').innerHTML = "";
}

export async function sendFriendRequest(id, current_user) {
    let payload = {
        "receiver_user_id": id,
        "sender_user_id": current_user,
    }
    await $.ajax({
        type: "POST",
        dataType: "json",
        url: "/send_friend_request/",
        data: payload,
        headers: {
            'X-CSRFToken': csrftoken,
			'token': csrftoken
        },
        success: function(data) {
            if (data['response'] == "Friend request sent.") {
                updateFriendsList(current_user, data.receiver, 'add');
            }
        },
        error: function(data) {
            console.error("Error:", data);
        }
    });
}

function removeFriendRequest(id, current_user) {
	let payload = {
		"receiver_user_id": id,
		"sender_user_id": current_user,
	}
	$.ajax({
		type: "POST",
		dataType: "json",
		url: "/remove_friend_request/",
		data: payload,
		headers: {
			'X-CSRFToken': csrftoken
		},
		success: function(data) {
			if (data['response'] == "Friend removed.") {
				updateFriendsList(current_user, data.receiver, 'remove');
			}
		},
		error: function(data) {
			console.error("Error:", data);
		}
	});
}

function blockUser(id, current_user)
{
	let payload = {
		"user_getting_blocked": id,
		"user_blocking": current_user,
	}
	$.ajax({
		type: "POST",
		dataType: "json",
		url: "/block_user/",
		data: payload,
		headers: {
			'X-CSRFToken': csrftoken
		},
		success: function(data) {
		},
		error: function(data) {
			console.log("Error", data);
		}
	})
}

function handleRemoveFriend(button) {
    const userId = button.getAttribute('data-user-id');
    const currentUser = button.getAttribute('data-current-user');
    removeFriendRequest(userId, currentUser);
}

function clickRemoveFriendEventListener(event) {
    handleRemoveFriend(event.currentTarget);
}

function handleChatButtonClick(button) {
    let chat = document.getElementById("chat-container");
    let previousId = document.querySelector("#keep");

    const userId = button.getAttribute('data-user-id');
    const currentUser = button.getAttribute('data-current-user');

    if (previousId && previousId.getAttribute("value") !== userId) {
        deleteChatBox();
        createChatBox(userId);
    } else if (!chat) {
        createChatBox(userId);
    }
}

function chatClickEventListener(event) {
    handleChatButtonClick(event.currentTarget);
}

export function updateFriendsList(current_user, friends, action) {
    const friendsList = document.querySelector('.column:nth-child(2) ul');
    const connectedUsersList = document.querySelector('.column:nth-child(1) ul');

    if (action === 'add') {
		friends.forEach(friend => {
			const friendItem = document.createElement('li');
            friendItem.style.color = 'white';
            friendItem.style.display = 'flex';
            friendItem.style.alignItems = 'center';
            friendItem.style.marginBottom = '10px';
            friendItem.innerHTML = `
			<img style="border-radius: 50%; width: 50px; height: 50px; margin-right: 10px;" src="${friend.image}">
			${friend.pseudo}
			<button name="rem-friends-button" class="button" data-user-id="${friend.id42}" data-current-user="${current_user}">
			<svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
			<rect x="4" y="10" width="16" height="4"/>
			</svg>
			</button>
            <button name="chat-friends-button" class="button" data-user-id="${friend.id42}"  data-chat-rooms="${friend.chatroom}" 
                data-current-user="${current_user.id42}">
                <svg fill="#000000" height="800px" width="800px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
                    viewBox="0 0 60 60" xml:space="preserve">
                <path d="M30,1.5c-16.542,0-30,12.112-30,27c0,5.205,1.647,10.246,4.768,14.604c-0.591,6.537-2.175,11.39-4.475,13.689
                    c-0.304,0.304-0.38,0.769-0.188,1.153C0.276,58.289,0.625,58.5,1,58.5c0.046,0,0.093-0.003,0.14-0.01
                    c0.405-0.057,9.813-1.412,16.617-5.338C21.622,54.711,25.738,55.5,30,55.5c16.542,0,30-12.112,30-27S46.542,1.5,30,1.5z"/>
                </svg>
            </button>
            <div class="status-indicator">
            <svg height="20" width="20" xmlns="http://www.w3.org/2000/svg">
            <circle r="5" cx="10" cy="10" fill="${friend.connected ? 'green' : 'red'}" />
            </svg>
            </div>
            `;
            friendsList.appendChild(friendItem);
			
			document.querySelectorAll(`[data-user-id="${friend.id42}"]`).forEach(button => {
				if (button.name === "add-friends-button") {
					button.closest('li').remove();
				}
			});
            // Remove the friend from the connected users list
        });
		if (document.querySelectorAll('button[name="chat-friends-button"]').length > 1)
		{
			document.querySelectorAll('button[name="rem-friends-button"]').forEach(button => button.removeEventListener('click', clickRemoveFriendEventListener))
			document.querySelectorAll('button[name="chat-friends-button"]').forEach(button => button.removeEventListener('click', chatClickEventListener))
		}
		document.querySelectorAll('button[name="rem-friends-button"]').forEach(button => {
			button.addEventListener('click', clickRemoveFriendEventListener);
		});
		document.querySelectorAll('button[name="chat-friends-button"]').forEach(button => {

			button.addEventListener('click', chatClickEventListener);
		});
    } else if (action === 'remove') {
        friends.forEach(friend => {
            // Remove the friend from the friends list
            document.querySelectorAll(`[data-user-id="${friend.id42}"]`).forEach(button => {
                if (button.name === "rem-friends-button") {
                    button.closest('li').remove();
                }
            });

            // Add the friend back to the connected users list
            const userItem = document.createElement('li');
            userItem.style.color = 'white';
            userItem.style.display = 'flex';
            userItem.style.alignItems = 'center';
            userItem.style.marginBottom = '10px';
            userItem.innerHTML = `
                <img style="border-radius: 50%; width: 50px; height: 50px; margin-right: 10px;" src="${friend.image}">
                ${friend.pseudo}
                <button name="add-friends-button" class="button" data-user-id="${friend.id42}" data-current-user="${current_user}">
                    <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <rect x="10" y="4" width="4" height="16"/>
                        <rect x="4" y="10" width="16" height="4"/>
                    </svg>
                </button>
				<div class="status-indicator">
                <svg height="20" width="20" xmlns="http://www.w3.org/2000/svg">
                    <circle r="5" cx="10" cy="10" fill="${friend.connected ? 'green' : 'red'}" />
                </svg>
                </div>
            `;
            connectedUsersList.appendChild(userItem);
            document.querySelectorAll('button[name="add-friends-button"]').forEach(button => {
                button.addEventListener('click', () => {
					const userId = button.getAttribute('data-user-id');
                    const currentUser = button.getAttribute('data-current-user');
                    sendFriendRequest(userId, currentUser);
                });
            });
        });
    }
}

export function deleteChatBox() {
	let chatB = document.getElementById("whatever");
	chatB.remove();
	showSection('friends', false);
	let socket = getChatSocket();
	socket.close();
	setSocket(null);
}

export function goFriends() {
    document.querySelectorAll('button[name="add-friends-button"]').forEach(button => {
        button.addEventListener('click', () => {
            const userId = button.getAttribute('data-user-id');
            const currentUser = button.getAttribute('data-current-user');
            sendFriendRequest(userId, currentUser);
        });
    });

    document.querySelectorAll('button[name="rem-friends-button"]').forEach(button => {
        button.addEventListener('click', clickRemoveFriendEventListener);
    });
    document.querySelectorAll('button[name="chat-friends-button"]').forEach(button => {

        button.addEventListener('click', chatClickEventListener);
    });

    document.querySelectorAll('button[name="block-user"]').forEach(button => {
        button.addEventListener('click', async () => {
            const userId = button.getAttribute('data-user-id');
            const currentUser = button.getAttribute('data-current-user');

            blockUser(userId, currentUser);
            
            button.value = "blocked";
            button.textContent = "blocked";
        });
    });

}
