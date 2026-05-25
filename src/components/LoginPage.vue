<template>
  <div class="min-h-[70vh] flex items-center justify-center">
    <div class="w-full max-w-md p-8 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl">
      <h2 class="text-2xl font-bold text-gray-100 text-center mb-8">
        {{ isRegister ? '注册账号' : '用户登录' }}
      </h2>

      <div class="space-y-5">
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">用户名</label>
          <input
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            @keydown.enter="submit"
          />
        </div>

        <div>
          <label class="block text-sm text-gray-400 mb-1.5">密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            @keydown.enter="submit"
          />
        </div>

        <div v-if="error" class="text-sm text-red-400 border border-red-500/20 px-4 py-2.5 rounded-lg bg-red-500/5">
          {{ error }}
        </div>

        <div v-if="successMsg" class="text-sm text-green-400 border border-green-500/20 px-4 py-2.5 rounded-lg bg-green-500/5">
          {{ successMsg }}
        </div>

        <button
          @click="submit"
          :disabled="submitting"
          class="w-full py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary/20 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-bg focus:ring-primary"
        >
          {{ submitting ? '请稍候...' : (isRegister ? '注册' : '登录') }}
        </button>

        <p class="text-center text-sm text-gray-500">
          <span v-if="isRegister">已有账号？</span>
          <span v-else>没有账号？</span>
          <button
            @click="isRegister = !isRegister; error = ''; successMsg = ''"
            class="text-primary hover:text-primary-hover transition-colors ml-1"
          >
            {{ isRegister ? '去登录' : '去注册' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuth } from '../composables/useAuth';

const { login, register } = useAuth();

const username = ref('');
const password = ref('');
const isRegister = ref(false);
const error = ref('');
const successMsg = ref('');
const submitting = ref(false);

async function submit() {
  error.value = '';
  successMsg.value = '';
  submitting.value = true;

  try {
    if (isRegister.value) {
      const res = await register(username.value, password.value);
      if (res.success) {
        successMsg.value = '注册成功，已自动登录';
      } else {
        error.value = res.error || '注册失败';
      }
    } else {
      const res = await login(username.value, password.value);
      if (!res.success) {
        error.value = res.error || '登录失败';
      }
    }
  } catch (err: any) {
    error.value = err.response?.data?.error || '网络错误，请重试';
  } finally {
    submitting.value = false;
  }
}
</script>
