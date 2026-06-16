export interface Source {
  source: string;
  page: string | number;
  score: number;
  distance?: number;
  preview?: string;
}

export interface Message {
  role: 'user' | 'assistant';
  text: string;
  timestamp: Date;
  sources?: Source[];
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
