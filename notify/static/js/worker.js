self.addEventListener('install', function(e) {
	console.log("ASDASDASD");
	self.skipWaiting();
});

self.addEventListener('push', function(e) {
	try {
		const response_json = e.data.json();
		const title = response_json['title'];
		const message = response_json['message'];
		const message_tag = response_json['tag'];
		console.log(0);
	}
	catch(err) {
		const title = "";
		const message = event.data.text();
		const message_tag = "";
		console.log(1);
	}

	self.registration.showNotification("MKCH", {
		body: "Мое имя - Гомер Джей Симп-сон. Я - единственный сверхчеловек, Я - супермен без страха и упрека, Я - креативная сила планеты, Я - знамя запада и востока.",
		icon: '/static/notify_icon.png',
		tag: "porn",
		vibrate: [200, 100, 200, 100, 200, 100, 200]
	});
});
