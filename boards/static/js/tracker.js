class ThreadTracker {
	constructor(element_selector=".thread-tracker", timerSelector=".thread-tracker-timer", formSelector=".thread-tracker-form", maxThreads=50, sTillUpdate=30) {
		this.el = document.querySelector(element_selector);
		this.formField = document.querySelector(formSelector);
		this.updateTimerBtn = document.querySelector(timerSelector);
		this.maxThreads = maxThreads;
		this.lastLen = 0;
		this.sTillUpdate = sTillUpdate;
		this.ordering = "-creation";
		this.boards = [];

		let gtu = () => {
			let so = sTillUpdate;
			let s = sTillUpdate;
			let r = (newTimer = 0) => { // замыкание
				if(newTimer > 0) {
					so = newTimer;
					s = newTimer;
					return {update: true, sTillUpdate: so};
				}

				s--;
				if(s <= 0) {s = so; return {update: true, sTillUpdate: so};}
				else {return {update: false, sTillUpdate: s};}
			};

			return r;
		};

		this.tickUpdate = gtu(); // https://developer.mozilla.org/ru/docs/Web/JavaScript/Guide/Closures

		setInterval(()=>{this.updateTimer()}, 1000);

		this.updateTimerBtn.addEventListener('click', (_) => { // сразу после обновления таймера внесрочно вызывается тик, если вам это не нужно - уберите вызов updateTimer.
			this.resetTimer();
			this.updateTimer();

			this.update();
		});

		this.formField.addEventListener('submit', (e) => {
			e.preventDefault();
			this.processVarUpdate();
		});
	}

	// вызывается при обновлении формы конфигурации. Не рекомендуется вызывать просто так.
	// возвращает: НИЧЕГО!
	processVarUpdate() {
		let data = new FormData(this.formField);

		let updateT = parseInt(data.get("update_delay"));
		let maxT = parseInt(data.get("max_threads"));
		let ordering = data.get("ordering");
		let board = data.get("board_code");

		this.ordering = ordering;

		if(board !== "") {
			this.addBoard(board);
		}

		if(maxT != NaN) {
			console.log(`Max threads is now ${maxT}`)
			this.maxThreads = maxT;
			this.clearHistory();
			this.update();
		}

		if(updateT != NaN) {
			console.log(`New interval is now ${updateT}`);
			this.setUInterval(updateT);
		}
	}

	// добавляет борду в отмеченные для отслеживания.
	// возвращает: true если борда была добавлена, false в ином случае (борда уже была в списке)
	addBoard(code) {
		if(this.boards.indexOf(code) === -1){
			this.boards.push(code);

			let d = document.querySelector(".thread-tracker-boards");
			let t = document.createElement("h4");
			t.innerHTML = ` /${code}/ `;

			d.appendChild(t);

			return true;
		}
		return false;
	}

	// удаляет борду из отмеченных для отслеживания.
	// возвращает: true если борда была удалена, false в ином случае (борды не было в списке)
	delBoard(code) {
		let ind = this.boards.indexOf(code);
		if(ind === -1){
			return false;
		}

		this.boards.splice(ind, 1);
		return true;
	}

	// возвращает: интервал обновления контента
	getUInterval() {
		return this.sTillUpdate;
	}

	// задаёт интервал обновления контента и сбрасывает текущий отсчёт. (n - целое число секунд интервала)
	// возвращает: новый интервал обновления контента
	setUInterval(n) {
		this.sTillUpdate = n;
		this.tickUpdate(n); // смотрите конструктор.

		return this.getUInterval();
	}

	// возвращает: максимальное количество тредов в истории
	getMaxThreads() {
		return this.maxThreads;
	}

	// задаёт: максимальное количество тредов в истории
	// возвращает: новое максимальное количество тредов в истории
	setMaxThreads(n) {
		this.maxThreads = n;
		return this.getMaxThreads();
	}

	// обновляет таймер и, если он истёк, вызывает обновление списка тредов.
	// возвращает: НИЧЕГО!
	updateTimer() {
		let tick = this.tickUpdate();

		if(tick.update) {
			this.update();
		}

		this.updateTimerBtn.innerHTML = `Обновить (${tick.sTillUpdate} с.)`;
	}

	// сбрасывает таймер в начальное состояние.
	// возвращает: НИЧЕГО!
	resetTimer() {
		this.tickUpdate(this.sTillUpdate);
	}

	// удаляет все посты с трекера и устанавливает lastLen в 0
	// возвращает: НИЧЕГО!
	clearHistory() {
		while(this.el.firstChild) {
			this.el.removeChild(this.el.firstChild);
		}

		this.lastLen = 0;
	}

	async update() {
		let threads = await (await fetch(`/api/threads/?ordering=${this.ordering}&format=json`)).json();

		let tl = threads.length;
		if(threads.length > this.maxThreads) {
			threads = threads.slice(0, this.maxThreads);
		}

		if(tl > this.lastLen) {
			for(let i = 0; i < Math.min(this.maxThreads, tl - this.lastLen); i++) {
				let thread = threads[threads.length-1-i];
				if(!thread) {console.warn(`thread ${i} is null!`); continue;}

				let elp = document.createElement("div");
				elp.className = "tracker-entry";

				let elt = document.createElement("h2");
				let eld = document.createElement("h3");

				elt.innerHTML = thread.title;
				eld.innerHTML = thread.text;

				elp.appendChild(elt);
				elp.appendChild(eld);

				if(this.el.firstChild) {
					this.el.insertBefore(elp, this.el.firstChild);
				}
				else {
					this.el.appendChild(elp);
				}

				if(this.lastLen > 0) {
					this.el.removeChild(this.el.children[this.el.children.length-1]);
				}
			}

			this.lastLen = tl;
		}
	}
};

window.addEventListener('load', () => {
	let tracker = new ThreadTracker();
	tracker.update();
});
