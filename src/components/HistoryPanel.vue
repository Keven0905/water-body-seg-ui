<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-medium text-gray-300 flex items-center">
        <ClockIcon class="w-5 h-5 mr-2 text-amber-400" />
        识别历史记录
      </h3>
      <span class="text-xs text-gray-500">共 {{ records.length }} 条</span>
    </div>

    <div v-if="records.length === 0" class="p-8 rounded-2xl border border-dashed border-white/20 bg-dark-panel text-center">
      <p class="text-sm text-gray-500">暂无历史记录，完成一次水体识别后将自动记录</p>
    </div>

    <div v-else class="space-y-2 max-h-[60vh] overflow-y-auto pr-1">
      <div
        v-for="record in records"
        :key="record.id"
        class="flex items-center p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 hover:border-white/15 transition-colors"
      >
        <div class="flex-1 min-w-0">
          <p class="text-sm text-gray-200 font-medium truncate">{{ record.original_name }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ record.timestamp }}</p>
        </div>

        <div class="flex items-center space-x-6 ml-4">
          <div class="text-center">
            <span class="block text-xs text-gray-500">覆盖率</span>
            <span class="text-sm font-bold text-primary">{{ record.water_ratio }}%</span>
          </div>
          <div class="text-center">
            <span class="block text-xs text-gray-500">水体像素</span>
            <span class="text-sm text-gray-300">{{ record.water_pixels.toLocaleString() }}</span>
          </div>

          <div class="flex items-center space-x-2">
            <a
              :href="`/api/history/${record.id}/download`"
              class="p-2 rounded-lg bg-white/5 hover:bg-primary/20 text-gray-400 hover:text-primary transition-colors"
              title="导出 PNG"
            >
              <DownloadIcon class="w-4 h-4" />
            </a>
            <button
              @click="handleDelete(record.id)"
              class="p-2 rounded-lg bg-white/5 hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors"
              title="删除记录"
            >
              <Trash2Icon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ClockIcon, DownloadIcon, Trash2Icon } from 'lucide-vue-next';

interface HistoryRecord {
  id: number;
  original_name: string;
  result_filename: string;
  water_ratio: number;
  water_pixels: number;
  total_pixels: number;
  timestamp: string;
}

const records = ref<HistoryRecord[]>([]);

async function fetchHistory() {
  try {
    const { data } = await axios.get<HistoryRecord[]>('/api/history');
    records.value = data;
  } catch {
    records.value = [];
  }
}

async function handleDelete(id: number) {
  try {
    await axios.delete(`/api/history/${id}`);
    records.value = records.value.filter(r => r.id !== id);
  } catch {
    // silent
  }
}

onMounted(fetchHistory);
</script>
