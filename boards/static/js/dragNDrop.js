const allowedFileTypes = ["image", "video"]

function dragover_handler(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
}

function drop_handler(e) {
    e.preventDefault();

    const files = e.dataTransfer.files;
    for(let file of files) {
        if(!allowedFileTypes.some(r => file.type.includes(r))){dragleave_handler(e); alert("Загружен файл с недопустимым форматом."); return;}
    }

    e.target.files = files;

    dragleave_handler(e);
}

function dragenter_handler(e) {
    e.preventDefault();

    e.target.classList.add("dragndrop");
}

function dragleave_handler(e) {
    e.preventDefault();

    e.target.classList.remove("dragndrop");
}
