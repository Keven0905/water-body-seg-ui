<template>
  <div class="w-full flex flex-col items-center space-y-6">
    <div v-if="error" class="w-full max-w-4xl p-4 rounded-lg bg-red-500/10 border border-red-500/50 flex items-center justify-between" role="alert">
      <span class="text-red-400 font-medium">{{ error }}</span>
      <button @click="$emit('retry')" class="px-4 py-2 bg-red-500/20 hover:bg-red-500/40 text-red-300 rounded-md transition-colors">重新上传</button>
    </div>

    <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4 lg:gap-8 h-[75vh] min-h-[650px]">

      <!-- 左：卫星原图 -->
      <div class="relative overflow-hidden rounded-xl border border-white/10 bg-dark-panel">
        <span class="absolute top-4 left-4 z-10 px-3 py-1 bg-black/60 backdrop-blur-md rounded-full text-xs text-gray-300 border border-white/10 shadow-lg pointer-events-none">卫星原图 (JPG)</span>

        <div
          ref="leftContainer"
          class="w-full h-full overflow-hidden cursor-move"
          @wheel="e => handleWheel(e, leftContainer)"
          @mousedown="handleMouseDown"
        >
          <img
            ref="leftImg"
            :src="originalUrl"
            alt="原始卫星影像"
            class="max-w-none origin-top-left block transition-opacity duration-300 pointer-events-none will-change-transform"
            :style="{ transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})` }"
            :class="originalLoaded ? 'opacity-100' : 'opacity-0'"
            @load="originalLoaded = true"
          />
        </div>
      </div>

      <!-- 右：原图 + 水体蒙层叠加 -->
      <div class="relative overflow-hidden rounded-xl border border-white/10 bg-dark-panel">
        <span class="absolute top-4 left-4 z-10 px-3 py-1 bg-black/60 backdrop-blur-md rounded-full text-xs text-primary border border-white/10 shadow-lg pointer-events-none">水体识别结果 (叠加)</span>

        <div v-if="isProcessing" class="absolute inset-0 flex flex-col items-center justify-center bg-dark-panel z-20" aria-busy="true">
          <div class="w-12 h-12 border-4 border-gray-600 border-t-primary rounded-full animate-spin mb-4"></div>
          <span class="text-primary animate-pulse tracking-widest text-sm">正在识别水体区域...</span>
        </div>

        <div v-else-if="error && !resultUrl" class="absolute inset-0 flex flex-col items-center justify-center bg-dark-panel z-20">
          <span class="text-red-400/80 text-sm border border-red-500/20 px-4 py-2 rounded-md bg-red-500/5">识别失败，无法进行比对计算</span>
        </div>

        <div
          v-else-if="resultUrl"
          ref="rightContainer"
          class="w-full h-full overflow-hidden cursor-move relative"
          @wheel="e => handleWheel(e, rightContainer)"
          @mousedown="handleMouseDown"
        >
          <img
            :src="originalUrl"
            alt="卫星原图底衬"
            class="max-w-none origin-top-left block transition-opacity duration-300 pointer-events-none will-change-transform"
            :style="{ transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})` }"
          />

          <img
            :src="resultUrl"
            alt="水体识别叠加层"
            class="absolute top-0 left-0 max-w-none origin-top-left block transition-opacity duration-300 pointer-events-none will-change-transform"
            :style="{ transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})` }"
            :class="resultLoaded ? 'opacity-100' : 'opacity-0'"
            @load="resultLoaded = true"
          />
        </div>
      </div>

    </div>

    <div v-if="waterStats" class="w-full max-w-2xl grid grid-cols-3 gap-4">
      <div class="p-4 rounded-xl border border-white/10 bg-white/5 text-center">
        <span class="block text-xs text-gray-500 mb-1">水体覆盖率</span>
        <span class="text-2xl font-bold text-primary">{{ waterStats.waterRatio }}<span class="text-sm font-normal text-gray-500 ml-0.5">%</span></span>
      </div>
      <div class="p-4 rounded-xl border border-white/10 bg-white/5 text-center">
        <span class="block text-xs text-gray-500 mb-1">水体像素</span>
        <span class="text-2xl font-bold text-gray-100">{{ waterStats.waterPixels.toLocaleString() }}</span>
      </div>
      <div class="p-4 rounded-xl border border-white/10 bg-white/5 text-center">
        <span class="block text-xs text-gray-500 mb-1">图像总像素</span>
        <span class="text-2xl font-bold text-gray-100">{{ waterStats.totalPixels.toLocaleString() }}</span>
      </div>
    </div>

    <div class="flex space-x-4">
      <a
        v-if="compositeDownloadUrl"
        :href="compositeDownloadUrl"
        download
        class="px-6 py-2.5 bg-primary hover:bg-primary-hover text-white rounded-lg transition-all shadow-lg shadow-primary/20 flex items-center focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-bg focus:ring-primary"
      >
        <DownloadIcon class="w-4 h-4 mr-2" />
        导出结果
      </a>
      <button @click="$emit('reset')" class="px-6 py-2.5 bg-white/5 hover:bg-white/10 border border-white/20 text-gray-300 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-gray-500">返回上传</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { DownloadIcon } from 'lucide-vue-next';
import { useSyncedPanZoom } from '../composables/useSyncedPanZoom';

const props = defineProps<{
  originalUrl: string;
  resultUrl: string | null;
  compositeDownloadUrl: string | null;
  waterStats: { waterRatio: number; waterPixels: number; totalPixels: number } | null;
  isProcessing: boolean;
  error: string | null;
}>();

defineEmits<{ (e: 'reset'): void; (e: 'retry'): void }>();

const leftContainer = ref<HTMLElement | null>(null);
const rightContainer = ref<HTMLElement | null>(null);
const leftImg = ref<HTMLImageElement | null>(null);

const originalLoaded = ref(false);
const resultLoaded = ref(false);

const bothLoaded = computed(() => props.resultUrl !== null && originalLoaded.value && resultLoaded.value);

const { transform, initPanZoomSync, handleWheel, handleMouseDown } = useSyncedPanZoom(
  leftContainer,
  leftImg
);

watch(bothLoaded, async (newVal) => {
  if (newVal) {
    await nextTick();
    initPanZoomSync();
  }
});
</script>
