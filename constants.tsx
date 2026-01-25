
import { Book, CommunityPost, User } from './types';

export const MOCK_USER: User = {
  id: 'user-1',
  name: '김버디',
  email: 'buddy@example.com',
  trustScore: 98,
  bio: '고전 문학을 사랑하는 독서가입니다.',
  openChatUrl: 'https://open.kakao.com/o/bookbuddy1',
  profileImage: 'https://picsum.photos/seed/user1/200/200',
};

export const MOCK_BOOKS: Book[] = [
  {
    id: 'book-1',
    title: '데미안',
    author: '헤르만 헤세',
    coverImage: 'https://picsum.photos/seed/demian/200/300',
    uploaderId: 'user-1',
    status: 'READING',
    updatedAt: '2024-03-20',
  },
  {
    id: 'book-2',
    title: '사피엔스',
    author: '유발 하라리',
    coverImage: 'https://picsum.photos/seed/sapiens/200/300',
    uploaderId: 'user-2',
    status: 'COMPLETED',
    updatedAt: '2024-03-18',
  },
];

export const MOCK_POSTS: CommunityPost[] = [
  {
    id: 'post-1',
    authorId: 'user-2',
    authorName: '이독서',
    content: '오늘 사피엔스를 다 읽었습니다. 인류의 역사에 대해 깊이 고민하게 되는 시간이었네요. 같이 토론하실 분?',
    likes: 12,
    comments: 4,
    createdAt: '2시간 전',
  },
  {
    id: 'post-2',
    authorId: 'user-1',
    authorName: '김버디',
    content: '헤르만 헤세의 문장은 항상 가슴을 울리네요. 데미안 다시 읽기 시작했어요.',
    likes: 8,
    comments: 2,
    createdAt: '5시간 전',
  }
];
