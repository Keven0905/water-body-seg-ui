import { ref, computed } from 'vue';
import axios from 'axios';

interface UserInfo {
  username: string;
  role: 'admin' | 'user';
}

const user = ref<UserInfo | null>(null);
const loading = ref(true);

export function useAuth() {
  const isLoggedIn = computed(() => user.value !== null);
  const isAdmin = computed(() => user.value?.role === 'admin');

  async function fetchMe() {
    loading.value = true;
    try {
      const { data } = await axios.get<UserInfo>('/api/me');
      user.value = data;
    } catch {
      user.value = null;
    } finally {
      loading.value = false;
    }
  }

  async function login(username: string, password: string) {
    const { data } = await axios.post('/api/login', { username, password });
    if (data.success) {
      user.value = data.user;
    }
    return data;
  }

  async function register(username: string, password: string) {
    const { data } = await axios.post('/api/register', { username, password });
    if (data.success) {
      user.value = data.user;
    }
    return data;
  }

  async function logout() {
    await axios.post('/api/logout');
    user.value = null;
  }

  return { user, loading, isLoggedIn, isAdmin, fetchMe, login, register, logout };
}
