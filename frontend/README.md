# Purdue AI Assistant

## Overview

Purdue AI Assistant is an interactive chatbot designed to assist Purdue University students with their academic needs. This web application provides a user-friendly interface for students to ask questions related to their courses, university policies, campus resources, and more. Powered by artificial intelligence, the assistant aims to provide accurate and helpful information to enhance the learning experience of Purdue students.

## Features

- **Intuitive Chat Interface**: Clean, modern UI for seamless conversation with the AI
- **Dark/Light Mode**: Toggle between dark and light themes based on preference
- **Mobile Responsive**: Fully responsive design that works on desktops, tablets, and mobile devices
- **User Authentication**: Login/signup functionality to save chat history and preferences
- **Chat History**: Access to previous conversations for continued learning
- **Purdue-Branded**: Featuring Purdue University colors and logo for a familiar experience

## Technology Stack

- **Frontend**: React.js
- **Styling**: Tailwind CSS with custom Purdue theme variables
- **UI Components**: Custom built components with Purdue design language
- **Responsiveness**: Mobile-first design approach

## Usage

1. **Start a New Chat**: Click the "New Chat" button to begin a conversation with Purdue AI
2. **Ask Questions**: Type your Purdue-related questions in the text area and press Enter or click the send button
3. **View Responses**: The AI will process your question and provide a helpful response
4. **Toggle Themes**: Use the Light Mode toggle in the sidebar to switch between dark and light themes
5. **Access Previous Chats**: Click on chat sessions in the sidebar to revisit previous conversations

### Purdue Theming

The application uses Purdue's official colors defined in CSS variables:

```css
:root {
  --purdue-gold: #CEB888;
  --purdue-black: #000000;
  --purdue-dark-gold: #9D8E5C;
  --purdue-light-gold: #DCCCA3;
  --purdue-gray: #555960;
  --purdue-light-gray: #f5f5f5;
  --purdue-dark-gray: #333333;
}
```

You can modify these variables in `styles.css` to update the theme throughout the application.
