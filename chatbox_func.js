document.getElementById("chatInput").addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    event.preventDefault(); // prevent default form behavior

    const message = this.value.trim();
    if (!message) return;   // ignore empty input

    // Append message with ">" to chatHistory
    const msgDiv = document.createElement("div");
    msgDiv.innerText = "> " + message;
    document.getElementById("chatHistory").appendChild(msgDiv);

    this.value = "";        // clear the input
  }
});
