// также известен как popup.js

function createToolTipListener(elemObj) { // парс треда и создание попапа
	for(let element of elemObj.querySelectorAll(".reply")) {
		const linkobj = element.querySelector(".replylnk");
		const hrefobj = document.querySelector("#" + linkobj.href.split("#")[1]);

		let cont = elemObj.querySelector(".reply-container");

		element.addEventListener('mouseenter', (e) => {
			let flothr = document.createElement("div");
			flothr.className = "floating-thread";

			let post_header = document.createElement("div");
			post_header.className = "post-header";
			post_header.id = `floating_${hrefobj.id}`;

			let hrefobjFiles = hrefobj.querySelector(".comment-files");
			if(hrefobjFiles) {
				let fcount = document.createElement("h4");
				fcount.innerHTML = `файлов прикреплено: ${hrefobjFiles.childElementCount}`;
				post_header.appendChild(fcount);
			}

			let flohead = document.createElement("h3");
			flohead.className = "floating-title";
			post_header.appendChild(flohead);

			let flotext = hrefobj.querySelector(".post-message").cloneNode(true);
			flotext.className = "floating-text";
			post_header.appendChild(flotext);

			let replies = document.createElement("div");
			replies.className = "replies";

			let reply_container = document.createElement("div");
			reply_container.className = "reply-container";
			post_header.appendChild(reply_container);

			flohead.innerHTML = hrefobj.querySelector(".header-data").innerHTML;

			let rlist = hrefobj.parentNode.querySelector(".replies");

			if(rlist) {
				replies.innerHTML = rlist.innerHTML;
				post_header.appendChild(replies);
			}

			for(let lnk of post_header.querySelectorAll(".reply")) {
				const r = lnk.querySelector(".replylnk").href.split("#")[1];

				if(elemObj.querySelector(".post-header").id.endsWith(r)) {lnk.className = "reply-not-interactible";}
			}

			for(let r of flothr.querySelectorAll(".floating-thread")) {
				r.remove(); // баг: рекурсивное открытие ссылок на ссылки. Решение: удаление попапов в открываемых ссылках. Если кто знает лучше - жду ПР.
			}
			flothr.appendChild(post_header);

			// первый открываемый коммент позиционируем по координатам страницы. В следующих координаты считаются уже относительно рута самого попапа.
			const rect = elemObj.getBoundingClientRect(); // господи какой же это костыль

			flothr.style.left = (elemObj.className == "floating-thread" ? (e.clientX - rect.left) : e.pageX) + "px";
			flothr.style.top = (elemObj.className == "floating-thread" ? (e.clientY - rect.top) : e.pageY) + "px";

			cont.appendChild(flothr);

			createToolTipListeners([flothr]); // возможность наводиться на ссылки внутри попапов возникших от наведения на ссылку.
		});

		element.addEventListener("mouseleave", (e) => {
			let elems = cont.querySelectorAll(".floating-thread");

			let timeout = setTimeout(() => {elems.forEach((el) => {el.remove();});}, 1000);

			elems.forEach((el) => {
				el.addEventListener("mouseenter", () => {
					clearTimeout(timeout);
					elems.forEach((elem) => {elem.addEventListener("mouseleave", (ev) => {ev.target.remove();});});
				});
			});
		});
	}
}

function createToolTipListeners(elementSet = null) {
	if(!elementSet) {
		elementSet = document.querySelectorAll(".post");
	}

	for(let element of elementSet) {
		createToolTipListener(element);
	}
}

if(navigator.maxTouchPoints <= 1) { // это район для ПК юзеров, и тебе здесь не место!!!
	window.addEventListener('load', () => {
		createToolTipListeners();
	});
}
