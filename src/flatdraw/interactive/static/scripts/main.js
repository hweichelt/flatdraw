const buttons_node = document.querySelectorAll("button.node");
const buttons_track = document.querySelectorAll(".palette .track");

let brush = undefined;
let brush_button = undefined;

const map = new Map();
const map_x = 10;

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