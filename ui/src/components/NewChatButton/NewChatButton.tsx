import React from 'react';
import './NewChatButton.css';

interface NewChatButtonProps {
  onClick: () => void;
}

const NewChatButton: React.FC<NewChatButtonProps> = ({ onClick }) => {
  return (
    <button className="new-chat-btn" onClick={onClick}>
      <span className="plus-icon">+</span>
      New Chat
    </button>
  );
};

export default NewChatButton;
