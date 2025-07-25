function toggleTheme() {
    let b = document.body;
    let e = document.getElementById("theme-toggle");
    const theme = localStorage.getItem("theme");

    if(theme=="dark") {
        localStorage.setItem("theme", "light");
        b.classList.remove("dark-theme");
    }
    else {
        localStorage.setItem("theme", "dark");
        b.classList.add("dark-theme");
    }

    if(e) {
        e.src = e.src.replace(theme=="dark"?"moon.svg":"sun.svg", theme=="dark"?"sun.svg":"moon.svg");
    }
}

function initTheme() {
    let e = document.getElementById("theme-toggle");
    let b = document.body;
    let theme = localStorage.getItem("theme");

    if(theme === "dark") {
        b.classList.add("dark-theme");
        if(e) {
            e.src = e.src.replace("sun.svg", "moon.svg");
        }
    }
}

document.addEventListener("DOMContentLoaded", initTheme);
