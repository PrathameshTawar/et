"""
DynamoDB Service for SatyaSetu
Handles user scan history storage and retrieval
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from decimal import Decimal

# Only import for type checking - will work at runtime with boto3 installed
if TYPE_CHECKING:
    import boto3
    from boto3.dynamodb.conditions import Key, Attr

from config import settings
from core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class DynamoDBService:
    """DynamoDB service for storing and retrieving scan history"""
    
    def __init__(self, table_name: str = "satyasetu-scan-history"):
        self.table_name: str = table_name
        self.client: Any = None  # boto3 dynamodb resource  
        self.table: Any = None   # DynamoDB Table
        
    def initialize(self, aws_access_key_id: Optional[str] = None, 
                   aws_secret_access_key: Optional[str] = None, 
                   aws_region: Optional[str] = None) -> None:
        """Initialize DynamoDB connection"""
        try:
            # Import boto3 at runtime
            import boto3
            
            self.client = boto3.resource(
                'dynamodb',
                aws_access_key_id=aws_access_key_id or settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws_secret_access_key or settings.AWS_SECRET_ACCESS_KEY,
                region_name=aws_region or settings.AWS_REGION
            )
            self.table = self.client.Table(self.table_name)
            logger.info(f"DynamoDB initialized with table: {self.table_name}")
        except ImportError:
            logger.warning("boto3 not installed. Using mock mode.")
            self.client = None
            self.table = None
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB: {e}")
            raise ExternalServiceError("dynamodb", str(e))
    
    async def save_scan(self, user_id: str, scan_data: Dict[str, Any]) -> bool:
        """Save a scan record to DynamoDB"""
        try:
            if not self.table:
                self.initialize()
            
            # If no real DynamoDB, just log and return success (mock mode)
            if not self.table:
                logger.info(f"Mock: Would save scan for user {user_id}")
                return True
            
            item = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'scan_type': scan_data.get('scan_type', 'text'),
                'input_text': scan_data.get('input_text', ''),
                'verdict': scan_data.get('verdict', 'UNKNOWN'),
                'risk_level': scan_data.get('risk_level', 'UNKNOWN'),
                'confidence_score': Decimal(str(scan_data.get('confidence_score', 0.0))),
                'response': scan_data.get('response', ''),
                'sources': scan_data.get('sources', []),
                'risk_flags': scan_data.get('risk_flags', []),
                'metadata': {
                    'language': scan_data.get('language', 'hi'),
                    'processing_time': Decimal(str(scan_data.get('processing_time', 0.0)))
                }
            }
            
            await asyncio.to_thread(self.table.put_item, Item=item)
            logger.info(f"Scan saved for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save scan: {e}")
            return False
    
    async def get_user_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get scan history for a specific user"""
        try:
            if not self.table:
                self.initialize()
            
            if not self.table:
                logger.info(f"Mock: Would get history for user {user_id}")
                return []
            
            # Import Key for type checking
            from boto3.dynamodb.conditions import Key
            
            response = await asyncio.to_thread(
                self.table.query,
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=False,
                Limit=limit
            )
            
            items = response.get('Items', [])
            return [self._convert_decimals(item) for item in items]
            
        except Exception as e:
            logger.error(f"Failed to get user history: {e}")
            return []
    
    async def get_recent_scans(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent scans across all users"""
        try:
            if not self.table:
                self.initialize()
            
            if not self.table:
                logger.info("Mock: Would get recent scans")
                return []
            
            response = await asyncio.to_thread(
                self.table.scan,
                Limit=limit
            )
            
            items = response.get('Items', [])
            return [self._convert_decimals(item) for item in items]
            
        except Exception as e:
            logger.error(f"Failed to get recent scans: {e}")
            return []
    
    async def delete_scan(self, user_id: str, timestamp: str) -> bool:
        """Delete a specific scan record"""
        try:
            if not self.table:
                self.initialize()
            
            if not self.table:
                logger.info(f"Mock: Would delete scan for user {user_id}")
                return True
            
            await asyncio.to_thread(
                self.table.delete_item,
                Key={
                    'user_id': user_id,
                    'timestamp': timestamp
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete scan: {e}")
            return False
    
    def _convert_decimals(self, item: Dict) -> Dict:
        """Convert Decimal types to float for JSON serialization"""
        result = {}
        for key, value in item.items():
            if isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, dict):
                result[key] = self._convert_decimals(value)
            elif isinstance(value, list):
                result[key] = [
                    float(v) if isinstance(v, Decimal) else v for v in value
                ]
            else:
                result[key] = value
        return result


# Singleton instance
dynamodb_service = DynamoDBService()


def get_dynamodb_service() -> DynamoDBService:
    """Get the DynamoDB service instance"""
    return dynamodb_service
