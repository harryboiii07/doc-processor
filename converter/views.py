"""
API views for Excel conversion service.
"""
import logging
import time
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import psutil

from .serializers import (
    ExcelFileUploadSerializer,
    ExcelConversionResponseSerializer,
    ErrorResponseSerializer,
    HealthCheckResponseSerializer
)
from .utils import process_excel_streaming, ExcelProcessingError

logger = logging.getLogger('converter')


class ConvertExcelView(APIView):
    """
    API endpoint for converting Excel files to JSON format.
    
    POST /api/convert-excel?page=1&limit=1000
    - Input: Binary Excel file (multipart/form-data)
    - Query Parameters (optional):
      - page: Page number (starts from 1)
      - limit: Number of rows per page (max 100,000)
    - Output: JSON array with each row as an object
    - Max file size: 100MB
    - Supported formats: .xlsx, .xls
    """
    parser_classes = [MultiPartParser]
    
    def post(self, request, *args, **kwargs):
        """
        Convert uploaded Excel file to JSON format.
        """
        request_start_time = time.time()
        request_id = f"req_{int(request_start_time * 1000)}"
        
        # Log request received
        logger.info(
            f"Request received - ID: {request_id}, "
            f"Content-Length: {request.META.get('CONTENT_LENGTH', 'unknown')}, "
            f"Content-Type: {request.META.get('CONTENT_TYPE', 'unknown')}"
        )
        
        try:
            # Validate request data
            serializer = ExcelFileUploadSerializer(data=request.data)
            if not serializer.is_valid():
                error_response = {
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid request data',
                        'details': serializer.errors
                    }
                }
                logger.warning(
                    f"Validation failed - ID: {request_id}, "
                    f"Errors: {serializer.errors}"
                )
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            
            uploaded_file = serializer.validated_data['file']
            
            # Extract pagination parameters from query parameters
            page = request.query_params.get('page')
            limit = request.query_params.get('limit')
            
            # Validate pagination parameters
            if page is not None or limit is not None:
                try:
                    if page is not None:
                        page = int(page)
                        if page < 1:
                            raise ValueError("Page must be >= 1")
                    if limit is not None:
                        limit = int(limit)
                        if limit < 1:
                            raise ValueError("Limit must be >= 1")
                        if limit > 100000:
                            raise ValueError("Limit cannot exceed 100,000")
                    
                    # Both parameters must be provided together
                    if (page is not None and limit is None) or (page is None and limit is not None):
                        error_response = {
                            'success': False,
                            'error': {
                                'code': 'VALIDATION_ERROR',
                                'message': 'Invalid pagination parameters',
                                'details': "Both 'page' and 'limit' query parameters must be provided together for pagination."
                            }
                        }
                        logger.warning(
                            f"Pagination validation failed - ID: {request_id}, "
                            f"Page: {page}, Limit: {limit}"
                        )
                        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
                        
                except (ValueError, TypeError) as e:
                    error_response = {
                        'success': False,
                        'error': {
                            'code': 'VALIDATION_ERROR',
                            'message': 'Invalid pagination parameters',
                            'details': f"Invalid pagination parameter: {str(e)}"
                        }
                    }
                    logger.warning(
                        f"Pagination parameter error - ID: {request_id}, "
                        f"Page: {request.query_params.get('page')}, "
                        f"Limit: {request.query_params.get('limit')}, "
                        f"Error: {str(e)}"
                    )
                    return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            
            # Log processing started
            pagination_info = f", Page: {page}, Limit: {limit}" if page and limit else ""
            logger.info(
                f"Processing started - ID: {request_id}, "
                f"File: {uploaded_file.name}, "
                f"Size: {uploaded_file.size / (1024 * 1024):.1f}MB, "
                f"Type: {uploaded_file.content_type}{pagination_info}"
            )
            
            # Process the Excel file
            try:
                result = process_excel_streaming(uploaded_file, batch_size=1000, page=page, limit=limit)
                
                # Log successful processing
                processing_time = time.time() - request_start_time
                logger.info(
                    f"Processing completed - ID: {request_id}, "
                    f"Rows: {result['metadata']['total_rows']}, "
                    f"Time: {processing_time:.2f}s, "
                    f"Speed: {result['metadata']['performance']['rows_per_second']} rows/sec"
                )
                
                # Validate response format
                response_serializer = ExcelConversionResponseSerializer(data=result)
                if response_serializer.is_valid():
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    logger.error(
                        f"Response validation failed - ID: {request_id}, "
                        f"Errors: {response_serializer.errors}"
                    )
                    raise ExcelProcessingError("Internal error: Invalid response format")
                    
            except ExcelProcessingError as e:
                error_response = {
                    'success': False,
                    'error': {
                        'code': 'PROCESSING_ERROR',
                        'message': 'Failed to process Excel file',
                        'details': str(e)
                    }
                }
                logger.error(
                    f"Processing error - ID: {request_id}, "
                    f"File: {uploaded_file.name}, "
                    f"Error: {str(e)}"
                )
                return Response(error_response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                
            except MemoryError as e:
                error_response = {
                    'success': False,
                    'error': {
                        'code': 'MEMORY_ERROR',
                        'message': 'File too large to process in available memory',
                        'details': 'Try uploading a smaller file or contact support'
                    }
                }
                logger.error(
                    f"Memory error - ID: {request_id}, "
                    f"File: {uploaded_file.name}, "
                    f"Size: {uploaded_file.size / (1024 * 1024):.1f}MB"
                )
                return Response(error_response, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
                
        except Exception as e:
            # Handle unexpected errors
            error_response = {
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An unexpected error occurred',
                    'details': str(e) if settings.DEBUG else 'Please contact support'
                }
            }
            logger.error(
                f"Unexpected error - ID: {request_id}, "
                f"Error: {str(e)}, "
                f"Type: {type(e).__name__}"
            )
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            # Log request completion
            total_time = time.time() - request_start_time
            logger.info(
                f"Request completed - ID: {request_id}, "
                f"Total time: {total_time:.2f}s"
            )


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring service status.
    
    GET /health
    Returns service health status, version, and basic metrics.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Return health check information.
        """
        try:
            # Get current memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1)
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'version': getattr(settings, 'APP_VERSION', '1.0.0'),
                'memory_usage': f"{memory_percent:.1f}%",
                'system_info': {
                    'cpu_usage': f"{cpu_percent:.1f}%",
                    'memory_mb': round(memory_info.rss / (1024 * 1024), 1),
                    'available_memory_mb': round(psutil.virtual_memory().available / (1024 * 1024), 1)
                },
                'service_info': {
                    'max_file_size_mb': settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024),
                    'supported_formats': ['.xlsx', '.xls'],
                    'batch_size': 1000
                }
            }
            
            # Validate response
            serializer = HealthCheckResponseSerializer(data=health_data)
            if serializer.is_valid():
                return Response(health_data, status=status.HTTP_200_OK)
            else:
                # Fallback response if validation fails
                return Response({
                    'status': 'healthy',
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'version': getattr(settings, 'APP_VERSION', '1.0.0'),
                    'memory_usage': 'unknown'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            # Return degraded status if health check itself fails
            return Response({
                'status': 'degraded',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'version': getattr(settings, 'APP_VERSION', '1.0.0'),
                'memory_usage': 'unknown',
                'error': str(e) if settings.DEBUG else 'Health check error'
            }, status=status.HTTP_200_OK)


# Additional utility view for testing
class ServiceInfoView(APIView):
    """
    Service information endpoint for debugging and monitoring.
    
    GET /api/info
    Returns detailed service configuration and capabilities.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Return detailed service information.
        """
        try:
            service_info = {
                'service': 'Excel to JSON Converter',
                'version': getattr(settings, 'APP_VERSION', '1.0.0'),
                'django_version': getattr(settings, 'DJANGO_VERSION', 'unknown'),
                'configuration': {
                    'max_file_size_mb': settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024),
                    'max_memory_size_mb': settings.DATA_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024),
                    'supported_formats': ['.xlsx', '.xls'],
                    'batch_size': 1000,
                    'debug_mode': settings.DEBUG
                },
                'endpoints': {
                    'convert': '/api/convert-excel',
                    'health': '/health',
                    'info': '/api/info'
                },
                'system': {
                    'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
                    'cpu_count': psutil.cpu_count(),
                    'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2)
                }
            }
            
            return Response(service_info, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Service info error: {str(e)}")
            return Response({
                'error': 'Unable to retrieve service information',
                'details': str(e) if settings.DEBUG else 'Internal error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)