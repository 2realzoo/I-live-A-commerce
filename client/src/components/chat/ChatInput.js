// src/components/ChatInput.js
import React from 'react';

function ChatInput({ currentMessage, setCurrentMessage }) {
  const handleChange = (e) => {
    setCurrentMessage(e.target.value);
  };

  return (
    <input
      type="text"
      value={currentMessage}
      onChange={handleChange}
      placeholder="채팅을 입력하세요..."
      style={{ margin: '10px' }}
    />
  );
}

export default ChatInput;
