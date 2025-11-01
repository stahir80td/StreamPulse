"""
Avro serialization utilities
"""

import avro.schema
import avro.io
import io
import os

class AvroSerializer:
    """Handles Avro serialization for ContentDownloadEvent"""
    
    def __init__(self, schema_path: str):
        """
        Initialize serializer with Avro schema
        
        Args:
            schema_path: Path to .avsc schema file
        """
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r') as f:
            self.schema = avro.schema.parse(f.read())
        
        print(f"✅ Loaded Avro schema from {schema_path}")
    
    def serialize(self, event_dict: dict) -> bytes:
        """
        Serialize event dictionary to Avro binary format
        
        Args:
            event_dict: Event data as dictionary
            
        Returns:
            Binary Avro-encoded bytes
        """
        writer = avro.io.DatumWriter(self.schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(event_dict, encoder)
        return bytes_writer.getvalue()
    
    def deserialize(self, event_bytes: bytes) -> dict:
        """
        Deserialize Avro binary to event dictionary (for testing)
        
        Args:
            event_bytes: Binary Avro-encoded data
            
        Returns:
            Event data as dictionary
        """
        bytes_reader = io.BytesIO(event_bytes)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(self.schema)
        return reader.read(decoder)