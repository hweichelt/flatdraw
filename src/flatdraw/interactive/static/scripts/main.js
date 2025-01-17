const buttons_node = document.querySelectorAll("button.node");
const buttons_track = document.querySelectorAll(".palette .track");

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
map_element.style.width = `${map_width}px`;
map_element.style.height = `${map_height}px`;
map_element.style.gridTemplateColumns = `repeat(${map_x},1fr)`;
map_element.style.gridTemplateRows = `repeat(${map_y},1fr)`;

main.addEventListener("mousedown", event => {
    if(event.button === 1){
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
    if(event.button === 1) {
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
});

buttons_track.forEach((button, i) => {
    button.addEventListener("click", event => {
        event.preventDefault();
        set_brush_button(button);
    });
});

buttons_node.forEach((button, i) => {
    const button_x = i % map_x;
    const button_y = Math.floor(i / map_x);
    button.addEventListener("click", event => {
       event.preventDefault();
       if(brush) {
           set_node_value(button_x, button_y, brush);
           update_node(button_x, button_y);
       }
    });
    set_node_value(button_x, button_y, "0");
    update_node(button_x, button_y);
});

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