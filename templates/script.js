
    const chatDiv = document.getElementById("chat");
    const userInput = document.getElementById("user-input");
    const submitButton = document.getElementById("submit");

    submitButton.addEventListener("click", () => {
        const userMessage = userInput.value;
        if (userMessage.trim() === "") {
            return;
        }

        appendMessage("You: " + userMessage);

        fetch("http://127.0.0.1:5000/get_weather", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({content: userMessage}),
        })
            .then((response) => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error("Invalid Res");
                }
            })
            .then((data) => {
                try {
                    appendMessage("ChatBot: " + data.message);
                } catch (error) {
                    console.error("Error parsing JSON response:", error);
                }
                userInput.value = "";
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    });

    function appendMessage(message) {
        const messageDiv = document.createElement("div");
        messageDiv.textContent = message;
        // chatMessage.textContent = `[${chat.role}]: ${chat.content}`;
        chatDiv.appendChild(messageDiv);
    }

