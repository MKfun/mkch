function toggleAnimations() {
    let b = document.body;
    let e = document.getElementById("animations-toggle");
    const anims = LocalStorage.get("animations", "1");

    if(anims == "1") {
        LocalStorage.set("animations", "0");
        b.classList.remove("animated");
    }
    else {
        LocalStorage.set("animations", "1");
        b.classList.add("animated");
    }

    if(e) {
        e.innerHTML = anims == "1" ? "Включить анимации" : "Выключить анимации";
    }
}

function initAnimations() {
    let e = document.getElementById("animations-toggle");
    let b = document.body;
    let anims = LocalStorage.get("animations", "1");

    if(anims == "1") {
        b.classList.add("animated");
    }

    if(e) {
        e.innerHTML = anims == "1" ? "Выключить анимации" : "Включить анимации";
    }
}

document.addEventListener("DOMContentLoaded", initAnimations);
