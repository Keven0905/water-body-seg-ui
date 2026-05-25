<template>
  <div class="relative w-full flex flex-col items-center justify-center min-h-[75vh]">
    
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-primary/10 rounded-full blur-[120px] pointer-events-none -z-10"></div>
    <div class="absolute top-1/2 left-1/4 w-[400px] h-[400px] bg-blue-500/10 rounded-full blur-[100px] pointer-events-none -z-10"></div>

    <div 
      class="relative w-full max-w-2xl p-16 border border-white/10 rounded-3xl bg-white/5 backdrop-blur-xl transition-all duration-300 flex flex-col items-center justify-center cursor-pointer group focus:outline-none focus:ring-2 focus:ring-primary shadow-2xl shadow-black/40 overflow-hidden"
      :class="isDragging ? 'border-primary/80 bg-white/10 scale-[1.02]' : 'hover:bg-white/10 hover:border-primary/50 hover:shadow-primary/20'"
      @click="triggerInput"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      role="button"
      tabindex="0"
      aria-label="选择卫星影像原图 (JPG格式)"
      @keydown.enter="triggerInput"
    >
      <div class="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>

      <input 
        type="file" 
        ref="fileInput" 
        class="hidden" 
        accept=".jpg, .jpeg" 
        @change="handleFileChange" 
      />
      
      <div class="relative p-4 rounded-full bg-white/5 mb-6 group-hover:bg-primary/20 transition-colors duration-300">
        <UploadCloudIcon class="w-12 h-12 text-gray-400 group-hover:text-primary transition-colors" />
      </div>
      
      <h3 class="text-2xl font-semibold text-gray-100 mb-3 tracking-wide">
        {{ isDragging ? '松开鼠标立即匹配' : '点击或拖拽选取卫星原图' }}
      </h3>
      
      <div class="flex items-center space-x-2 text-sm text-gray-400">
        <span class="px-2 py-1 bg-black/30 rounded text-gray-300 border border-white/5">JPG</span>
        <span>系统将自动匹配对应的 PNG 结果图</span>
      </div>
    </div>

    <div class="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-3xl w-full px-4">
      <div class="flex flex-col items-center text-center space-y-3 opacity-60 hover:opacity-100 transition-opacity cursor-default">
        <ZapIcon class="w-6 h-6 text-primary" />
        <h4 class="text-sm font-medium text-gray-200">毫秒级极速匹配</h4>
        <p class="text-xs text-gray-500">基于本地高速缓存架构，丢弃网络延迟</p>
      </div>
      <div class="flex flex-col items-center text-center space-y-3 opacity-60 hover:opacity-100 transition-opacity cursor-default">
        <LayersIcon class="w-6 h-6 text-blue-400" />
        <h4 class="text-sm font-medium text-gray-200">亚像素级双视窗</h4>
        <p class="text-xs text-gray-500">采用原生高精度仿射变换矩阵实现严格同步</p>
      </div>
      <div class="flex flex-col items-center text-center space-y-3 opacity-60 hover:opacity-100 transition-opacity cursor-default">
        <ShieldCheckIcon class="w-6 h-6 text-teal-400" />
        <h4 class="text-sm font-medium text-gray-200">科研级神经网络</h4>
        <p class="text-xs text-gray-500">内置改良调参后的U-Net神经网络</p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { UploadCloudIcon, ZapIcon, LayersIcon, ShieldCheckIcon } from 'lucide-vue-next';

const emit = defineEmits<{ (e: 'select', file: File): void }>();
const fileInput = ref<HTMLInputElement | null>(null);
const isDragging = ref(false); // 拖拽状态机

const triggerInput = () => fileInput.value?.click();

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    emit('select', target.files[0]);
    target.value = ''; 
  }
};

const handleDrop = (e: DragEvent) => {
  isDragging.value = false; // 重置拖拽状态
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    emit('select', e.dataTransfer.files[0]);
  }
};
</script>