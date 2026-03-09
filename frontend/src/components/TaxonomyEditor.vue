<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="border-4 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Taxonomy Editor</h2>
        <button
          @click="createNewTaxonomy"
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          <Plus class="inline w-4 h-4 mr-2" />
          Add Taxonomy
        </button>
      </div>

      <!-- Taxonomy Form -->
      <div v-if="editingTaxonomy" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          {{ isEditingExisting ? 'Edit Taxonomy' : 'Create Taxonomy' }}
        </h3>

        <div class="grid grid-cols-1 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              ID
              <span v-if="isEditingExisting" class="ml-2 text-xs text-gray-500 dark:text-gray-400">(read-only when editing)</span>
            </label>
            <input
              :value="editingTaxonomy.id"
              @input="editingTaxonomy.id = $event.target.value"
              type="text"
              :disabled="isEditingExisting"
              :class="[
                'mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                isEditingExisting
                  ? 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                  : 'border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white'
              ]"
              placeholder="e.g., customer, env, product"
            />
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Unique identifier for this taxonomy level</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
            <input
              v-model="editingTaxonomy.name"
              type="text"
              class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white"
              placeholder="e.g., Customer, Environment, Product"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Priority</label>
            <input
              v-model.number="editingTaxonomy.priority"
              type="number"
              class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white"
              placeholder="Lower numbers = higher priority"
            />
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Lower numbers are processed first (higher priority)</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Regex Pattern</label>
            <textarea
              v-model="editingTaxonomy.pattern"
              rows="3"
              class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white"
              placeholder="e.g., ^cust:(?P<id>\w+)$"
            ></textarea>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Use named capture groups (?P&lt;name&gt;pattern) to extract values.
              The group name should match the taxonomy ID for relations.
            </p>
          </div>

          <!-- Relations Section -->
          <div class="mt-6">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Relations (Optional)</h4>
            <div class="space-y-4">
              <div v-for="(relation, index) in editingTaxonomy.relations" :key="index" class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <div class="grid grid-cols-1 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Group Name</label>
                    <input
                      v-model="relation.group"
                      type="text"
                      class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white"
                      placeholder="e.g., customer"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Target Taxonomy</label>
                    <input
                      v-model="relation.targets"
                      type="text"
                      class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white"
                      placeholder="e.g., customer"
                    />
                  </div>
                  <div class="mt-2">
                    <button
                      @click="removeRelation(index)"
                      class="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700"
                    >
                      Remove Relation
                    </button>
                  </div>
                </div>
              </div>
              <button
                @click="addRelation"
                class="px-3 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
              >
                Add Relation
              </button>
            </div>
          </div>
        </div>

        <!-- Regex Tester -->
        <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Test Regex Pattern</h4>
          <div class="grid grid-cols-1 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Test Tags</label>
              <input
                v-model="testTags"
                type="text"
                class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white"
                placeholder="e.g., customer:acme env:production product:webapp"
              />
            </div>

            <div>
              <button
                @click="testRegex"
                :disabled="!editingTaxonomy.regex_pattern || !testTags"
                class="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                Test Pattern
              </button>
            </div>

            <div v-if="regexTestResult" class="mt-3">
              <div v-if="regexTestResult.match" class="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
                <p class="text-sm font-medium text-green-800 dark:text-green-200">✅ Match Found</p>
                <pre class="mt-2 text-xs text-green-700 dark:text-green-300">{{ JSON.stringify(regexTestResult.groups, null, 2) }}</pre>
              </div>
              <div v-else class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                <p class="text-sm font-medium text-red-800 dark:text-red-200">❌ No Match</p>
                <p v-if="regexTestResult.error" class="mt-1 text-xs text-red-700 dark:text-red-300">{{ regexTestResult.error }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 flex justify-end space-x-3">
          <button
            @click="cancelEdit"
            class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Cancel
          </button>
          <button
            @click="saveTaxonomy"
            :disabled="!isFormValid"
            class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            Save
          </button>
        </div>
      </div>

      <!-- Taxonomies List -->
      <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Existing Taxonomies</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
            Taxonomies are processed in priority order (lower numbers first)
          </p>
        </div>

        <ul class="divide-y divide-gray-200 dark:divide-gray-700">
          <li v-for="taxonomy in sortedTaxonomies" :key="taxonomy.id">
            <div class="px-4 py-4 flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center">
                  <span class="text-sm font-medium text-gray-900 dark:text-white">{{ taxonomy.name }}</span>
                  <span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200">
                    {{ taxonomy.id }}
                  </span>
                  <span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                    Priority: {{ taxonomy.priority }}
                  </span>
                </div>
                <div class="mt-1">
                  <code class="text-xs bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-gray-800 dark:text-gray-200">{{ taxonomy.regex_pattern }}</code>
                </div>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="editTaxonomy(taxonomy)"
                  class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                >
                  <Edit class="w-4 h-4" />
                </button>
                <button
                  @click="deleteTaxonomy(taxonomy.id)"
                  class="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </li>
        </ul>

        <div v-if="taxonomies.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No taxonomies defined yet. Create your first taxonomy to get started.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { Plus, Edit, Trash2 } from 'lucide-vue-next'
import axios from 'axios'

export default {
  name: 'TaxonomyEditor',
  components: {
    Plus,
    Edit,
    Trash2
  },
  setup() {
    const taxonomies = ref([])
    const editingTaxonomy = ref(null)
    const testTags = ref('')
    const regexTestResult = ref(null)

    const sortedTaxonomies = computed(() => {
      return [...taxonomies.value].sort((a, b) => a.priority - b.priority)
    })

    const isFormValid = computed(() => {
      return editingTaxonomy.value &&
             editingTaxonomy.value.id &&
             editingTaxonomy.value.name &&
             editingTaxonomy.value.pattern !== undefined &&
             editingTaxonomy.value.priority !== undefined
    })

    const isEditingExisting = computed(() => {
      return editingTaxonomy.value &&
             taxonomies.value.some(t => t.id === editingTaxonomy.value.id)
    })

    const loadTaxonomies = async () => {
      try {
        const response = await axios.get('/api/taxonomies')
        taxonomies.value = response.data
      } catch (error) {
        console.error('Error loading taxonomies:', error)
      }
    }

    const createNewTaxonomy = () => {
      editingTaxonomy.value = {
        id: '',
        name: '',
        pattern: '',
        priority: taxonomies.value.length + 1,
        relations: []
      }
      testTags.value = ''
      regexTestResult.value = null
    }

    const editTaxonomy = (taxonomy) => {
      editingTaxonomy.value = {
        ...taxonomy,
        relations: taxonomy.relations || []
      }
      testTags.value = ''
      regexTestResult.value = null
    }

    const addRelation = () => {
      if (!editingTaxonomy.value.relations) {
        editingTaxonomy.value.relations = []
      }
      editingTaxonomy.value.relations.push({
        group: '',
        targets: ''
      })
    }

    const removeRelation = (index) => {
      editingTaxonomy.value.relations.splice(index, 1)
    }

    const cancelEdit = () => {
      editingTaxonomy.value = null
      testTags.value = ''
      regexTestResult.value = null
    }

    const saveTaxonomy = async () => {
      try {
        if (editingTaxonomy.value.id && taxonomies.value.some(t => t.id === editingTaxonomy.value.id && t !== editingTaxonomy.value)) {
          // Update existing
          await axios.put(`/api/taxonomies/${editingTaxonomy.value.id}`, editingTaxonomy.value)
        } else {
          // Create new
          await axios.post('/api/taxonomies', editingTaxonomy.value)
        }

        await loadTaxonomies()
        cancelEdit()
      } catch (error) {
        console.error('Error saving taxonomy:', error)
        alert('Error saving taxonomy: ' + (error.response?.data?.detail || error.message))
      }
    }

    const deleteTaxonomy = async (id) => {
      if (!confirm('Are you sure you want to delete this taxonomy?')) {
        return
      }

      try {
        await axios.delete(`/api/taxonomies/${id}`)
        await loadTaxonomies()
      } catch (error) {
        console.error('Error deleting taxonomy:', error)
        alert('Error deleting taxonomy: ' + (error.response?.data?.detail || error.message))
      }
    }

    const testRegex = () => {
      if (!editingTaxonomy.value.pattern || !testTags.value) {
        return
      }

      try {
        const regex = new RegExp(editingTaxonomy.value.pattern)
        const match = testTags.value.match(regex)

        if (match) {
          regexTestResult.value = {
            match: true,
            groups: match.groups || {}
          }
        } else {
          regexTestResult.value = {
            match: false,
            groups: null
          }
        }
      } catch (error) {
        regexTestResult.value = {
          match: false,
          groups: null,
          error: error.message
        }
      }
    }

    onMounted(() => {
      loadTaxonomies()
    })

    return {
      taxonomies,
      editingTaxonomy,
      testTags,
      regexTestResult,
      sortedTaxonomies,
      isFormValid,
      isEditingExisting,
      createNewTaxonomy,
      editTaxonomy,
      cancelEdit,
      saveTaxonomy,
      deleteTaxonomy,
      testRegex,
      addRelation,
      removeRelation
    }
  }
}
</script>
