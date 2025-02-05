# Virtual Assistant Chatbot

## Overview

This project is a virtual assistant chatbot built using Flask and a language model. The chatbot can respond to user queries and provide assistance in a conversational manner. It also supports voice input for a more interactive experience.

## Features

- Text-based interaction with the chatbot.
- Voice input functionality using the Web Speech API.
- Integration with a language model for generating responses.
- Responsive web interface.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python.
- **JavaScript**: For handling client-side interactions and voice recognition.
- **HTML/CSS**: For structuring and styling the web interface.
- **LangChain**: For integrating language models.

## Requirements

To run this project, you need the following Python packages:

- Flask
- langchain-groq
- langchain-core
- jinja2
- requests
- (Any other dependencies you may have)

You can install these packages using the `requirements.txt` file provided in the project.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Set up a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set your API key**: Make sure to replace `"your_api_key_here"` in `app.py` with your actual API key for the language model.

## Running the Application

1. **Start the Flask server**:

   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:

   ```
   http://localhost:5000/
   ```

3. **Interact with the chatbot**: Type your message or use the voice input feature.

## Usage

- Type your message in the input box and press the send button or hit Enter.
- Click the "Start Voice Input" button to use voice recognition.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [LangChain](https://langchain.readthedocs.io/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
