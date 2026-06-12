// import { useState, useEffect } from 'react';
// import Header from './components/Header/Header';
// import Sidebar from './components/Sidebar/Sidebar';
// import ChatWindow from './components/ChatWindow/ChatWindow';
// // import { ChatSession, Message, User } from './types';
// import './App.css';
// import type { ChatSession, Message, User } from './types';

// function App() {
//   const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
//   const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
//   const [activeChatId, setActiveChatId] = useState<string | null>(null);
//   const [isLoading, setIsLoading] = useState(false);
  
//   const [user] = useState<User>({
//     firstName: 'Anubhaw',
//     lastName: 'Dwivedi',
//     email: 'cvking.anubhaw@gmail.com'
//   });

//   const getCurrentMessages = (): Message[] => {
//     const activeChat = chatSessions.find(chat => chat.id === activeChatId);
//     return activeChat ? activeChat.messages : [];
//   };

//   const generateChatId = () => {
//     return Date.now().toString() + Math.random().toString(36).substr(2, 9);
//   };

//   const createNewChat = () => {
//     const newChat: ChatSession = {
//       id: generateChatId(),
//       title: '',
//       messages: [],
//       createdAt: new Date(),
//     };
    
//     setChatSessions(prev => [newChat, ...prev]);
//     setActiveChatId(newChat.id);
//   };

//   const selectChat = (chatId: string) => {
//     setActiveChatId(chatId);
//   };

//   const deleteChat = (chatId: string) => {
//     setChatSessions(prev => {
//       const filtered = prev.filter(chat => chat.id !== chatId);
      
//       if (activeChatId === chatId) {
//         if (filtered.length > 0) {
//           setActiveChatId(filtered[0].id);
//         } else {
//           const newChat: ChatSession = {
//             id: generateChatId(),
//             title: '',
//             messages: [],
//             createdAt: new Date(),
//           };
//           setActiveChatId(newChat.id);
//           return [newChat];
//         }
//       }
      
//       return filtered;
//     });
//   };

//   const sendMessage = async (messageText: string) => {
//     if (!activeChatId) {
//       createNewChat();
//       return;
//     }

//     const userMessage: Message = {
//       role: 'user',
//       text: messageText,
//       timestamp: new Date(),
//     };

//     setChatSessions(prev => 
//       prev.map(chat => 
//         chat.id === activeChatId
//           ? { ...chat, messages: [...chat.messages, userMessage] }
//           : chat
//       )
//     );

//     setIsLoading(true);

//     try {
//       const response = await fetch("http://localhost:5000/query", {
//       // const response = await fetch("http://192.168.1.172:8000/query", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ query: messageText }),
//       });

//       const data = await response.json();

//       const assistantMessage: Message = {
//         role: 'assistant',
//         text: data.answer || "Sorry, I couldn't process your request.",
//         timestamp: new Date(),
//       };

//       setChatSessions(prev => 
//         prev.map(chat => 
//           chat.id === activeChatId
//             ? { 
//                 ...chat, 
//                 messages: [...chat.messages, assistantMessage],
//                 title: chat.title || messageText.slice(0, 30) + '...'
//               }
//             : chat
//         )
//       );

//     } catch (error) {
//       const errorMessage: Message = {
//         role: 'assistant',
//         text: "⚠️ Error connecting to server. Please try again.",
//         timestamp: new Date(),
//       };

//       setChatSessions(prev => 
//         prev.map(chat => 
//           chat.id === activeChatId
//             ? { ...chat, messages: [...chat.messages, errorMessage] }
//             : chat
//         )
//       );
//     } finally {
//       setIsLoading(false);
//     }
//   };


// useEffect(() => {
//   if (chatSessions.length === 0) {
//     setChatSessions(prev => {
//       if (prev.length === 0) {
//         const newChat: ChatSession = {
//           id: generateChatId(),
//           title: '',
//           messages: [],
//           createdAt: new Date(),
//         };
//         setActiveChatId(newChat.id);
//         return [newChat];
//       }
//       return prev;
//     });
//   }
// }, []);

//   return (
//     <div className="app">
//       <Header 
//         user={user}
//         sidebarCollapsed={sidebarCollapsed}
//       />
      
//       <div className="app-body">
//         <Sidebar
//           isCollapsed={sidebarCollapsed}
//           chatSessions={chatSessions}
//           activeChatId={activeChatId}
//           onSelectChat={selectChat}
//           onNewChat={createNewChat}
//           onDeleteChat={deleteChat}
//           onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
//         />
        
//         <ChatWindow
//           messages={getCurrentMessages()}
//           onSendMessage={sendMessage}
//           isLoading={isLoading}
//           sidebarCollapsed={sidebarCollapsed}
//           user={user}
//         />
//       </div>
//     </div>
//   );
// }

// export default App;
import { useState, useEffect } from 'react';
import Header from './components/Header/Header';
import Sidebar from './components/Sidebar/Sidebar';
import ChatWindow from './components/ChatWindow/ChatWindow';
import type { ChatSession, Message, User } from './types';
import './App.css';
function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [user] = useState<User>({
    firstName: 'Anubhaw',
    lastName: 'Dwivedi',
    email: 'cvking.anubhaw@gmail.com'
  });
  const getCurrentMessages = (): Message[] => {
    const activeChat = chatSessions.find(chat => chat.id === activeChatId);
    return activeChat ? activeChat.messages : [];
  };
  const generateChatId = () => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  };
  const createNewChat = () => {
    const newChat: ChatSession = {
      id: generateChatId(),
      title: '',
      messages: [],
      createdAt: new Date(),
    };
    setChatSessions(prev => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };
  const selectChat = (chatId: string) => {
    setActiveChatId(chatId);
  };
  const deleteChat = (chatId: string) => {
    setChatSessions(prev => {
      const filtered = prev.filter(chat => chat.id !== chatId);
      if (activeChatId === chatId) {
        if (filtered.length > 0) {
          setActiveChatId(filtered[0].id);
        } else {
          const newChat: ChatSession = {
            id: generateChatId(),
            title: '',
            messages: [],
            createdAt: new Date(),
          };
          setActiveChatId(newChat.id);
          return [newChat];
        }
      }
      return filtered;
    });
  };
  const sendMessage = async (messageText: string) => {
    console.log("sendMessage called with:", messageText);
    console.log("Current activeChatId:", activeChatId);
    let currentChatId = activeChatId;
    // If no active chat, create one first
    if (!currentChatId) {
      const newChatId = generateChatId();
      const newChat: ChatSession = {
        id: newChatId,
        title: '',
        messages: [],
        createdAt: new Date(),
      };
      setChatSessions(prev => [newChat, ...prev]);
      setActiveChatId(newChatId);
      currentChatId = newChatId;
    }
    const userMessage: Message = {
      role: 'user',
      text: messageText,
      timestamp: new Date(),
    };
    setChatSessions(prev => {
      const updated = prev.map(chat =>
        chat.id === currentChatId
          ? { ...chat, messages: [...chat.messages, userMessage] }
          : chat
      );
      console.log("Updated chatSessions after user message:", updated);
      return updated;
    });
    setIsLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: messageText }),
      });
      const data = await response.json();
      console.log("API response:", data);
      const assistantMessage: Message = {
        role: 'assistant',
        text: data.answer || "Sorry, I couldn't process your request.",
        timestamp: new Date(),
      };
      setChatSessions(prev => {
        const updated = prev.map(chat =>
          chat.id === currentChatId
            ? {
                ...chat,
                messages: [...chat.messages, assistantMessage],
                title: chat.title || messageText.slice(0, 30) + '...'
              }
            : chat
        );
        console.log("Updated chatSessions after assistant message:", updated);
        return updated;
      });
    } catch (error) {
      console.error("API error:", error);
      const errorMessage: Message = {
        role: 'assistant',
        text: ":warning: Error connecting to server. Please try again.",
        timestamp: new Date(),
      };
      setChatSessions(prev =>
        prev.map(chat =>
          chat.id === currentChatId
            ? { ...chat, messages: [...chat.messages, errorMessage] }
            : chat
        )
      );
    } finally {
      setIsLoading(false);
    }
  };
  // Debug effect
  useEffect(() => {
    console.log("Current messages:", getCurrentMessages());
  }, [chatSessions, activeChatId]);
  // useEffect(() => {
  //   if (chatSessions.length === 0) {
  //     createNewChat();
  //   }
  // }, []);
  return (
    <div className="app">
      <Header
        user={user}
        sidebarCollapsed={sidebarCollapsed}
      />
      <div className="app-body">
        <Sidebar
          isCollapsed={sidebarCollapsed}
          chatSessions={chatSessions}
          activeChatId={activeChatId}
          onSelectChat={selectChat}
          onNewChat={createNewChat}
          onDeleteChat={deleteChat}
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
        <ChatWindow
          messages={getCurrentMessages()}
          onSendMessage={sendMessage}
          isLoading={isLoading}
          sidebarCollapsed={sidebarCollapsed}
          user={user}
        />
      </div>
    </div>
  );
}
export default App;
