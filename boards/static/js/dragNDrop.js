const allowedFileTypes = ["image", "video"];

function showPreview(inputElement, files) {
    let previewContainer = document.getElementById('file-preview');
    if (!previewContainer) {
        previewContainer = document.createElement('div');
        previewContainer.id = 'file-preview';
        previewContainer.className = 'thread-file';
        previewContainer.style.marginTop = '10px';
        inputElement.parentNode.appendChild(previewContainer);
    }

    previewContainer.innerHTML = '';

    Array.from(files).forEach(file => {
        if (!allowedFileTypes.some(r => file.type.includes(r))) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            let element;
            if (file.type.includes('image')) {
                element = document.createElement('img');
            } else if (file.type.includes('video')) {
                element = document.createElement('video');
                element.controls = false; 
                element.autoplay = true;
                element.loop = true;
                element.muted = true;
            }

            if (element) {
                element.src = e.target.result;
                element.className = 'thread-image'; 
                element.style.maxWidth = '150px';  
                element.style.maxHeight = '150px';
                element.style.marginRight = '10px';
                element.style.objectFit = 'contain';
                previewContainer.appendChild(element);
            }
        };
        reader.readAsDataURL(file);
    });
}

function dragover_handler(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
}

function drop_handler(e) {
    e.preventDefault();
    const files = e.dataTransfer.files;

    for (let file of files) {
        if (!allowedFileTypes.some(r => file.type.includes(r))) {
            dragleave_handler(e);
            alert("Загружен файл с недопустимым форматом.");
            return;
        }
    }

    e.target.files = files; 
    dragleave_handler(e);
    
    showPreview(e.target, files);
}

function dragenter_handler(e) {
    e.preventDefault();
    e.target.classList.add("dragndrop");
}

function dragleave_handler(e) {
    e.preventDefault();
    e.target.classList.remove("dragndrop");
}

document.addEventListener('DOMContentLoaded', () => {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            showPreview(e.target, e.target.files);
        });
    });
});
