class LocalStorage {
	static get(key, set) {
		let v = localStorage.getItem(key);
		if(!v && set){v = set; localStorage.setItem(key, set);}

		return v;
	}

	static set(key, val) {
		localStorage.setItem(key, val);
	}
}
