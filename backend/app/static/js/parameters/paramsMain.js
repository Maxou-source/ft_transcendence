import { csrftoken } from "../main.js";

const mti = (v, i) => {
	v.length ?
		i.classList.add('typed')
	: i.classList.remove('typed');
};

export function goParams() {
	document.getElementById('info-form')
		.addEventListener('submit', updateUserInfos);
	let inputs = document.querySelectorAll('.ctn-inpt input');
	inputs.forEach((input, index) => {
		mti(input.value, input);
		input.addEventListener('change', (e) =>
			mti(e.target.value, input)
		);
	});

	let form = document.querySelector(".ctn-change-form");
	const csrfToken = document.createElement('input');
	csrfToken.type = 'hidden';
	csrfToken.name = 'csrfmiddlewaretoken';
	csrfToken.value = csrfToken;
	form.appendChild(csrfToken);
	
	document.querySelector("#modify-avatar").addEventListener('click', openAvatarModal);
	document.querySelector("#close-avatar").addEventListener('click', closeAvatarModal);
	document.getElementById('avatar-input').addEventListener('change', changeAvatarInput);
}

function openAvatarModal () {
	let avatar = document.getElementById('avatar-modal');
	avatar.classList.add('on');
}

const closeAvatarModal = () => {
	let avatar = document.getElementById('avatar-modal');
	let submit = document.getElementById('submit-avatar-btn');
	let display = document.getElementById('change-avatar-img');

	avatar.classList.remove('on');

	// display.src = '{{ image }}';

	submit.onclick = manageAvatarFocus
	// submit.textContent = 'Modifier'
};

const getCSRFToken = () => {
	return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

export const updateUserInfos = (event) => {
	event.preventDefault();

	let ln = document.getElementById('lname').value;
	let fn = document.getElementById('fname').value;
	let psd = document.getElementById('pseudo').value;

	if (ln === "" || fn === "" || psd === "")
	{
		alert("You can't leave some fields empty !!");
		return ;
	}

	$.ajax({
		url: 'update_profile/',
		type: 'POST',
		data: {
			'pseudo': psd,
			'last_name': ln,
			'first_name': fn,
			'csrfmiddlewaretoken': getCSRFToken()
		},
		success: function(response) {
		},
		error: function(response) {
			console.log('An error occurred');
		}
	});
}

const manageAvatarFocus = () => {
	document.getElementById('avatar-input').click()
}

const makeSubmitAvatar = async () => {
	const response = await fetch(window.blobAvatar);
	const b = await response.blob();

	let f = new FormData();
	f.append('avatar', b);
	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

	const rs = await fetch('upload_avatar/', {
		method: 'POST',
		headers: {
			'X-CSRFToken': csrftoken
		},
		body: f
	})

	const data = await rs.json()
	if (data.ok)    {
		const images = document.querySelectorAll('.ctn-user-img img')
		images.forEach((img, i) => 
			img.src = data.url
		)
		closeAvatarModal();
	}
}


function changeAvatarInput(e) {
	if (e.target.files.length && e.target.files[0]) {
		let display = document.getElementById('change-avatar-img');
		display.src = window.URL.createObjectURL(e.target.files[0]);
		window.blobAvatar = display.src;
		let submit = document.getElementById('submit-avatar-btn');
		submit.textContent = 'Enregistrer';
		submit.onclick = makeSubmitAvatar;
	}
}
