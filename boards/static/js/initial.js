function popWarnings() {
	let warnings = document.querySelectorAll(".js-autopop");
	for(warning of warnings) {warning.remove();}
}

window.addEventListener('DOMContentLoaded', () => {
	popWarnings();
});
