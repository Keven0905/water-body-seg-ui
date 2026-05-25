<template>
  <div class="w-full max-w-5xl mx-auto mt-8 space-y-8">
    
    <div class="flex items-center justify-between pb-6 border-b border-white/10">
      <h2 class="text-2xl font-bold text-gray-100 flex items-center tracking-wide">
        <SettingsIcon class="w-6 h-6 mr-3 text-primary animate-spin-slow" />
        模型管理中心
      </h2>
      <button 
        @click="$emit('back')" 
        class="flex items-center px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 rounded-lg transition-all focus:outline-none"
      >
        <ArrowLeftIcon class="w-4 h-4 mr-2" />
        返回可视化前台
      </button>
    </div>

    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-300 flex items-center">
        <ActivityIcon class="w-5 h-5 mr-2 text-blue-400" />
        当前部署模型 (U-Net) 精度指标
      </h3>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div v-for="(metric, index) in metrics" :key="index" 
             class="p-5 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-sm hover:bg-white/10 hover:border-white/20 transition-colors flex flex-col items-center justify-center text-center space-y-2">
          <component :is="metric.icon" class="w-6 h-6" :class="metric.color" />
          <span class="text-sm text-gray-400">{{ metric.label }}</span>
          <span class="text-2xl font-bold text-gray-100">{{ metric.value }}<span class="text-sm font-normal text-gray-500 ml-1">%</span></span>
        </div>
      </div>
    </div>

    <div class="space-y-4 mt-12">
      <h3 class="text-lg font-medium text-gray-300 flex items-center">
        <DatabaseIcon class="w-5 h-5 mr-2 text-teal-400" />
        预训练权重管理
      </h3>
      <div class="p-8 rounded-2xl border border-dashed border-white/20 bg-dark-panel flex flex-col items-center justify-center text-center">
        <div class="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
          <FileTextIcon class="w-8 h-8 text-gray-400" />
        </div>
        <h4 class="text-gray-200 font-medium mb-2">更新 .pth 或 .onnx 权重文件</h4>
        <p class="text-sm text-gray-500 mb-6 max-w-md">上传新的神经网络权重文件后，系统将自动重载推理引擎。</p>
        
        <input 
          type="file" 
          ref="fileInput" 
          class="hidden" 
          accept=".pth, .onnx, .pt, .h5" 
          @change="handleModelSelect" 
        />
        
        <button 
          @click="triggerFileInput"
          class="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary/20 flex items-center focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-bg focus:ring-primary"
        >
          <UploadIcon class="w-5 h-5 mr-2" />
          选择模型文件
        </button>

        <p v-if="updateSuccess" class="mt-4 text-sm text-green-400 flex items-center animate-pulse">
          <CheckCircleIcon class="w-4 h-4 mr-1" /> 模型权重更新成功，推理引擎已重载
        </p>
        <p v-if="updateError" class="mt-4 text-sm text-red-400 flex items-center border border-red-500/20 px-4 py-2 rounded-md bg-red-500/5">
          <CheckCircleIcon class="w-4 h-4 mr-1.5 text-red-400" /> {{ updateError }}
        </p>
      </div>
    </div>

    <div class="mt-12">
      <HistoryPanel />
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import {
  SettingsIcon, ArrowLeftIcon, ActivityIcon, DatabaseIcon,
  UploadIcon, FileTextIcon, TargetIcon, LayersIcon,
  PieChartIcon, CrosshairIcon, CheckSquareIcon, CheckCircleIcon
} from 'lucide-vue-next';
import HistoryPanel from './HistoryPanel.vue';

defineEmits<{ (e: 'back'): void }>();

interface MetricItem {
  label: string;
  value: string;
  icon: any;
  color: string;
}

const metrics = ref<MetricItem[]>([
  { label: 'Accuracy', value: '--', icon: TargetIcon, color: 'text-emerald-400' },
  { label: 'F1-Score', value: '--', icon: CheckSquareIcon, color: 'text-blue-400' },
  { label: 'mIoU', value: '--', icon: LayersIcon, color: 'text-indigo-400' },
  { label: 'mPA', value: '--', icon: PieChartIcon, color: 'text-purple-400' },
  { label: 'mPrecision', value: '--', icon: CrosshairIcon, color: 'text-rose-400' },
]);

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/metrics');
    metrics.value = [
      { label: 'Accuracy', value: data.accuracy?.toFixed(2) ?? '--', icon: TargetIcon, color: 'text-emerald-400' },
      { label: 'F1-Score', value: data.f1_score?.toFixed(2) ?? '--', icon: CheckSquareIcon, color: 'text-blue-400' },
      { label: 'mIoU', value: data.miou?.toFixed(2) ?? '--', icon: LayersIcon, color: 'text-indigo-400' },
      { label: 'mPA', value: data.mpa?.toFixed(2) ?? '--', icon: PieChartIcon, color: 'text-purple-400' },
      { label: 'mPrecision', value: data.mprecision?.toFixed(2) ?? '--', icon: CrosshairIcon, color: 'text-rose-400' },
    ];
  } catch {
    // keep defaults if backend unavailable
  }
});

const fileInput = ref<HTMLInputElement | null>(null);
const updateSuccess = ref(false);
const updateError = ref<string | null>(null);

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleModelSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    updateSuccess.value = false;
    updateError.value = null;
    try {
      const formData = new FormData();
      formData.append('file', target.files[0]);
      await axios.post('/api/model/upload', formData);
      updateSuccess.value = true;
    } catch (err: any) {
      updateError.value = err.response?.data?.error || err.message || '模型上传失败';
    } finally {
      target.value = '';
    }
  }
};
</script>

<style scoped>
.animate-spin-slow {
  animation: spin 6s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>