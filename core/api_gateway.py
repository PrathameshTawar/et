"""
AWS API Gateway Integration for SatyaSetu
Provides API Gateway client and configuration for AWS deployment
"""

import asyncio
import logging
from typing import Optional, Dict, Any, TYPE_CHECKING

# Only import for type checking - will work at runtime with boto3 installed
if TYPE_CHECKING:
    import boto3
    from botocore.exceptions import ClientError

from config import settings
from core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class APIGatewayService:
    """AWS API Gateway service for managing REST APIs"""
    
    def __init__(self, aws_access_key_id: Optional[str] = None, 
                 aws_secret_access_key: Optional[str] = None, 
                 aws_region: Optional[str] = None):
        self.aws_access_key_id: str = aws_access_key_id or settings.AWS_ACCESS_KEY_ID or ""
        self.aws_secret_access_key: str = aws_secret_access_key or settings.AWS_SECRET_ACCESS_KEY or ""
        self.aws_region: str = aws_region or settings.AWS_REGION or "ap-south-1"
        
        self.client: Optional[Any] = None
        self.api_id: Optional[str] = None
        
    def initialize(self) -> None:
        """Initialize API Gateway client"""
        try:
            import boto3
            
            self.client = boto3.client(
                'apigateway',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
            logger.info("API Gateway client initialized")
        except ImportError:
            logger.warning("boto3 not installed. Using mock mode.")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize API Gateway: {e}")
            raise ExternalServiceError("api_gateway", str(e))
    
    async def create_api(self, name: str, description: str = "") -> Optional[str]:
        """Create a new REST API"""
        try:
            if not self.client:
                self.initialize()
            
            if not self.client:
                logger.info(f"Mock: Would create API {name}")
                self.api_id = f"mock-api-{name}"
                return self.api_id
            
            response = await asyncio.to_thread(
                self.client.create_rest_api,
                name=name,
                description=description,
                endpointConfiguration={
                    'types': ['REGIONAL']
                }
            )
            
            self.api_id = response['id']
            logger.info(f"Created API: {self.api_id}")
            return self.api_id
            
        except Exception as e:
            logger.error(f"Failed to create API: {e}")
            return None
    
    async def deploy_api(self, stage_name: str = "prod") -> Optional[str]:
        """Deploy the API to a stage"""
        try:
            if not self.client or not self.api_id:
                if not self.client:
                    self.initialize()
                if not self.api_id:
                    self.api_id = "mock-api-id"
            
            if not self.client:
                logger.info(f"Mock: Would deploy API to stage {stage_name}")
                return f"https://mock-api.execute-api.{self.aws_region}.amazonaws.com/{stage_name}"
            
            # First, get the root resource ID
            resources = await asyncio.to_thread(
                self.client.get_resources,
                restApiId=self.api_id
            )
            
            root_resource_id = None
            for resource in resources['items']:
                if resource['path'] == '/':
                    root_resource_id = resource['id']
                    break
            
            if not root_resource_id:
                raise ExternalServiceError("api_gateway", "Root resource not found")
            
            # Create deployment
            deployment = await asyncio.to_thread(
                self.client.create_deployment,
                restApiId=self.api_id,
                stageName=stage_name,
                variables={
                    'environment': 'production'
                }
            )
            
            deployment_id = deployment['id']
            logger.info(f"Deployed API to stage: {stage_name}")
            
            return f"https://{self.api_id}.execute-api.{self.aws_region}.amazonaws.com/{stage_name}"
            
        except Exception as e:
            logger.error(f"Failed to deploy API: {e}")
            return None
    
    async def create_resource(self, path: str, parent_id: str) -> Optional[str]:
        """Create a new resource in the API"""
        try:
            if not self.client or not self.api_id:
                if not self.client:
                    self.initialize()
                if not self.api_id:
                    self.api_id = "mock-api-id"
            
            if not self.client:
                logger.info(f"Mock: Would create resource {path}")
                return "mock-resource-id"
            
            response = await asyncio.to_thread(
                self.client.create_resource,
                restApiId=self.api_id,
                parentId=parent_id,
                pathPart=path.strip('/')
            )
            
            return response['id']
            
        except Exception as e:
            logger.error(f"Failed to create resource: {e}")
            return None
    
    async def put_method(self, resource_id: str, http_method: str, 
                        lambda_arn: Optional[str] = None) -> bool:
        """Create a method for a resource"""
        try:
            if not self.client or not self.api_id:
                if not self.client:
                    self.initialize()
                if not self.api_id:
                    self.api_id = "mock-api-id"
            
            if not self.client:
                logger.info(f"Mock: Would create method {http_method} for resource {resource_id}")
                return True
            
            method_kwargs: Dict[str, Any] = {
                'restApiId': self.api_id,
                'resourceId': resource_id,
                'httpMethod': http_method.upper(),
                'authorizationType': 'NONE'
            }
            
            if lambda_arn:
                method_kwargs['integration'] = {
                    'type': 'AWS_PROXY',
                    'integrationHttpMethod': 'POST',
                    'uri': f'arn:aws:apigateway:{self.aws_region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
                }
            
            await asyncio.to_thread(self.client.put_method, **method_kwargs)
            return True
            
        except Exception as e:
            logger.error(f"Failed to put method: {e}")
            return False
    
    def get_api_url(self, stage: str = "prod") -> str:
        """Get the API endpoint URL"""
        if not self.api_id:
            return ""
        return f"https://{self.api_id}.execute-api.{self.aws_region}.amazonaws.com/{stage}"


class LambdaIntegration:
    """AWS Lambda function management"""
    
    def __init__(self, aws_access_key_id: Optional[str] = None, 
                 aws_secret_access_key: Optional[str] = None,
                 aws_region: Optional[str] = None):
        self.aws_access_key_id: str = aws_access_key_id or settings.AWS_ACCESS_KEY_ID or ""
        self.aws_secret_access_key: str = aws_secret_access_key or settings.AWS_SECRET_ACCESS_KEY or ""
        self.aws_region: str = aws_region or settings.AWS_REGION or "ap-south-1"
        self.client: Optional[Any] = None
        
    def initialize(self) -> None:
        """Initialize Lambda client"""
        try:
            import boto3
            
            self.client = boto3.client(
                'lambda',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
        except ImportError:
            logger.warning("boto3 not installed. Using mock mode.")
            self.client = None
    
    async def invoke_function(self, function_name: str, payload: Dict[str, Any]) -> Optional[Dict]:
        """Invoke a Lambda function"""
        try:
            if not self.client:
                self.initialize()
            
            if not self.client:
                logger.info(f"Mock: Would invoke Lambda {function_name}")
                return {"statusCode": 200, "body": "mock response"}
            
            import json
            response = await asyncio.to_thread(
                self.client.invoke,
                FunctionName=function_name,
                Payload=json.dumps(payload),
                InvocationType='RequestResponse'
            )
            
            payload_stream = response['Payload']
            return json.load(payload_stream)
            
        except Exception as e:
            logger.error(f"Failed to invoke Lambda: {e}")
            return None


# Singleton instances
api_gateway_service = APIGatewayService()
lambda_integration = LambdaIntegration()


def get_api_gateway_service() -> APIGatewayService:
    """Get API Gateway service instance"""
    return api_gateway_service


def get_lambda_integration() -> LambdaIntegration:
    """Get Lambda integration instance"""
    return lambda_integration
