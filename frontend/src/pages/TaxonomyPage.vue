<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900">
    <TagsGraph />
  </div>
</template>

<script>
import TagsGraph from '../components/TagsGraph.vue';

export default {
  name: 'TaxonomyPage',
  components: {
    TagsGraph
  }
};
</script>
