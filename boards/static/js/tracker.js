class Tracker {
	constructor(threadDiv=".thread-tracker", updateBtn=".tracker-update", trackerURL=null){
		this.trackerURL = trackerURL ? trackerURL : window.location.href;

		this.threadDiv = threadDiv;

		this.el = document.querySelector(threadDiv);
		this.updateBtn = document.querySelector(updateBtn);

		this.threadsNow = this.el.children.length;

		this.updateTimer = 60;
		this.timerNow = this.updateTimer;

		let cd = () => {
			let upd = () => {
				this.timerNow--;
				if(this.timerNow <= 0) {
					this.timerNow = this.updateTimer;
					this.update();
				}

				this.updateBtn.innerHTML = `Обновить (${this.timerNow} с.)`;
			};

			return upd;
		};

		this.countdown = cd();

		this.params = new URLSearchParams({
			order_by: "-creation",
			max_num: 10
		});
	}

	forceUpdate() {
		this.timerNow = 0;
	}

	setUpdateInterval(i) {
		this.updateTimer = i;
		this.timerNow = i;
	}

	setUpdateParams(form) {
		this.params.set("max_num", form.querySelector(".select-max_num").value);

		console.log(this.params.toString());

		while(this.el.firstChild) {this.el.removeChild(this.el.firstChild);}
		this.threadsNow = 0;
		this.forceUpdate();
		this.update();
	}

	async update() {
		console.log("update");
			
		const text = await((await fetch(this.trackerURL + '?' + this.params.toString())).text());

		const parser = new DOMParser();
		const list = parser.parseFromString(text, 'text/html');

		const threads = list.querySelector(this.threadDiv);
		const threads_o = document.querySelector(this.threadDiv);

		const threads_inner_f = threads.querySelectorAll(".mini-thread");
		let threads_inner = threads_o.querySelectorAll(".mini-thread");

		const maxn = this.params.get("max_num");

		for(let i = 0; i < threads_inner_f.length && i < maxn; i++) {
			let thread_inner = threads_inner.length>=i+1?threads_inner[i]:null;
			let thread_inner_f = threads_inner_f[i];

			if(!thread_inner) {
				threads_o.appendChild(thread_inner_f);
			}
			else if(thread_inner.innerHTML != thread_inner_f.innerHTML) {
				thread_inner.innerHTML = thread_inner_f.innerHTML;
			}

			threads_inner = threads_o.querySelectorAll(".mini-thread");
		}
	}
}
