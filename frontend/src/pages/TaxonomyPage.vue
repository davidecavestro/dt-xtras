<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900">
    <TaxonomyVisualization />
  </div>
</template>

<script>
import TaxonomyVisualization from '../components/TaxonomyVisualization.vue';

export default {
  name: 'TaxonomyPage',
  components: {
    TaxonomyVisualization
  }
};
</script>
