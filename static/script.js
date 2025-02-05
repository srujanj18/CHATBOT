$(document).ready(function () {
    function sendMessage(userInput) {
        if (userInput.trim() === "") return; // Prevent sending empty messages

        $("#chatbox").append(
            '<div class="message user-message"><div class="icon user-icon"><img src="static/user-icon.jpg" alt="User Icon" class="icon"></div><div class="message-content">' +
            userInput +
            "</div></div>"
        );
        $("#userInput").val("");

        // Send the user input to the server
        $.ajax({
            type: "POST",
            url: "/ask",
            contentType: "application/json",
            data: JSON.stringify({ message: userInput }),
            success: function(data) {
                $("#chatbox").append(
                    '<div class="message bot-message"><div class="icon bot-icon"><img src="static/bot-icon.jpg" alt="Bot Icon" class="icon"></div><div class="message-content">' +
                    data.response +
                    "</div></div>"
                );
                $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);
            },
            error: function(error) {
                console.error("Error:", error);
                $("#chatbox").append(
                    '<div class="message bot-message"><div class="message-content">Error: Unable to get response.</div></div>'
                );
            }
        });
    }

    // Send message on button click
    $("#sendButton").click(function() {
        var userInput = $("#userInput").val();
        sendMessage(userInput);
    });

    // Send message on Enter key press
    $("#userInput").keypress(function (e) {
        if (e.which === 13) { // Enter key
            var userInput = $("#userInput").val();
            sendMessage(userInput);
            e.preventDefault(); // Prevent form submission if inside a form
        }
    });

    // Voice recognition
    $("#startVoiceInput").click(function () {
        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.start();

        recognition.onstart = function() {
            $("#voiceStatus").show(); // Show listening status
        };

        recognition.onresult = function(event) {
            var transcript = event.results[0][0].transcript;
            $("#userInput").val(transcript);
            sendMessage(transcript); // Send the recognized voice input
            $("#voiceStatus").hide(); // Hide listening status
        };

        recognition.onerror = function(event) {
            console.error("Speech recognition error:", event.error);
            $("#voiceStatus").hide(); // Hide listening status
        };

        recognition.onend = function() {
            $("#voiceStatus").hide(); // Hide listening status when done
        };
    });

    // Speech synthesis
    function speak(text) {
        var utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
    }
});