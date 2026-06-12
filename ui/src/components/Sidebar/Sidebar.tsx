import React from 'react';
import NewChatButton from '../NewChatButton/NewChatButton';
import './Sidebar.css';
import type { ChatSession } from '../../types';

interface SidebarProps {
  isCollapsed: boolean;
  chatSessions: ChatSession[];
  activeChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void;
  onToggleSidebar: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  chatSessions,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  onToggleSidebar,
}) => {
  const formatChatTitle = (session: ChatSession) => {
    if (session.title) return session.title;
    return session.messages.length > 0
      ? session.messages[0].text.slice(0, 30) + '...'
      : 'New Chat';
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  const handleDeleteChat = (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation();
    onDeleteChat(chatId);
  };

  return (
    <>
      <aside  >
        {!isCollapsed && (
          <>
            <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
              <div className="sidebar-content">
                <div className="sidebar-header">
                  <div className="logo-section">
                    <div className="logo-large">
                      <img src="/assets/cat-logo.png" alt="Cute cat face logo" />
                      <span className="logo-text">CVKing</span>
                      <span className="logo-subtext">billo Assistant</span>
                    </div>
                  </div>
                </div>

                <div className="sidebar-actions">
                  <NewChatButton onClick={onNewChat} />
                </div>

                <div className="chat-history">
                  <h3 className="history-title">Recent Chats</h3>
                  <div className="chat-list">
                    {chatSessions.map((session) => (
                      <div
                        key={session.id}
                        className={`chat-item-wrapper ${activeChatId === session.id ? 'active' : ''}`}
                      >
                        <button
                          className="chat-item"
                          onClick={() => onSelectChat(session.id)}
                        >
                          <div className="chat-item-content">
                            <div className="chat-title">
                              {formatChatTitle(session)}
                            </div>
                            <div className="chat-date">
                              {formatDate(session.createdAt)}
                            </div>
                          </div>
                        </button>
                        <button
                          className="delete-chat-btn"
                          onClick={(e) => handleDeleteChat(e, session.id)}
                          title="Delete chat"
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
                <button
          className="sidebar-toggle-edge"
          onClick={onToggleSidebar}
        >
          <span className={`toggle-icon ${isCollapsed ? 'collapsed' : ''}`}>
            {isCollapsed ? '→ ' : '←'}

          </span>
        </button>
              </div>
            </div>
          </>
        )}

        {isCollapsed && (
          <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`} onClick={onToggleSidebar}>
            <div className="sidebar-content">
              <div className="collapsed-content" onClick={onToggleSidebar}>
                <div className="logo-small">
                  <img src="/assets/cat-logo.png" alt="Cute cat face logo" />
                </div>
              </div>
              <button
          className="sidebar-toggle-edge"
          onClick={onToggleSidebar}
        >
          <span className={`toggle-icon ${isCollapsed ? 'collapsed' : ''}`}>
            {isCollapsed ? '→ ' : '←'}

          </span>
        </button>
            </div>
          </div>
        )}

        <button
          className="sidebar-toggle-edge"
          onClick={onToggleSidebar}
        >
          <span className={`toggle-icon ${isCollapsed ? 'collapsed' : ''}`}>
            {isCollapsed ? '→ ' : '←'}

          </span>
        </button>
      </aside>
    </>
  );
};

export default Sidebar;
