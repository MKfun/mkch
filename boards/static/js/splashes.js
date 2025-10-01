function setDevSplash() {
	const splashes = ['Наши живчики', 'К вашим услугам', 'Компания пацанов', 
                    'Для вас старались', 'Доска почёта', 'Спасибо нашим поварам'];
	let random = Math.floor(Math.random() * splashes.length);
	let title = document.querySelector(".dev-team h2");
	title.textContent = splashes[random];
}