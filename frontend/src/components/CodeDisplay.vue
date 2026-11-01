<script setup>
defineProps({
  code: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})
</script>

<template>
  <div class="code" :class="{ dim: loading }">{{ code || '····' }}</div>
</template>