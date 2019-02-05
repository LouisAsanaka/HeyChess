socket.on('player_list', function(data) {
    // Retrieve the player list element and clear it
    let playerListElement = document.getElementById("player-list");
    playerListElement.innerHTML = "";

    // Initialize the title of the list
    let titleElement = document.createElement("li");
    let titleLink = document.createElement("a");
    titleLink.appendChild(document.createTextNode("Online Players"));
    titleElement.appendChild(titleLink);
    titleElement.setAttribute("class", "player-list-title");
    playerListElement.appendChild(titleElement);

    // Parse the incoming data as an array of names
    let list = JSON.parse(data.playerList);

    const arrayLength = list.length;
    for (var i = 0; i < arrayLength; ++i) {
        // Create the player entry element
        let playerEntry = document.createElement("li");
        let entryLink = document.createElement("a");
        entryLink.appendChild(document.createTextNode(list[i]));
        playerEntry.appendChild(entryLink);
        playerEntry.setAttribute("class", "player-item");
        playerListElement.appendChild(playerEntry);
    }
});