export interface Message {
  role: 'user' | 'assistant';
  text: string;
  timestamp: Date;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

export interface User {
  firstName: string;
  lastName: string;
  email: string;
  avatar?: string;
}
