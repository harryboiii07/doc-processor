# Postman cURL Commands for Excel to JSON Conversion Service

## 1. Health Check Endpoint

```bash
curl --location 'http://localhost:8000/health' \
--header 'Accept: application/json'
```

## 2. Service Information Endpoint

```bash
curl --location 'http://localhost:8000/api/info' \
--header 'Accept: application/json'
```

## 3. Excel to JSON Conversion Endpoint

### Basic Excel File Upload
```bash
curl --location 'http://localhost:8000/api/convert-excel' \
--form 'file=@"/path/to/your/excel-file.xlsx"'
```

### With Additional Headers (Recommended for Postman)
```bash
curl --location 'http://localhost:8000/api/convert-excel' \
--header 'Accept: application/json' \
--form 'file=@"/path/to/your/excel-file.xlsx"'
```

### Example with Sample File (if you have test_sample.xlsx)
```bash
curl --location 'http://localhost:8000/api/convert-excel' \
--header 'Accept: application/json' \
--form 'file=@"test_sample.xlsx"'
```

## 4. Error Testing - Invalid File Type

```bash
curl --location 'http://localhost:8000/api/convert-excel' \
--header 'Accept: application/json' \
--form 'file=@"/path/to/text-file.txt"'
```

## 5. Error Testing - Missing File

```bash
curl --location 'http://localhost:8000/api/convert-excel' \
--header 'Accept: application/json' \
--header 'Content-Type: multipart/form-data'
```

## 6. Production Server Health Check (if using Docker)

```bash
curl --location 'http://localhost:8000/health' \
--header 'Accept: application/json' \
--header 'User-Agent: Postman/Production-Test'
```

## Expected Responses

### Health Check Response
```json
{
    "status": "healthy",
    "timestamp": "2025-01-01T12:00:00Z",
    "version": "1.0.0",
    "memory_usage": "45.2%",
    "system_info": {
        "cpu_usage": "12.5%",
        "memory_mb": 128.5,
        "available_memory_mb": 2048.0
    },
    "service_info": {
        "max_file_size_mb": 100,
        "supported_formats": [".xlsx", ".xls"],
        "batch_size": 1000
    }
}
```

### Successful Conversion Response
```json
{
    "success": true,
    "data": [
        {
            "Column1": "Column1",
            "__EMPTY": "__EMPTY",
            "__EMPTY_1": "__EMPTY_1"
        },
        {
            "Column1": "Value1",
            "__EMPTY": "Value2",
            "__EMPTY_1": "Value3"
        }
    ],
    "metadata": {
        "total_rows": 1,
        "processing_time": 0.009,
        "file_size": "0.0MB",
        "worksheet_name": "Sheet1",
        "file_type": "XLSX",
        "batch_size": 1000,
        "performance": {
            "rows_per_second": 457.74,
            "peak_memory_mb": 40.8,
            "total_batches": 1
        }
    }
}
```

### Error Response Example
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid request data",
        "details": {
            "file": ["This field is required."]
        }
    }
}
```

## Postman Import Instructions

1. **Open Postman**
2. **Click "Import" button**
3. **Select "Raw text" tab**
4. **Copy and paste any of the above cURL commands**
5. **Click "Continue" then "Import"**

### Alternative: Create Collection Manually

1. **Create New Collection**: "Excel to JSON Converter"
2. **Add Request**: Name it "Health Check"
   - Method: GET
   - URL: `http://localhost:8000/health`
   - Headers: `Accept: application/json`

3. **Add Request**: Name it "Convert Excel"
   - Method: POST
   - URL: `http://localhost:8000/api/convert-excel`
   - Body: form-data
   - Key: `file` (type: File)
   - Headers: `Accept: application/json`

4. **Add Request**: Name it "Service Info"
   - Method: GET
   - URL: `http://localhost:8000/api/info`
   - Headers: `Accept: application/json`

## Environment Variables for Postman

Create environment variables in Postman:
- `base_url`: `http://localhost:8000`
- `api_base`: `{{base_url}}/api`

Then use:
- Health: `{{base_url}}/health`
- Convert: `{{api_base}}/convert-excel`
- Info: `{{api_base}}/info`

## Testing Different File Sizes

### Small File Test (< 1MB)
```bash
curl --location 'http://localhost:8000/api/convert-excel' \
--header 'Accept: application/json' \
--form 'file=@"small_test.xlsx"' \
--write-out "Time: %{time_total}s\nSize: %{size_download} bytes\n"
```

### Large File Test (10-50MB)
```bash
curl --location 'http://localhost:8000/api/convert-excel' \
--header 'Accept: application/json' \
--form 'file=@"large_test.xlsx"' \
--max-time 300 \
--write-out "Time: %{time_total}s\nSize: %{size_download} bytes\n"
```

## Performance Testing Headers

Add these headers for performance monitoring:
```
Accept: application/json
User-Agent: Postman-Performance-Test
X-Request-ID: test-{{$timestamp}}
```

## Notes for Postman Testing

1. **File Upload**: Make sure to select the correct Excel file in the form-data body
2. **Timeout**: Set request timeout to 300 seconds for large files
3. **Response Format**: All responses are in JSON format
4. **Error Handling**: The service returns appropriate HTTP status codes
5. **Unicode Support**: The service handles Thai text and special characters correctly

## Quick Test Sequence

1. **Health Check** - Verify service is running
2. **Service Info** - Check configuration
3. **Small File** - Test basic functionality
4. **Error Cases** - Test validation
5. **Performance** - Test with larger files
