function toggleTheme() {
    let b = document.body;
    let e = document.getElementById("theme-toggle");

    const theme = LocalStorage.get("theme", "light");

    if(theme=="dark") {
        localStorage.setItem("theme", "light");
        b.classList.remove("dark-theme");
    }
    else {
        localStorage.setItem("theme", "dark");
        b.classList.add("dark-theme");
    }

    if(e) {
        e.innerHTML = theme == "dark" ? "Тёмная тема" : "Светлая тема";
    }
}

function initTheme() {
    let e = document.getElementById("theme-toggle");
    let b = document.body;

    let theme = LocalStorage.get("theme", "light");

    if(theme === "dark") {
        b.classList.add("dark-theme");
    }

    if(e) {
        e.innerHTML = theme == "dark" ? "Светлая тема" : "Тёмная тема";
    }
}

document.addEventListener("DOMContentLoaded", initTheme);
