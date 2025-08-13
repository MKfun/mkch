function toggleAnimations() {
    let b = document.body;
    let e = document.getElementById("animations-toggle");
    const anims = localStorage.getItem("animations");

    if(anims == "1") {
        localStorage.setItem("animations", "0");
        b.classList.remove("animated");
    }
    else {
        localStorage.setItem("animations", "1");
        b.classList.add("animated");
    }

    if(e) {
        e.innerHTML = anims == "1" ? "Включить анимации" : "Выключить анимации";
    }
}

function initAnimations() {
    let e = document.getElementById("animations-toggle");
    let b = document.body;
    let anims = localStorage.getItem("animations");

    if(anims == "1") {
        b.classList.add("animated");
    }

    if(e) {
        e.innerHTML = anims == "1" ? "Выключить анимации" : "Включить анимации";
    }
}

document.addEventListener("DOMContentLoaded", initAnimations);
