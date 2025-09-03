# Excel to JSON API - Pagination Examples

The Excel Converter API now supports pagination to handle large Excel files efficiently. This allows you to process files in chunks rather than loading all data at once.

## 📋 **Pagination Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | Optional | Page number (starts from 1) |
| `limit` | integer | Optional | Number of rows per page (max 100,000) |

**Important**: Both `page` and `limit` must be provided together. You cannot use one without the other.

## 🚀 **Usage Examples**

### 1. **Without Pagination (Default Behavior)**
Returns all rows from the Excel file:

```bash
curl -X POST http://localhost:8000/api/convert-excel \
  -F "file=@sample.xlsx" \
  -H "Accept: application/json"
```

### 2. **First 10 Rows (Page 1, Limit 10)**

```bash
curl -X POST "http://localhost:8000/api/convert-excel?page=1&limit=10" \
  -F "file=@sample.xlsx" \
  -H "Accept: application/json"
```

### 3. **Rows 11-20 (Page 2, Limit 10)**

```bash
curl -X POST "http://localhost:8000/api/convert-excel?page=2&limit=10" \
  -F "file=@sample.xlsx" \
  -H "Accept: application/json"
```

### 4. **Large Chunks (Page 1, Limit 1000)**

```bash
curl -X POST "http://localhost:8000/api/convert-excel?page=1&limit=1000" \
  -F "file=@sample.xlsx" \
  -H "Accept: application/json"
```

### 5. **Third Set of 10,000 Rows (Page 3, Limit 10000)**

```bash
curl -X POST "http://localhost:8000/api/convert-excel?page=3&limit=10000" \
  -F "file=@sample.xlsx" \
  -H "Accept: application/json"
```

## 📊 **Response Format**

### **With Pagination**

When pagination parameters are provided, the response includes additional pagination metadata:

```json
{
  "success": true,
  "data": [
    {
      "__EMPTY": "Row 1 Data",
      "__EMPTY_1": "More Data"
    },
    {
      "__EMPTY": "Row 2 Data", 
      "__EMPTY_1": "More Data"
    }
  ],
  "metadata": {
    "total_rows": 10,
    "original_total_rows": 1000,
    "processing_time": 0.125,
    "file_size": "2.1MB",
    "file_type": "XLSX"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_rows": 1000,
    "total_pages": 100,
    "current_page_rows": 10,
    "has_next": true,
    "has_prev": false,
    "start_index": 1,
    "end_index": 10
  }
}
```

### **Without Pagination**

When no pagination parameters are provided, the response format remains the same as before:

```json
{
  "success": true,
  "data": [
    // All rows from the Excel file
  ],
  "metadata": {
    "total_rows": 1000,
    "original_total_rows": 1000,
    "processing_time": 2.345,
    "file_size": "2.1MB",
    "file_type": "XLSX"
  }
  // No pagination field
}
```

## 🔧 **Pagination Metadata Explained**

| Field | Description |
|-------|-------------|
| `page` | Current page number |
| `limit` | Rows per page limit |
| `total_rows` | Total number of rows in the entire file |
| `total_pages` | Total number of pages available |
| `current_page_rows` | Number of rows in the current page |
| `has_next` | Whether there are more pages after this one |
| `has_prev` | Whether there are pages before this one |
| `start_index` | Starting row number (1-based) |
| `end_index` | Ending row number (1-based) |

## 💡 **Use Cases**

### **1. Large File Processing**
For files with 100,000+ rows, use pagination to avoid memory issues:
```bash
# Process first 10,000 rows
curl -X POST "http://localhost:8000/api/convert-excel?page=1&limit=10000" \
  -F "file=@large_file.xlsx"
```

### **2. Progressive Data Loading**
Load data progressively in your application:
```javascript
// JavaScript example
async function loadExcelData(file, page = 1, limit = 1000) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('page', page);
  formData.append('limit', limit);
  
  const response = await fetch('/api/convert-excel', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
}

// Load first page
const firstPage = await loadExcelData(file, 1, 1000);
console.log(`Showing ${firstPage.pagination.current_page_rows} of ${firstPage.pagination.total_rows} rows`);
```

### **3. Data Preview**
Show just the first few rows for preview:
```bash
# Get first 5 rows for preview
curl -X POST "http://localhost:8000/api/convert-excel?page=1&limit=5" \
  -F "file=@sample.xlsx"
```

## ⚠️ **Edge Cases**

### **1. Page Beyond Available Data**
If you request a page that doesn't exist, you'll get an empty result:

```bash
# File has 100 rows, requesting page 2 with limit 100
curl -X POST "http://localhost:8000/api/convert-excel?page=2&limit=100" \
  -F "file=@100_rows.xlsx"
```

Response:
```json
{
  "success": true,
  "data": [],
  "metadata": {
    "total_rows": 0,
    "original_total_rows": 100
  },
  "pagination": {
    "page": 2,
    "limit": 100,
    "total_rows": 100,
    "total_pages": 1,
    "current_page_rows": 0,
    "has_next": false,
    "has_prev": true,
    "start_index": 0,
    "end_index": 0
  }
}
```

### **2. Invalid Parameters**
```bash
# This will return an error - page without limit
curl -X POST "http://localhost:8000/api/convert-excel?page=1" \
  -F "file=@sample.xlsx"
```

Error Response:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid pagination parameters",
    "details": "Both 'page' and 'limit' query parameters must be provided together for pagination."
  }
}
```

## 🎯 **Best Practices**

1. **Start Small**: Begin with smaller limits (100-1000) to test your integration
2. **Monitor Performance**: Larger limits process faster but use more memory
3. **Handle Empty Pages**: Always check `current_page_rows` to handle empty results
4. **Use Metadata**: Leverage pagination metadata to build navigation UI
5. **Error Handling**: Always handle validation errors for missing parameters

## 📈 **Performance Considerations**

- **Memory Usage**: Pagination reduces memory usage for large files
- **Processing Speed**: Smaller pages process faster but require more requests
- **Network Overhead**: Balance page size vs. number of requests
- **Recommended Limits**:
  - Preview: 5-20 rows
  - UI Display: 50-200 rows
  - Bulk Processing: 1,000-10,000 rows
  - Maximum: 100,000 rows per page

---

🎉 **Happy paginating!** This feature makes it much easier to work with large Excel files efficiently.
