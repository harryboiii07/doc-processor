# Excel to JSON API - Column Mapping Examples

The Excel Converter API now supports optional column mapping configuration through the `data` parameter. This allows you to define how columns should be mapped and processed.

## 📋 **Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Required | Excel file (.xlsx/.xls) |
| `data` | JSON | Optional | Column mapping configuration |
| `page` | Query param | Optional | Page number for pagination |
| `limit` | Query param | Optional | Rows per page for pagination |

## 🚀 **Usage Examples**

### 1. **Without Column Mapping (Current Behavior)**
Standard conversion without any column mapping:

```bash
curl -X POST "http://localhost:8000/api/convert-excel" \
  -F "file=@sample.xlsx"
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "__EMPTY": "Row 1 Data",
      "__EMPTY_1": "More Data"
    }
  ],
  "metadata": {
    "total_rows": 100,
    "processing_time": 0.5
  }
}
```

### 2. **With Column Mapping**
Include column mapping configuration:

```bash
curl -X POST "http://localhost:8000/api/convert-excel" \
  -F "file=@sample.xlsx" \
  -F 'data=[{
    "required_columns": [
      {
        "field": "NO.",
        "header": "",
        "index": null
      },
      {
        "field": "INSURER",
        "header": "INDARA",
        "value": "INDARA"
      },
      {
        "field": "POLICY NO.",
        "header": "กรมธรรม์",
        "index": 5
      },
      {
        "field": "INSURANCE TYPE",
        "header": "ประเภท",
        "index": 4
      },
      {
        "field": "EFFECTIVE DATE",
        "header": "วันคุ้มครอง",
        "index": 1
      },
      {
        "field": "LICENSE",
        "header": "ทะเบียนรถ",
        "index": 8
      },
      {
        "field": "CHASSIS NUMBER",
        "header": "เลขตัวถัง",
        "index": 9
      }
    ]
  }]'
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "__EMPTY": "Row 1 Data",
      "__EMPTY_1": "More Data"
    }
  ],
  "metadata": {
    "total_rows": 100,
    "processing_time": 0.5
  },
  "headerrow": [
    {
      "required_columns": [
        {
          "field": "NO.",
          "header": "",
          "index": null
        },
        {
          "field": "INSURER",
          "header": "INDARA",
          "value": "INDARA"
        },
        {
          "field": "POLICY NO.",
          "header": "กรมธรรม์",
          "index": 5
        },
        {
          "field": "INSURANCE TYPE",
          "header": "ประเภท",
          "index": 4
        },
        {
          "field": "EFFECTIVE DATE",
          "header": "วันคุ้มครอง",
          "index": 1
        },
        {
          "field": "LICENSE",
          "header": "ทะเบียนรถ",
          "index": 8
        },
        {
          "field": "CHASSIS NUMBER",
          "header": "เลขตัวถัง",
          "index": 9
        }
      ]
    }
  ]
}
```

### 3. **With Pagination and Column Mapping**

```bash
curl -X POST "http://localhost:8000/api/convert-excel?page=1&limit=10" \
  -F "file=@sample.xlsx" \
  -F 'data=[{
    "required_columns": [
      {
        "field": "POLICY NO.",
        "header": "กรมธรรม์",
        "index": 5
      },
      {
        "field": "LICENSE",
        "header": "ทะเบียนรถ",
        "index": 8
      }
    ]
  }]'
```

Response includes both pagination and headerrow:
```json
{
  "success": true,
  "data": [
    // First 10 rows...
  ],
  "metadata": {
    "total_rows": 10,
    "original_total_rows": 1000
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_rows": 1000,
    "total_pages": 100,
    "has_next": true,
    "has_prev": false
  },
  "headerrow": [
    {
      "required_columns": [
        {
          "field": "POLICY NO.",
          "header": "กรมธรรม์",
          "index": 5
        },
        {
          "field": "LICENSE",
          "header": "ทะเบียนรถ",
          "index": 8
        }
      ]
    }
  ]
}
```

## 📊 **Column Mapping Structure**

The `data` parameter should be a JSON array containing objects with this structure:

```json
[
  {
    "required_columns": [
      {
        "field": "COLUMN_NAME",        // Required: Field identifier
        "header": "Display Header",    // Optional: Header text
        "index": 5,                    // Optional: Column index (0-based)
        "value": "Fixed Value"         // Optional: Fixed value for this field
      }
    ]
  }
]
```

### **Field Properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `field` | String | ✅ | Unique field identifier |
| `header` | String | ❌ | Display header text |
| `index` | Number | ❌ | Excel column index (0-based) |
| `value` | String | ❌ | Fixed value for this field |

## 🔧 **Use Cases**

### **1. Column Mapping Definition**
Define how Excel columns map to your data structure:

```json
{
  "field": "POLICY_NUMBER",
  "header": "กรมธรรม์", 
  "index": 5
}
```
*Maps Excel column 5 to POLICY_NUMBER field*

### **2. Fixed Values**
Set fixed values for certain fields:

```json
{
  "field": "INSURER",
  "header": "INDARA",
  "value": "INDARA"
}
```
*Always sets INSURER field to "INDARA"*

### **3. Header-Only Fields**
Fields with headers but no specific index:

```json
{
  "field": "NO.",
  "header": "",
  "index": null
}
```
*Field exists but no specific column mapping*

## ⚠️ **Validation**

### **Valid Data Parameter:**
```json
[
  {
    "required_columns": [
      {
        "field": "TEST_FIELD",
        "header": "Test Header"
      }
    ]
  }
]
```

### **Invalid Examples:**

**❌ Not an array:**
```json
{
  "required_columns": []
}
```

**❌ Missing required_columns:**
```json
[
  {
    "some_other_field": []
  }
]
```

**❌ required_columns not an array:**
```json
[
  {
    "required_columns": "invalid"
  }
]
```

## 💡 **Key Benefits**

1. **✅ Backward Compatible**: Works without data parameter
2. **📋 Column Mapping**: Define how columns should be processed  
3. **🔄 Passthrough**: Original mapping returned in response
4. **⚡ Performance**: No impact on processing speed
5. **📊 Metadata**: Includes mapping info for client processing

## 🧪 **Testing**

### **Test Without Data Parameter:**
```bash
curl -X POST "http://localhost:8000/api/convert-excel" \
  -F "file=@test.xlsx"
```
*Should work exactly as before*

### **Test With Data Parameter:**
```bash
curl -X POST "http://localhost:8000/api/convert-excel" \
  -F "file=@test.xlsx" \
  -F 'data=[{"required_columns":[{"field":"TEST","header":"Test"}]}]'
```
*Should include headerrow in response*

### **Test Invalid Data:**
```bash
curl -X POST "http://localhost:8000/api/convert-excel" \
  -F "file=@test.xlsx" \
  -F 'data="invalid"'
```
*Should return validation error*

---

🎉 **The API now supports flexible column mapping while maintaining full backward compatibility!**
