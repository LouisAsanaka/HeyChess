function createListEntry(className, text) {
    const entry = document.createElement("li");
    const entryLink = document.createElement("a");
    entryLink.appendChild(document.createTextNode(text));
    entry.appendChild(entryLink);
    entry.setAttribute("class", className);
    return entry;
}

function appendToList(listElement, listEntryElement) {
    if (typeof listElement === "string") {
        listElement = document.getElementById(listElement);
    }
    listElement.appendChild(listEntryElement);
}

function fillList(elementId, list, clickCallback, data, highlightCondition) {
    // Retrieve the list element and clear it
    const listElement = document.getElementById(elementId);

    const listItems = $("#" + elementId + " .list-item");
    listItems.each(function() {
        $(this).remove();
    });

    const arrayLength = list.length;
    for (let i = 0; i < arrayLength; ++i) {
        // Create the entry element
        let text = list[i];
        let className = "list-item";
        if (typeof highlightCondition !== 'undefined' && highlightCondition(text)) {
            className += " highlight";
        }
        const entry = createListEntry(className, text);
        if (typeof clickCallback !== "undefined") {
            entry.addEventListener("click", clickCallback);
        }
        if (typeof data !== "undefined") {
            for (let property in data) {
                let attribute = data[property];
                if (attribute == '{text_content}') {
                    attribute = text;
                }
                entry.setAttribute("data-" + property, attribute);
            }
        }
        appendToList(listElement, entry);
    }
}

$(document).ready(function() {
    socket.on('player_list', function(data) {
        const callback = function() {
            // You can't challenge yourself!
            const opponent = this.getAttribute("data-opponent");
            if (username == opponent) {
                window.createNotification({
                    positionClass: 'nfc-bottom-right',
                    showDuration: 5000,
                    theme: 'error'
                })({
                    message: "You can't challenge yourself!"
                });
                return;
            }
            // Send the challenge...
            socket.emit("challenge", {
                opponent: opponent
            });
        };
        let highlightCondition = function(name) {
            return name == username;
        };
        fillList("player-list", JSON.parse(data.playerList), callback, 
            { opponent: "{text_content}" }, highlightCondition);
    });

    socket.on('receive_challenge', function(data) {
        if (typeof data.challenge_id == 'undefined' || typeof data.challenger === 'undefined') {
            return;
        }
        const callback = function() {
            const challengeId = this.getAttribute("data-challenge-id");
            
            // Send the challenge...
            socket.emit("accept_challenge", {
                challenge_id: challengeId
            });

            // Clear challenges
            const listItems = $("#challenges .list-item");
            listItems.each(function() {
                $(this).remove();
            });
        };
        let entry = createListEntry("list-item", data.challenger);
        entry.addEventListener("click", callback);
        entry.setAttribute('data-challenger', data.challenger);
        entry.setAttribute('data-challenge-id', data.challenge_id);
        appendToList("challenges", entry);
    });

    socket.on('request_status', function(data) {
        if (typeof data.type !== "string" || typeof data.message !== "string") {
            return;
        }
        window.createNotification({
            positionClass: 'nfc-bottom-right',
            showDuration: 5000,
            theme: data.type
        })({
            message: data.message
        });
    });
});