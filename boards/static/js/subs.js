class Subs {
	static get() {
		const c = Cookies.get("subs");

		return c ? JSON.parse(c) : [];
	}

	static set(n) {
		Cookies.set("subs", JSON.stringify(n));
	}

	static push(n) {
		let s = this.get();
		s.push(n);

		this.set(s);
	}

	static remove(n) {
		let s = this.get();
		const ind = s.findIndex((elem) => {return elem.board == n.board && elem.thread == n.thread;});

		if(ind > -1) {
			s.splice(ind, 1);
			this.set(s);
		}

		return ind;
	}

	static contains(n) {
		return this.get().findIndex((elem) => {return elem.board == n.board && elem.thread == n.thread;}) > -1;
	}

	static findIndex(n) {
		return this.get().findIndex((elem) => {return elem.board == n.board && elem.thread == n.thread;});
	}

	static toggle(n) {
		if(this.contains(n)) {
			this.remove(n);
			return 0;
		}
		else {
			this.push(n);
			return 1;
		}
	}

	static modify(n) {
		let ind = this.findIndex(n);

		let l = this.get();

		if(ind > -1) {
			l[ind] = n;
		}
		else {
			l.push(n);
		}

		this.set(l);
	}

	static clean() {
		let a = this.get();
		let uniqueArray = a.filter(function(item, pos) {
			return Subs.findIndex(item) == pos;
		});
		this.set(uniqueArray);	
	}
}

window.addEventListener("DOMContentLoaded", async () => {
	Subs.clean();

	let cont = document.querySelector(".sub-data");
		if(cont) {
		let contInner = cont.querySelector(".sub-data-inner");

		let subs = Subs.get();

		for(let sub of subs) {
			let tCont = document.createElement("div");
			tCont.className = "sub-container";

			let board = document.createElement("h6");
			let title = document.createElement("h4");

			let subB = document.createElement("img");

			subB.className = "subscribe-button small-icon";
			subB.src = "/static/media/unsubscribe.png";
			subB.id = `subscribe_button_${sub.board}_${sub.thread}_inner`;

			const r = await fetch(`/api/board/${sub.board}/thread/${sub.thread}`);
			if(r.status == 404) {
				Subs.remove(sub);
				continue;
			}

			const json = await r.json();

			if(sub.comment_count < json.comment_count) {
				let diff = document.createElement("h5");
				diff.className = "warning";
				diff.innerHTML = `* +${json.comment_count - sub.comment_count}!`;

				if(json.comment_count >= json.bump_limit) {
					diff.innerHTML = `(УТОНУЛ) ${diff.innerHTML}`
				}

				tCont.appendChild(diff);

				Subs.modify({board: sub.board, thread: sub.thread, comment_count: json.comment_count});
			board.innerHTML = json.bo
			}

			board.innerHTML = json.board;
			title.innerHTML = json.title;

			tCont.appendChild(board);
			tCont.appendChild(title);
			tCont.appendChild(subB);

			title.addEventListener("click", () => {
				window.location.href = `/boards/board/${sub.board}/thread/${sub.thread}`;
			});

			contInner.appendChild(tCont);
		}
	}

	let elems = document.querySelectorAll(".subscribe-button");

	for(let elem of elems) {
		const spl = elem.id.split("_");

		const r = await fetch(`/api/board/${spl[2]}/thread/${spl[3]}`);
		if(r.status == 404) {
			Subs.remove({board: spl[2], thread: spl[3]});
			continue;
		}

		const json = await r.json();

		const data = {board: spl[2], thread: spl[3], comment_count: json.comment_count ? json.comment_count : 0};

		if(Subs.contains(data)) {
			let d = elem.src.split("/");
			d[d.length - 1] = "unsubscribe.png";
			elem.src = d.join("/");
		}

		elem.addEventListener("click", () => {
			const s = Subs.toggle(data) == 1;

			let d = elem.src.split("/");

			d[d.length - 1] = s ? "unsubscribe.png": "subscribe.png";

			elem.src = d.join("/");

			if(!s && elem.parentElement && elem.parentElement.className == "sub-container") {
				elem.parentNode.remove();
			}
		});
	}
});
