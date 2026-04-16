// Pripojenie na MQTT
const client = new Paho.Client("openlab.kpi.fei.tuke.sk", 443, "player" + Date.now());
client.onMessageArrived = onMessageArrived;
client.connect({onSuccess: onConnect, reconnect: true, useSSL: true, keepAliveInterval: 10, timeout: 10});

function onConnect() {
    client.subscribe("openlab/game/arkanoid/event");
    // Po pripojeni skryjeme sekciu offline a zobrazime online
    document.getElementById("offline").classList.add("hidden");
    document.getElementById("online").classList.remove("hidden");
}

function onMessageArrived(message) {
    const jsonMessage = JSON.parse(message.payloadString);
    const {type, value} = jsonMessage;

    if (type === "start" || type === "win" || type === "fail") {
        document.getElementById("bricks").innerHTML = ""
        changeScreen(type);
    } else if (type === "break") {
        animateBreak(value);
    } else if (type === "hit" && value === "wall" || value === "paddle") {
        animateHit(value);
    }
}

function changeScreen(screen) {
    // Skryjeme vsetky stranky
    document.querySelectorAll("body>div").forEach(elem => elem.classList.add("hidden"));
    // Zobrazime zvolenu stranku
    document.getElementById(screen).classList.remove("hidden");
}

function animateBreak(color) {
    const animatedBrick = document.querySelector(".brick." + color);

    // Spustime animaciu letiacej kocky, viac na https://css-tricks.com/restart-css-animation/
    animatedBrick.classList.remove("animate");
    void animatedBrick.offsetWidth;
    animatedBrick.classList.add("brick", color, "animate");

    // Pridame dalsiu kocku do skore
    const newBrick = document.createElement("div");
    newBrick.classList.add("brick", color);
    document.getElementById("bricks").appendChild(newBrick);
}

function animateHit(item) {
    // Spustime animaciu podla typu narazu (wall alebo paddle)
    const page = document.getElementById("start");
    page.classList.remove("animate-ship-shake", "animate-background");
    void page.offsetWidth;
    page.classList.add(item === "wall" ? "animate-ship-shake" : "animate-background");
}