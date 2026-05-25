<template>
  <div class="min-h-screen text-gray-100 font-sans antialiased selection:bg-primary selection:text-white">

    <header class="w-full px-8 py-6 border-b border-white/5 bg-white/5 backdrop-blur-lg sticky top-0 z-50">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-3 h-8 bg-primary rounded-sm"></div>
          <h1 class="text-2xl font-bold tracking-tight">基于U-Net模型的卫星图像水体识别系统 <span class="font-light text-gray-400">水体识别系统</span></h1>
        </div>

        <div v-if="isLoggedIn" class="flex items-center space-x-3">
          <span class="text-xs text-gray-500">
            {{ user?.username }}
            <span v-if="isAdmin" class="text-primary ml-0.5">(管理员)</span>
          </span>

          <button
            v-if="currentView === 'home' && isAdmin"
            @click="currentView = 'admin'"
            class="flex items-center text-sm font-medium text-gray-400 hover:text-primary transition-colors px-3 py-1.5 rounded-md hover:bg-white/5"
          >
            <SettingsIcon class="w-4 h-4 mr-1.5" />
            后台管理
          </button>

          <button
            v-if="currentView === 'admin'"
            @click="currentView = 'home'"
            class="flex items-center text-sm font-medium text-gray-400 hover:text-primary transition-colors px-3 py-1.5 rounded-md hover:bg-white/5"
          >
            返回前台
          </button>

          <button
            @click="handleLogout"
            class="flex items-center text-sm font-medium text-gray-500 hover:text-red-400 transition-colors px-3 py-1.5 rounded-md hover:bg-white/5"
          >
            退出登录
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8">
      <Transition name="fade" mode="out-in">

        <LoginPage v-if="!isLoggedIn" key="login-view" />

        <div v-else-if="currentView === 'home'" key="home-view">
          <ImageUploader
            v-if="!originalImageUrl && !isProcessing && !errorMsg"
            @select="handleImageSelection"
          />
          <ResultViewer
            v-else
            :original-url="originalImageUrl!"
            :result-url="resultImageUrl"
            :composite-download-url="compositeDownloadUrl"
            :water-stats="waterStats"
            :is-processing="isProcessing"
            :error="errorMsg"
            @reset="reset"
            @retry="reset"
          />
        </div>

        <AdminDashboard
          v-else-if="currentView === 'admin' && isAdmin"
          key="admin-view"
          @back="currentView = 'home'"
        />

      </Transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { SettingsIcon } from 'lucide-vue-next';
import ImageUploader from './components/ImageUploader.vue';
import ResultViewer from './components/ResultViewer.vue';
import AdminDashboard from './components/AdminDashboard.vue';
import LoginPage from './components/LoginPage.vue';
import { useImageMatcher } from './composables/useImageMatcher';
import { useAuth } from './composables/useAuth';

const { user, isLoggedIn, isAdmin, logout } = useAuth();

const currentView = ref<'home' | 'admin'>('home');

const { originalImageUrl, resultImageUrl, compositeDownloadUrl, isProcessing, errorMsg, waterStats, handleImageSelection, reset } = useImageMatcher();

async function handleLogout() {
  await logout();
  currentView.value = 'home';
  reset();
}
</script>
