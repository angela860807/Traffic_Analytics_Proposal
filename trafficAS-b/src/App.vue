<template>
  <RouterView />
  <AuthModal />
</template>

<script setup>
import { RouterView } from 'vue-router'
import AuthModal from '@/components/AuthModal.vue'
</script>
