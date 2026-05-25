import { ref } from 'vue';
import axios from 'axios';

export function useImageMatcher() {
  const originalImageUrl = ref<string | null>(null);
  const resultImageUrl = ref<string | null>(null);
  const compositeDownloadUrl = ref<string | null>(null);
  const isProcessing = ref(false);
  const errorMsg = ref<string | null>(null);
  const waterStats = ref<{ waterRatio: number; waterPixels: number; totalPixels: number } | null>(null);

  const handleImageSelection = async (file: File) => {
    errorMsg.value = null;
    isProcessing.value = true;

    originalImageUrl.value = URL.createObjectURL(file);
    resultImageUrl.value = null;
    compositeDownloadUrl.value = null;
    waterStats.value = null;

    const match = file.name.match(/(.+)\.jpe?g$/i);
    if (!match) {
      errorMsg.value = `格式被拒绝：只能选择 .jpg 或 .jpeg 格式的原图。当前文件: ${file.name}`;
      isProcessing.value = false;
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);

      const { data } = await axios.post('/api/segment', formData);

      if (!data.success) {
        throw new Error(data.error || '分割请求失败');
      }

      resultImageUrl.value = `/results/${data.filename}`;
      if (data.composite_filename) {
        compositeDownloadUrl.value = `/results/${data.composite_filename}`;
      }
      if (data.water_ratio !== undefined) {
        waterStats.value = {
          waterRatio: data.water_ratio,
          waterPixels: data.water_pixels,
          totalPixels: data.total_pixels,
        };
      }
    } catch (err: any) {
      const msg = err.response?.data?.error || err.message || '文件匹配过程中发生未知错误。';
      errorMsg.value = msg;
    } finally {
      isProcessing.value = false;
    }
  };

  const reset = () => {
    if (originalImageUrl.value) URL.revokeObjectURL(originalImageUrl.value);
    originalImageUrl.value = null;
    resultImageUrl.value = null;
    compositeDownloadUrl.value = null;
    errorMsg.value = null;
    isProcessing.value = false;
    waterStats.value = null;
  };

  return { originalImageUrl, resultImageUrl, compositeDownloadUrl, isProcessing, errorMsg, waterStats, handleImageSelection, reset };
}