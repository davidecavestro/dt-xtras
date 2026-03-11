# Pagination Implementation for DT API

This document describes the pagination implementation for the Dependency-Track (DT) API integration in the frontend application.

## Overview

The DT API supports pagination for most list endpoints, allowing users to navigate through large datasets efficiently. This implementation provides:

1. **Reusable pagination components** - UI components for pagination controls
2. **Composable functions** - Vue 3 composables for pagination state management
3. **API service integration** - Service layer methods for paginated API calls
4. **Multiple list views** - Paginated views for Projects, Components, and Vulnerabilities

## Architecture

### 1. Pagination Component (`Pagination.vue`)

A reusable pagination component that provides:
- Page navigation (first, previous, next, last)
- Page size selector (10, 20, 50, 100 items)
- Current page display with item count
- Responsive design with dark mode support

### 2. Pagination Composables (`usePagination.js`)

Two composable functions:

#### `usePagination(options)`
Manages pagination state:
- Current page, page size, total items
- Navigation methods
- Loading and error states

#### `usePaginatedData(fetchFunction, options)`
Combines pagination with data fetching:
- Automatic data fetching on page changes
- Loading and error handling
- Refresh functionality

### 3. API Service (`api.js`)

Enhanced API service with pagination support:
- DT-specific pagination parameters (`pageNumber`, `pageSize`, `offset`, `limit`)
- Sorting support (`sortName`, `sortOrder`)
- Pagination metadata extraction
- Multiple DT endpoints with pagination

## DT API Pagination Details

Based on the DT OpenAPI specification, the API supports two pagination methods:

### Page-based Pagination
- `pageNumber`: Page number (1-based, default: 1)
- `pageSize`: Items per page (default: 100)
- `sortName`: Field to sort by
- `sortOrder`: Sort order (`asc` or `desc`)

### Offset-based Pagination
- `offset`: Starting offset (0-based)
- `limit`: Number of items to return
- `sortName`: Field to sort by
- `sortOrder`: Sort order (`asc` or `desc`)

### Supported Endpoints

The following DT endpoints support pagination:

1. **Projects** - `/v1/project` (`getProjects`)
2. **Vulnerabilities** - `/v1/vulnerability` (`getVulnerabilities`)
3. **Licenses** - `/v1/license` (`getLicenses`)
4. **CWEs** - `/v1/cwe` (`getCwes`)
5. **License Groups** - `/v1/licenseGroup` (`getLicenseGroups`)
6. **Team Projects** - `/v1/acl/team/{uuid}` (`retrieveProjects`)

## Implementation Examples

### Basic Usage in a Component

```vue
<template>
  <div>
    <!-- Data display -->
    <div v-for="item in data" :key="item.id">
      {{ item.name }}
    </div>

    <!-- Pagination controls -->
    <Pagination
      :current-page="pagination.currentPage"
      :page-size="pagination.pageSize"
      :total-items="pagination.totalItems"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />
  </div>
</template>

<script>
import { usePaginatedData } from '../composables/usePagination'
import apiService from '../services/api'
import Pagination from './Pagination.vue'

export default {
  components: { Pagination },
  setup() {
    const { data, pagination, fetchData } = usePaginatedData(
      async (params) => apiService.getProjects(params),
      { initialPageSize: 20 }
    )

    const handlePageChange = (page) => {
      pagination.setPage(page)
      fetchData()
    }

    const handlePageSizeChange = (pageSize) => {
      pagination.setPageSize(pageSize)
      fetchData()
    }

    return { data, pagination, handlePageChange, handlePageSizeChange }
  }
}
</script>
```

### Advanced Usage with Filters

```javascript
const { data, pagination, fetchData } = usePaginatedData(
  async (params) => {
    const queryParams = {
      search: filters.value.search,
      severity: filters.value.severity,
      activeOnly: filters.value.activeOnly
    }
    return apiService.getVulnerabilities(params, queryParams)
  },
  { initialPageSize: 50 }
)
```

## Features

### 1. Smart Pagination Detection
The API service automatically detects pagination metadata from:
- Response headers (`x-total-count`, `total-count`)
- Response data structure
- Inferred from array length when total is unknown


### 3. Filter Integration
Easily combine pagination with filters:
```javascript
apiService.getProjects(
  { page: 1, pageSize: 50 },
  { activeOnly: true, search: 'security' }
)
```

### 4. Error Handling
Built-in error handling for:
- Network errors
- API errors
- Invalid pagination parameters

### 5. Loading States
Automatic loading state management during:
- Initial data fetch
- Page navigation
- Page size changes

## Best Practices

1. **Use appropriate page sizes**: Start with 20-50 items for most lists
2. **Implement search**: Combine pagination with search for better UX
3. **Cache responses**: Consider caching frequently accessed pages
4. **Handle edge cases**: Empty states, loading states, and errors
5. **Responsive design**: Ensure pagination works on mobile devices

## Future Enhancements

1. **Infinite scrolling**: Alternative to traditional pagination
2. **URL synchronization**: Store pagination state in URL
3. **Bulk actions**: Select items across multiple pages
4. **Export functionality**: Export current page or all results
5. **Saved preferences**: Remember user's preferred page size

## Files

- `src/components/Pagination.vue` - Reusable pagination component
- `src/composables/usePagination.js` - Pagination composables
- `src/services/api.js` - API service with pagination support
- `src/components/ProjectsList.vue` - Projects list with pagination
- `src/components/VulnerabilitiesList.vue` - Vulnerabilities list with pagination

This implementation provides a comprehensive pagination solution that integrates seamlessly with the DT API while offering a great user experience.
