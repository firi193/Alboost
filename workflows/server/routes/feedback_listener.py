"""
AWS Lambda handler for processing user feedback.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle incoming feedback requests.
    
    Args:
        event (Dict): Lambda event data
        context (Any): Lambda context
        
    Returns:
        Dict: Response object
    """
    try:
        logger.info(f"Received feedback event: {json.dumps(event)}")
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Validate required fields
        required_fields = ['feedback_type', 'campaign_id']
        missing_fields = [field for field in required_fields if field not in body]
        
        if missing_fields:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f"Missing required fields: {', '.join(missing_fields)}"
                })
            }
            
        feedback_type = body['feedback_type']
        campaign_id = body['campaign_id']
        
        # Validate feedback type
        if feedback_type not in ['positive', 'negative']:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': "Invalid feedback type. Must be 'positive' or 'negative'"
                })
            }
            
        # Initialize workflow and get feedback agent
        from workflows.agent_orchestration import ContentMarketingWorkflow
        workflow = ContentMarketingWorkflow()
        feedback_agent = workflow.agents['feedback']
        
        # Process feedback
        feedback_data = {
            'type': feedback_type,
            'campaign_id': campaign_id,
            'timestamp': datetime.now().isoformat()
        }
        
        feedback_agent.receive_message('user', {
            'type': 'feedback',
            'content': feedback_data
        })
        
        logger.info(f"Feedback processed: {feedback_type} for campaign {campaign_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': 'Feedback processed successfully'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"Internal server error: {str(e)}"
            })
        }