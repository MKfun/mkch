function createDateToolTipListeners() {
	let elems = document.querySelectorAll(".post-date");

	for(let elem of elems) {
		let date_detail = elem.querySelector(".date-detail");

		elem.addEventListener("mouseenter", (e) => {
			date_detail.hidden = false;

			date_detail.style.left = e.pageX + "px";
			date_detail.style.top = e.pageY + "px";
		});

		elem.addEventListener("mouseleave", () => {
			date_detail.hidden = true;
		});
	}
}

if(navigator.maxTouchPoints <= 1) {
	window.addEventListener("load", () => {
		createDateToolTipListeners();
	});
}
