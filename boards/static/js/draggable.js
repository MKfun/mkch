function makeDraggable(element) {
    let p0, p1, p2, p3 = 0;
    let scale = 1.0;

    let eh = document.getElementById(element.id + "-header");

    if(eh) {
        eh.addEventListener("mousedown", dragMouseDown);
        eh.addEventListener("wheel", scaleDraggable);
    }
    else {
        element.addEventListener("mousedown", dragMouseDown);
        element.addEventListener("wheel", scaleDraggable);
    }

    function closeDraggable(e) {
        e = e || window.event;
        e.preventDefault();

        closeDragEvent();
        element.remove();
    }

    function scaleDraggable(e) {
        e.preventDefault();

        scale += e.deltaY * -0.001;
        scale = Math.min(Math.max(0.125, scale), 4);
        element.style.transform = `scale(${scale})`;
    }

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();

        if(e.button === 1){closeDraggable();}

        p2 = e.clientX;
        p3 = e.clientY;

        document.addEventListener('mouseup', closeDragEvent);
        document.addEventListener('mousemove', elementDrag);
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();

        p0 = p2 - e.clientX;
        p1 = p3 - e.clientY;
        p2 = e.clientX;
        p3 = e.clientY;

        element.style.top = (element.offsetTop - p1) + "px";
        element.style.left = (element.offsetLeft - p0) + "px";
    }

    function closeDragEvent() {
        document.removeEventListener('mouseup', closeDragEvent);
        document.removeEventListener('mousemove', elementDrag);

        mouseUp = null;
        mousemove = null;
    }
}

function createImageFloatingDiv(imgId) {
    let width = screen.width;
    let iorg = document.getElementById(imgId);

    if(width < 640) {
    	window.location.href = iorg.src;
    }
    else {
	    let d = document.createElement("div");
	    let h = document.createElement("div");

	    d.appendChild(h);

	    d.id = `floatingdiv_${imgId}`;
	    d.className = "draggable";
	    const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const topOffset = 50;
	    d.style.left = "35%";
	    d.style.top = `${scrollTop + topOffset}px`

	    h.className = "draggable-header";

	    let i = document.createElement("img");
	    i.className = "floating-image"
	    i.src = iorg.src;

	    t = document.createElement("h1");
	    t.className = "draggable-header-text";
	    t.innerHTML = i.src.length > 40 ? i.src.substring(0, 40) + "..." : i.src;
	    h.appendChild(t);

	    d.appendChild(i);

	    document.body.appendChild(d);
	    makeDraggable(d);
    }
}
