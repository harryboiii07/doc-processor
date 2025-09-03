"""
Serializers for Excel conversion API.
"""
import magic
from rest_framework import serializers


class ExcelFileUploadSerializer(serializers.Serializer):
    """
    Serializer for Excel file upload validation.
    """
    file = serializers.FileField()

    def validate_file(self, value):
        """
        Validate uploaded file is a valid Excel file.
        """
        # Check file size (100MB limit)
        max_size = 100 * 1024 * 1024  # 100MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size too large. Maximum allowed size is {max_size / (1024 * 1024):.0f}MB. "
                f"Uploaded file is {value.size / (1024 * 1024):.1f}MB."
            )

        # Check file extension
        allowed_extensions = ['.xlsx', '.xls']
        file_extension = None
        if hasattr(value, 'name') and value.name:
            file_extension = '.' + value.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise serializers.ValidationError(
                    f"Invalid file extension '{file_extension}'. "
                    f"Allowed extensions: {', '.join(allowed_extensions)}"
                )

        # Validate file type using python-magic (more reliable than extension)
        try:
            # Read first few bytes to determine file type
            value.seek(0)
            file_header = value.read(1024)
            value.seek(0)  # Reset file pointer
            
            mime_type = magic.from_buffer(file_header, mime=True)
            
            # Valid MIME types for Excel files
            valid_mime_types = [
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
                'application/vnd.ms-excel',  # .xls
                'application/zip',  # Sometimes .xlsx files are detected as zip
                'application/octet-stream',  # Generic binary, but check extension
            ]
            
            if mime_type not in valid_mime_types:
                raise serializers.ValidationError(
                    f"Invalid file type. Expected Excel file (.xlsx/.xls), "
                    f"but got '{mime_type}'. File extension: {file_extension}"
                )
            
            # Additional validation for generic mime types
            if mime_type in ['application/octet-stream', 'application/zip']:
                if file_extension not in allowed_extensions:
                    raise serializers.ValidationError(
                        f"File type '{mime_type}' requires valid Excel extension. "
                        f"Got '{file_extension}', expected one of: {', '.join(allowed_extensions)}"
                    )
                
                # For .xlsx files, check if it's actually a ZIP archive (which .xlsx files are)
                if file_extension == '.xlsx':
                    # Check for ZIP file signature (PK header)
                    if len(file_header) >= 4 and file_header[:2] == b'PK':
                        # This is likely a valid .xlsx file (ZIP-based format)
                        pass
                    else:
                        raise serializers.ValidationError(
                            "File appears to be corrupted or not a valid Excel file"
                        )
                        
        except serializers.ValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            # For other exceptions, provide a more user-friendly message
            raise serializers.ValidationError(
                f"Unable to validate file: {str(e)}. Please ensure the file is a valid Excel file."
            )

        # Check if file is empty
        if value.size == 0:
            raise serializers.ValidationError("Uploaded file is empty.")

        return value


class ExcelConversionResponseSerializer(serializers.Serializer):
    """
    Serializer for successful Excel conversion response.
    """
    success = serializers.BooleanField(default=True)
    data = serializers.ListField(
        child=serializers.DictField(),
        help_text="Array of objects representing Excel rows"
    )
    metadata = serializers.DictField(
        help_text="Processing metadata including row count, processing time, etc."
    )
    pagination = serializers.DictField(
        required=False,
        help_text="Pagination information (present when pagination is used)"
    )


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer for error responses.
    """
    success = serializers.BooleanField(default=False)
    error = serializers.DictField(
        help_text="Error details including code, message, and specific details"
    )


class HealthCheckResponseSerializer(serializers.Serializer):
    """
    Serializer for health check response.
    """
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    version = serializers.CharField()
    memory_usage = serializers.CharField()
