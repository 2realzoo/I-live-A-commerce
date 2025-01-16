// src/components/SendChatButton.js
import React from 'react';

function SendChatButton({ onSend }) {
  return (
    <button onClick={onSend} style={{ margin: '10px' }}>
      전송
    </button>
  );
}

export default SendChatButton;
