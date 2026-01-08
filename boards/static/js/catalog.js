function updateCatalogButton() {
    const btn = document.getElementById("catalog-toggle");
    if (!btn) return;

    if (Cookies.get("default-catalog") === "1") {
        btn.innerText = "Список тредов по умолчанию";
    } else {
        btn.innerText = "Каталог по умолчанию";
    }
}

function toggleCatalogSetting() {
    if (Cookies.get("default-catalog") === "1") {
        Cookies.remove("default-catalog", { path: '/' });
    } else {
        Cookies.set("default-catalog", "1", { expires: 365, path: '/' });
    }
    updateCatalogButton();
}

document.addEventListener("DOMContentLoaded", () => {
    updateCatalogButton();
});
