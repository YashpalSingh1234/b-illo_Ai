import React, { useState, useRef, useEffect } from 'react';
import type { Message, User } from '../../types';
import './ChatWindow.css';
import Markdown from 'react-markdown'

interface ChatWindowProps {
  user: User | null;
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  sidebarCollapsed: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ 
  user,
  messages, 
  onSendMessage, 
  isLoading = false,
  sidebarCollapsed
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`chat-window ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            
            <h2> Hi {user?.firstName}</h2>
            <h2>  Welcome to billo</h2>
            <p>Start a conversation by typing your question below</p>
            <div className="example-prompts">
              <button 
                className="example-prompt"
                onClick={() => setInput("What can you help me with?")}
              >
                What is Machine Learning?
              </button>
              <button 
                className="example-prompt"
                onClick={() => setInput("Explain machine learning")}
              >
                Do you know about CVKing Learning?
              </button>
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message, index) => (
              <div key={index} className={`message-wrapper ${message.role}`}>
                <div className="message-content">
                  <div className="message-avatar">
                    {message.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-bubble">
                    <div className="message-text">
                    < Markdown>{message.text}</Markdown> 
                    </div>
                    <div className="message-time">
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message-wrapper assistant">
                <div className="message-content">
                  <div className="message-avatar">🤖</div>
                  <div className="message-bubble loading">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="input-container">
        <div className="input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="chat-input"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="send-button"
          >
            {isLoading ? (
              <div className="loading-spinner"></div>
            ) : (
              <span className="send-icon">➤</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;

// import React, { useState, useRef, useEffect } from 'react';
// import type { Message, User } from '../../types';
// import './ChatWindow.css';
// interface ChatWindowProps {
//   user: User | null;
//   messages: Message[];
//   onSendMessage: (message: string) => void;
//   isLoading?: boolean;
//   sidebarCollapsed: boolean;
// }
// const ChatWindow: React.FC<ChatWindowProps> = ({
//   user,
//   messages,
//   onSendMessage,
//   isLoading = false,
//   sidebarCollapsed
// }) => {
//   const [input, setInput] = useState('');
//   const messagesEndRef = useRef<HTMLDivElement>(null);
//   const inputRef = useRef<HTMLInputElement>(null);
//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };
//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);
//   const handleSend = () => {
//     if (!input.trim() || isLoading) return;
//     onSendMessage(input.trim());
//     setInput('');
//   };
//   const handleKeyPress = (e: React.KeyboardEvent) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       handleSend();
//     }
//   };
//   const formatTime = (timestamp: Date) => {
//     return timestamp.toLocaleTimeString([], {
//       hour: '2-digit',
//       minute: '2-digit'
//     });
//   };
//   console.log("message", messages)
//   console.log("input", input)
//   return (
//     <div className={`chat-window ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
//       <div className="messages-container">
//         {messages.length === 0 ? (
//           <div className="empty-state">
//             <div className="empty-icon">:speech_balloon:</div>
//             <h2> Hi {user?.firstName}</h2>
//             <h2>  Welcome to billo</h2>
//             <p>Start a conversation by typing your question below</p>
//             <div className="example-prompts">
//               <button
//                 className="example-prompt"
//                 onClick={() => setInput("What can you help me with?")}
//               >
//                 What is Machine Learning?
//               </button>
//               <button
//                 className="example-prompt"
//                 onClick={() => setInput("Explain machine learning")}
//               >
//                 Do you know about CVKing Learning?
//               </button>
//             </div>
//           </div>
//         ) : (
//           <div className="messages-list">
//             {messages.map((message, index) => (
//               <div key={index} className={`message-wrapper ${message.role}`}>
//                 <div className="message-content">
//                   <div className="message-avatar">
//                     {message.role === 'user' ? ':bust_in_silhouette:' : ':robot_face:'}
//                   </div>
//                   <div className="message-bubble">
//                     <div className="message-text">{message.text}</div>
//                     <div className="message-time">
//                       {formatTime(message.timestamp)}
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             ))}
//             {isLoading && (
//               <div className="message-wrapper assistant">
//                 <div className="message-content">
//                   <div className="message-avatar">:robot_face:</div>
//                   <div className="message-bubble loading">
//                     <div className="typing-indicator">
//                       <span></span>
//                       <span></span>
//                       <span></span>
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             )}
//             <div ref={messagesEndRef} />
//           </div>
//         )}
//       </div>
//       <div className="input-container">
//         <div className="input-wrapper">
//           {/* <input
//             ref={inputRef}
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             onKeyPress={handleKeyPress}
//             placeholder="Type your message..."
//             className="chat-input"
//             disabled={isLoading}
//           /> */}
//           <input
//             ref={inputRef}
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             onKeyDown={handleKeyPress}  // Changed from onKeyPress
//             placeholder="Type your message..."
//             className="chat-input"
//             disabled={isLoading}
//           />
//           <button
//             onClick={handleSend}
//             disabled={!input.trim() || isLoading}
//             className="send-button"
//           >
//             {isLoading ? (
//               <div className="loading-spinner"></div>
//             ) : (
//               <span className="send-icon">➤</span>
//             )}
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };
// export default ChatWindow;
