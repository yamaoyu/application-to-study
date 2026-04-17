import { ref, computed } from "vue";

export const usePage = (todos, itemNum) => {
  // ページネーション用の変数
  const currentPage = ref(1);
  const itemsPerPage = ref(itemNum);
  const totalItems = computed(() => todos.value.length);
  const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value));
  const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value);
  const endIndex = computed(() => Math.min(startIndex.value + itemsPerPage.value, totalItems.value));
    
  const paginatedTodos = computed(() => {
    return todos.value.slice(startIndex.value, endIndex.value);
  });

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page;
    }
  };

  // 表示するページ番号の範囲を計算
  const visiblePages = computed(() => {
    const pages = [];
    const maxVisiblePages = 5;
    let start = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2))
    let end = Math.min(totalPages.value, start + maxVisiblePages - 1)
    
    // 最後のページが表示範囲に入るように調整
    if (end - start + 1 < maxVisiblePages) {
      start = Math.max(1, end - maxVisiblePages + 1);
    }
    
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages
  });

  return {
    currentPage,
    itemsPerPage,
    totalItems,
    totalPages,
    paginatedTodos,
    visiblePages,
    goToPage
  }
};
