const buttons_node = document.querySelectorAll(".node-wrapper");
const buttons_track = document.querySelectorAll(".palette .track");
const button_save = document.getElementById("save-button");

let brush = undefined;
let brush_button = undefined;

const main = document.querySelector("main");
const map_element = main.querySelector(".map");
const map = new Map();
const map_x = Number.parseInt(map_element.querySelector("input[name=x]").value);
const map_y = Number.parseInt(map_element.querySelector("input[name=y]").value);
let map_scale = 1;
let map_width;
let map_height;
const map_offset = 50;
const zoom_delta = 0.1;
let map_shift_x = 0;
let map_shift_y = 0;
let map_shift_old_x = 0;
let map_shift_old_y = 0;
let dragging = false;
let drag_origin_x = 0;
let drag_origin_y = 0;
let pressing_mouse_0 = false;
let draw_mode = "tracks";

const form_save = document.getElementById("save-form");


document.querySelectorAll("input[type=hidden].loaded").forEach(node => {
    map.set(Number.parseInt(node.name), node.value)
});

document.addEventListener('keydown', event => {
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        if(button_save.disabled){
            form_save.querySelector("input[type=text]").focus();
        } else{
            button_save.click();
        }
    }
});

document.getElementById("output-button").addEventListener("click", event => {
    open_output_dir();
});
form_save.addEventListener("change", event => {
    update_save_button();
})
form_save.querySelector("input[type=text]").addEventListener("input", event => {
    update_save_button();
});
form_save.addEventListener("submit", event => {
    event.preventDefault();
    save_map();
});

document.getElementById("add-train-button").addEventListener("click", event => {set_draw_mode("train")})

const map_aspect_ratio = map_x / map_y;
if(map_aspect_ratio >= 1){
    // landscape
    map_width = main.getBoundingClientRect().width - map_offset;
    map_height = map_width / map_aspect_ratio;
} else {
    //portrait
    map_height = main.getBoundingClientRect().height - map_offset;
    map_width = map_height * map_aspect_ratio;
}
if(map_height > main.getBoundingClientRect().height - map_offset) {
    // scale to max height of main
    const height_offset = main.getBoundingClientRect().height - map_offset;
    const scale_adjustment = height_offset / map_height;
    map_height = map_height * scale_adjustment;
    map_width = map_width * scale_adjustment;
}

map_element.style.width = `${map_width}px`;
map_element.style.height = `${map_height}px`;
map_element.style.gridTemplateColumns = `repeat(${map_x},1fr)`;
map_element.style.gridTemplateRows = `repeat(${map_y},1fr)`;

main.addEventListener("mousedown", event => {
    event.preventDefault();
    if (event.button === 0) {
        pressing_mouse_0 = true
    } else if(event.button === 1){
        drag_origin_x = event.screenX;
        drag_origin_y = event.screenY;
        dragging = true;
    }
});
main.addEventListener("mousemove", event => {
    if (dragging){
        const diff_x = event.screenX - drag_origin_x;
        const diff_y = event.screenY - drag_origin_y;
        map_shift_x = (diff_x / 750);
        map_shift_y = (diff_y / 750);
        const shift_x = map_shift_old_x + map_shift_x;
        const shift_y = map_shift_old_y + map_shift_y;
        map_element.style.transform = `translate(${-50 + shift_x * 50}%,${-50 + shift_y * 50}%)`;
    }
})
main.addEventListener("mouseup", event => {
    if (event.button === 0) {
        pressing_mouse_0 = false
    } else if(event.button === 1) {
        map_shift_old_x = map_shift_old_x + map_shift_x;
        map_shift_old_y = map_shift_old_y + map_shift_y;
        dragging = false;
    }
});

main.addEventListener("wheel", (event) => {
    const direction = Math.sign(event.wheelDelta);
    const new_map_scale = map_scale + direction * zoom_delta;
    if(new_map_scale >= 0.8){
        map_scale = new_map_scale
    }
    map_element.style.width = `${map_width * map_scale}px`;
    map_element.style.height = `${map_height * map_scale}px`;
    map_element.style.setProperty('--grid-enabled',(map_scale >= 1)? "1": "0");
});

buttons_track.forEach((button, i) => {
    button.addEventListener("click", event => {
        event.preventDefault();
        set_brush_button(button);
    });
});

map_element.addEventListener("click", event => {
    event.preventDefault();
    if(draw_mode === "tracks"){
        draw(event.target.closest(".map"), event.clientX, event.clientY)
    }
});
map_element.addEventListener("mousemove", event => {
    event.preventDefault();
    if(pressing_mouse_0){
        if(draw_mode === "tracks") {
            draw(event.target.closest(".map"), event.clientX, event.clientY)
        }
    }
})

function draw(map, client_x, client_y,){
    const rect = map.getBoundingClientRect();
        const x = client_x - rect.left;
        const y = client_y - rect.top;
        const node_width = rect.width / map_x;
        const node_height = rect.height / map_y;
        const node_x = Math.floor(x / node_width);
        const node_y = Math.floor(y / node_height);
       if(brush) {
           set_node_value(node_x, node_y, brush);
           update_node(node_x, node_y);
        }
}

function set_node_value(x, y, value) {
    const button_id = x + y * map_x;
    map.set(button_id, value);
}


function update_node(x, y) {
    const button_id = x + y * map_x;
    const button = buttons_node[button_id];
    const node_value = map.get(button_id);

    // button.innerHTML = node_value;
    button.className = "node"
    button.classList.add(`t-${node_value}`)
    button.classList.add("t-sprite")
}

function set_brush_button(new_button){
    brush = new_button.querySelector("input[type=hidden]").value;
    if(brush_button){
        brush_button.classList.remove("selected");
    }
    new_button.classList.add("selected");
    brush_button = new_button;
}

function set_draw_mode(mode){
    draw_mode = mode;
    main.className = ""
    main.classList.add(`draw-mode-${mode}`)
}

function update_save_button() {
    const filename = form_save.querySelector("input[type=text]").value;
    const export_lp = form_save.querySelector("input[name=export-lp]").checked;
    const export_png = form_save.querySelector("input[name=export-png]").checked;
    button_save.disabled = !(filename.length > 0 && (export_lp || export_png));
}

function save_map(){
    document.body.classList.add("saving");

    const actual_tracks = [...map].filter(([k, v]) => v !== 0 );

    let data = new FormData()
    data.append("map", JSON.stringify(Object.fromEntries(map)));
    data.append("filename", form_save.querySelector("input[name=filename]").value);
    data.append("export-lp", `${+ form_save.querySelector("input[name=export-lp]").checked}`);
    data.append("export-png", `${+ form_save.querySelector("input[name=export-png]").checked}`);
    data.append("width", map_x.toString());
    data.append("height", map_y.toString());
    fetch("/editor/save", {
        "method": "POST",
        "body": data,
    }).then(
        // artificial 1sec timeout
        () => new Promise(resolve => setTimeout(resolve, 1000)).then(
            () => {document.body.classList.remove("saving")}
        )
    )
}

function open_output_dir() {
    fetch("/editor/open_output_dir").then();
}