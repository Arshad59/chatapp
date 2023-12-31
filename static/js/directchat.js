console.log("Js check from directchat.js");

// Retrieving room.name from html template tags and passing it to roomName.
const private_room_id = JSON.parse(document.getElementById('private_room_id').textContent);

// Initialize variables based on the html elements.
let chatLog = document.querySelector("#chatLog");
let chatMessageInput = document.querySelector("#chatMessageInput");
let chatMessageSend = document.querySelector("#chatMessageSend");
let onlineUsersSelector = document.querySelector("#onlineUsersSelector");
let fileInput = document.getElementById('fileInput');
// Adds option to 'onlineUsersSelector.'
function onlineUsersSelectorAdd(value) {
    if (document.querySelector("option[value='" + value + "']")) return;
    let newOption = document.createElement("option");

    newOption.value = value;
    newOption.innerHTML = value;
    onlineUsersSelector.appendChild(newOption);
}

// Removes an option from 'onlineUsersSelector.'
function onlineUsersSelectorRemove(value) {
    let oldOption = document.querySelector("option[value='" + value + "']");
    if (oldOption !== null) oldOption.remove();
}

// 
onlineUsersSelector.onchange = function() {
    chatMessageInput.value = "/pm " + onlineUsersSelector.value + " ";
    onlineUsersSelector.value = null;
    chatMessageInput.focus();
};

// Focus 'ChatMessageInput' when user opens the page.
chatMessageInput.focus();


// Submit info if enter key is pressed.
chatMessageInput.onkeyup = function(e) {
    if (e.keyCode === 13) {
        chatMessageSend.click();
    }
};
console.log("Event listener attached to chatMessageSend")
// Clears the input and forwards the message.
chatMessageSend.onclick = function () {
    if (chatMessageInput.value.length === 0 && !fileInput.files.length) {
        console.log("No file or message to send");
        return;
    }

    if (fileInput.files.length) {
        const file = fileInput.files[0];

        const reader = new FileReader();
reader.readAsDataURL(file);
        reader.onload = (event) => {
            const fileContent = event.target.result;

            // Send a message with the file content and type to the server
            chatSocket.send(JSON.stringify({
                'message': {
                    'file': {
                        'content': fileContent,
                        'type': file.type,
                    },
                },
            }));
            console.log("File sent successfully");
        };

        
    } else {
        // Handle sending text messages
        chatSocket.send(JSON.stringify({
            "message": chatMessageInput.value,
        }));
    }

    // Clear input fields
    chatMessageInput.value = "";
    fileInput.value = "";
};

// WebSockets.

ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";

let chatSocket = null;
function appendFile(uploader, file) {
    const fileMessage = document.createElement('div');
    fileMessage.className = 'file-message';

    const uploaderElement = document.createElement('span');
    uploaderElement.className = 'file-uploader';
    uploaderElement.textContent = `${uploader}: `;

    const linkElement = document.createElementNS('image');
    linkElement.src = `/media/private_chat_images/${file.filename}`;  // Update the path based on your media settings
    linkElement.alt = `File: ${file.filename}`;
    linkElement.target = '_blank';

    const timestampElement = document.createElement('span');
    timestampElement.className = 'file-timestamp';
    timestampElement.textContent = ` [${file.timestamp}]`;

    fileMessage.appendChild(uploaderElement);
    fileMessage.appendChild(linkElement);
    fileMessage.appendChild(timestampElement);

    chatLog.appendChild(fileMessage);
}

// Modify the switch case for 'file' type in chatSocket.onmessage


function connect() {
    chatSocket = new WebSocket(ws_scheme + "://" + window.location.host + "/ws/messenger/direct_chat/" + private_room_id + "/");
    
    chatSocket.onopen = function(e) {
        console.log("Successfully connected to the WebSocket.");
    }

    chatSocket.onclose = function(e) {
        console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s...");
        setTimeout(function() {
            console.log("Reconnecting...");
            connect();
        }, 2000);
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log(data);

        switch (data.type) {
            case "chat_message":
                chatLog.value += data.user + ": " + data.message + "\n";
                break;
            case "user_list":
                for (let i = 0; i < data.users.length; i++) {
                    onlineUsersSelectorAdd(data.users[i]);
                }
                break;
            case "user_join":
                chatLog.value += data.user + " joined the chat!\n";
                onlineUsersSelectorAdd(data.user);
                break;
            case "user_leave":
                chatLog.value += data.user + " has left the chat.\n"
                onlineUsersSelectorRemove(data.user);
                break;
            case "private_message":
                chatLog.value += "PM from " + data.user + ": " + data.message + "\n";
                break;
            case "private_message_delivered":
                chatLog.value += "PM to " + data.target + ": " + data.message + "\n";
                break;
            case 'file':
                const file = data.file;
                const uploader = data.user;
                // Append the file information to the chat log
                appendFile(uploader, file);
                break;
            default:
                console.error("Unknown message type!");
                break;
        }
        // Scroll to the bottom of the chatlog.
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    chatSocket.onerror = function(err) {
        console.log("WebSocket encountered an error:" + err.message);
        console.log("Closing the Socket.");
        chatSocket.close();
    }
}
connect();