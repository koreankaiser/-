
import { createClient } from '@supabase/supabase-js';

// 환경 변수 안전하게 가져오기
const getEnv = (key: string): string => {
  try {
    if (typeof process !== 'undefined' && process.env) {
      return (process.env as any)[key] || '';
    }
  } catch (e) {
    return '';
  }
  return '';
};

const supabaseUrl = getEnv('SUPABASE_URL');
const supabaseAnonKey = getEnv('SUPABASE_ANON_KEY');

// 유효한 URL과 Key가 있을 때만 실제 클라이언트 생성
const isConfigured = supabaseUrl && supabaseAnonKey && supabaseUrl.startsWith('https://');

export const supabase = isConfigured
  ? createClient(supabaseUrl, supabaseAnonKey)
  : ({
      auth: {
        getSession: async () => ({ data: { session: null }, error: null }),
        onAuthStateChange: () => ({
          data: { subscription: { unsubscribe: () => {} } },
        }),
        getUser: async () => ({ data: { user: null }, error: null }),
        signInWithPassword: async () => ({ data: { user: null, session: null }, error: new Error('API 키가 설정되지 않았습니다.') }),
        signUp: async () => ({ data: { user: null, session: null }, error: new Error('API 키가 설정되지 않았습니다.') }),
      },
      from: () => ({
        select: () => ({
          eq: () => Promise.resolve({ data: [], error: null }),
          order: () => Promise.resolve({ data: [], error: null }),
        }),
        insert: () => Promise.resolve({ data: [], error: null }),
        update: () => ({
          eq: () => Promise.resolve({ data: [], error: null }),
        }),
      }),
    } as any);

if (!isConfigured) {
  console.warn('BookBuddy: Supabase 설정이 되어있지 않습니다. 데모 모드로 동작합니다.');
}
