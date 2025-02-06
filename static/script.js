$(document).ready(function () {
    let isMuted = false; // Track mute state
    let currentUtterance = null; // Track the current utterance

    function sendMessage(userInput) {
        if (userInput.trim() === "") return; // Prevent sending empty messages

        $("#chatbox").append(
            '<div class="message user-message"><div class="icon user-icon"><img src="static/user-icon.jpg" alt="User Icon" class="icon"></div><div class="message-content">' +
            userInput +
            "</div></div>"
        );
        $("#userInput").val("");

        // Check if the user is asking for an image
        if (userInput.toLowerCase().includes("generate image")) {
            const prompt = userInput.replace("generate image", "").trim(); // Extract the prompt
            generateImage(prompt); // Call the image generation function
            return; // Exit the function early
        }

        // Send the user input to the server
        $.ajax({
            type: "POST",
            url: "/ask",
            contentType: "application/json",
            data: JSON.stringify({ message: userInput }),
            success: function(data) {
                // Call the typing effect function
                typeMessage(data.response);
            },
            error: function(error) {
                console.error("Error:", error);
                $("#chatbox").append(
                    '<div class="message bot-message"><div class="message-content">Error: Unable to get response.</div></div>'
                );
            }
        });
    }

    // Function for typing effect
    function typeMessage(text) {
        const typingDelay = 0; // Decrease the delay for faster typing (in milliseconds)
        let index = 0;

        // Create a new message element
        const messageElement = $('<div class="message bot-message"><div class="icon bot-icon"><img src="static/bot-icon.jpg" alt="Bot Icon" class="icon"></div><div class="message-content"></div></div>');
        $("#chatbox").append(messageElement);
        $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight); // Scroll to the bottom

        // Function to type each character
        function typeCharacter() {
            if (index < text.length) {
                messageElement.find('.message-content').append(text.charAt(index));
                index++;
                setTimeout(typeCharacter, typingDelay); // Call the function again after the delay
            } else {
                if (!isMuted) {
                    speak(text); // Call the speak function to read out the response
                }
            }
        }

        typeCharacter(); // Start typing
    }

    // Function for speech synthesis
    function speak(text) {
        if (isMuted) return; // Don't speak if muted
        currentUtterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(currentUtterance);
    }

    // Mute and Unmute functionality
    $("#muteButton").click(function() {
        isMuted = true;
        if (currentUtterance) {
            window.speechSynthesis.pause(); // Pause the current utterance
        }
        $(this).hide(); // Hide mute button
        $("#unmuteButton").show(); // Show unmute button
    });

    $("#unmuteButton").click(function() {
        isMuted = false;
        if (currentUtterance) {
            window.speechSynthesis.resume(); // Resume the current utterance
        }
        $(this).hide(); // Hide unmute button
        $("#muteButton").show(); // Show mute button
    });

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

    // Function to generate an image
    function generateImage(prompt) {
        $.ajax({
            type: "POST",
            url: "/generate_image",
            contentType: "application/json",
            data: JSON.stringify({ prompt: prompt }),
            success: function(data) {
                if (data.image_url) {
                    $("#chatbox").append(
                        '<div class="message bot-message"><div class="icon bot-icon"><img src="static/bot-icon.jpg" alt="Bot Icon" class="icon"></div><div class="message-content"><img src="' + data.image_url + '" alt="Generated Image" style="max-width: 100%; height: auto;"></div></div>'
                    );
                    $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight); // Scroll to the bottom
                } else {
                    $("#chatbox").append(
                        '<div class="message bot-message"><div class="message-content">Error generating image.</div></div>'
                    );
                }
            },
            error: function(error) {
                console.error("Error:", error);
                $("#chatbox").append(
                    '<div class="message bot-message"><div class="message-content">Error: Unable to generate image.</div></div>'
                );
            }
        });
    }
});
