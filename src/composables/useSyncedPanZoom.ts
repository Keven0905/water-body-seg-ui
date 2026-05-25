import { ref, type Ref } from 'vue';

export function useSyncedPanZoom(
  containerRef: Ref<HTMLElement | null>,
  imgRef: Ref<HTMLImageElement | null>
) {
  // 共享的变换矩阵状态
  const transform = ref({ x: 0, y: 0, scale: 1 });
  
  // 核心算法：限制缩放和位移边界，绝对禁止出现留白
  const enforceBounds = (x: number, y: number, scale: number) => {
    if (!containerRef.value || !imgRef.value) return { x, y, scale };
    
    const cw = containerRef.value.clientWidth;
    const ch = containerRef.value.clientHeight;
    const iw = imgRef.value.naturalWidth;
    const ih = imgRef.value.naturalHeight;
    
    // 强制 Cover 模式：保证任何时候图片的较短边都能占满容器
    const minScale = Math.max(cw / iw, ch / ih);
    const finalScale = Math.max(minScale, scale);
    
    // 计算位移极限（触边死锁）
    const minX = cw - iw * finalScale;
    const minY = ch - ih * finalScale;
    
    // x和y的取值永远被限制在 [允许偏移的最大负值, 0] 之间
    const finalX = Math.min(0, Math.max(minX, x));
    const finalY = Math.min(0, Math.max(minY, y));
    
    return { x: finalX, y: finalY, scale: finalScale };
  };

  const initPanZoomSync = () => {
    if (!containerRef.value || !imgRef.value) return;
    const cw = containerRef.value.clientWidth;
    const ch = containerRef.value.clientHeight;
    const iw = imgRef.value.naturalWidth;
    const ih = imgRef.value.naturalHeight;
    
    const minScale = Math.max(cw / iw, ch / ih);
    
    // 初始化居中计算
    const initialX = (cw - iw * minScale) / 2;
    const initialY = (ch - ih * minScale) / 2;
    
    transform.value = enforceBounds(initialX, initialY, minScale);
  };

  // 以鼠标指针为圆心的矩阵缩放推导
  const handleWheel = (e: WheelEvent, currentContainer: HTMLElement | null) => {
    if (!currentContainer) return;
    e.preventDefault();
    const zoomFactor = 1.15; // 缩放灵敏度
    const direction = e.deltaY < 0 ? 1 : -1;
    const newScale = transform.value.scale * (direction > 0 ? zoomFactor : (1 / zoomFactor));
    
    const rect = currentContainer.getBoundingClientRect();
    const cursorX = e.clientX - rect.left;
    const cursorY = e.clientY - rect.top;

    const imgX = (cursorX - transform.value.x) / transform.value.scale;
    const imgY = (cursorY - transform.value.y) / transform.value.scale;

    const newX = cursorX - imgX * newScale;
    const newY = cursorY - imgY * newScale;

    transform.value = enforceBounds(newX, newY, newScale);
  };

  // 纯原生拖拽逻辑
  let isDragging = false;
  let startMouse = { x: 0, y: 0 };
  let startTransform = { x: 0, y: 0 };

  const handleMouseDown = (e: MouseEvent) => {
    e.preventDefault();
    isDragging = true;
    startMouse = { x: e.clientX, y: e.clientY };
    startTransform = { x: transform.value.x, y: transform.value.y };
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;
    const dx = e.clientX - startMouse.x;
    const dy = e.clientY - startMouse.y;
    transform.value = enforceBounds(startTransform.x + dx, startTransform.y + dy, transform.value.scale);
  };

  const handleMouseUp = () => {
    isDragging = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  return { transform, initPanZoomSync, handleWheel, handleMouseDown };
}