function toggleNsfwBlur() {
    let b = document.body;
    let e = document.getElementById("nsfw-toggle");
    const s = Cookies.get("blur-nsfw");

    if(s=="1") {
        Cookies.set("blur-nsfw", "0");
    }
    else {
        Cookies.set("blur-nsfw", "1");
    }

    if(e) {
        e.innerHTML = s=="1" ? "Блюрить NSFW" : "Не блюрить NSFW"
    }
}
