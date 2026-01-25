
export type ReadingStatus = 'WISH' | 'READING' | 'COMPLETED';

export interface User {
  id: string;
  name: string;
  email: string;
  profileImage?: string;
  trustScore: number;
  openChatUrl?: string;
  bio?: string;
}

export interface Book {
  id: string;
  title: string;
  author: string;
  coverImage: string;
  uploaderId: string;
  status: ReadingStatus;
  updatedAt: string;
}

export interface MatchRequest {
  id: string;
  senderId: string;
  receiverId: string;
  bookId: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
  createdAt: string;
}

export interface CommunityPost {
  id: string;
  authorId: string;
  authorName: string;
  content: string;
  likes: number;
  comments: number;
  createdAt: string;
}
