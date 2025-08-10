function toggleNsfwBlur() {
    let b = document.body;
    let e = document.getElementById("nsfw-toggle");
    const s = Cookies.get("blur-nsfw");

    if(s=="1") {
        Cookies.set("blur-nsfw", "0");
        window.location.reload();
    }
    else {
        Cookies.set("blur-nsfw", "1");
        window.location.reload();
    }
}
