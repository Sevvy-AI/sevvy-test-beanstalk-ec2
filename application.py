import logging
import sys
import traceback
from datetime import datetime
from flask import Flask, request, jsonify
import os
import sentry_sdk

sentry_sdk.init(
    dsn="https://43c7014b19f5ba6dd3e80ed8c270e489@o4509641833775104.ingest.us.sentry.io/4509647590391808",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profile_session_sample_rate to 1.0 to profile 100%
    # of profile sessions.
    profile_session_sample_rate=1.0,
    # Set profile_lifecycle to "trace" to automatically
    # run the profiler on when there is an active transaction
    profile_lifecycle="trace",
)

# Configure logging for CloudWatch
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create Flask application
application = Flask(__name__)

@application.before_request
def log_request_info():
    """Log incoming requests for monitoring"""
    logger.info(f"Request: {request.method} {request.url} - IP: {request.remote_addr}")

@application.after_request
def log_response_info(response):
    """Log outgoing responses for monitoring"""
    logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
    return response

@application.route('/', methods=['GET'])
@application.route('/index', methods=['GET'])
def index():
    """Root endpoint that returns the service status."""
    return jsonify({
        'service': 'sevvy-test-server',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Sevvy Test Server is running'
    }), 200

@application.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint to test deployments"""
    return jsonify({'message': 'pong', 'timestamp': datetime.utcnow().isoformat()}), 200

@application.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancers"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'sevvy-test-server'
    }), 200

@application.route('/error/null-pointer', methods=['POST'])
def null_pointer_error():
    """Simulate null pointer exception"""
    try:
        logger.info("Triggering null pointer error for testing")
        none_object = None
        # This will raise AttributeError
        result = none_object.some_attribute
        return jsonify({'result': result})
    except Exception as e:
        logger.error(f"NULL_POINTER_ERROR: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return jsonify({
            'error': 'null_pointer',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@application.route('/error/server-error', methods=['POST'])
def generic_server_error():
    """Generic 500 server error"""
    logger.error("GENERIC_SERVER_ERROR: Simulated internal server error")
    return jsonify({
        'error': 'internal_server_error',
        'message': 'Something went wrong on the server',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

@application.route('/error/division-zero', methods=['POST'])
def division_by_zero_error():
    """Division by zero error with detailed logging"""
    try:
        logger.info("Attempting division calculation for testing")
        numerator = 100  # Default value
        
        # Try to get numerator from JSON if available, but don't fail if no JSON
        try:
            if request.is_json and request.get_json(silent=True):
                numerator = request.get_json().get('numerator', 100)
        except:
            pass  # Use default if JSON parsing fails
            
        denominator = 0  # Always zero to trigger error
        
        logger.info(f"Calculation: {numerator} / {denominator}")
        result = numerator / denominator
        
        return jsonify({'result': result})
    except ZeroDivisionError as e:
        logger.error(f"DIVISION_BY_ZERO_ERROR: {str(e)}")
        logger.error(f"Numerator: {numerator}, Denominator: {denominator}")
        logger.error("Extra log line")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return jsonify({
            'error': 'division_by_zero',
            'message': 'Division by zero is not allowed',
            'details': {
                'numerator': numerator,
                'denominator': denominator
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 400

@application.route('/error/custom/<error_type>', methods=['POST'])
def custom_error(error_type):
    """Configurable error endpoint"""
    error_configs = {
        'timeout': {'code': 408, 'message': 'Request timeout'},
        'forbidden': {'code': 403, 'message': 'Access forbidden'},
        'not_found': {'code': 404, 'message': 'Resource not found'},
        'bad_request': {'code': 400, 'message': 'Bad request format'},
        'unauthorized': {'code': 401, 'message': 'Unauthorized access'}
    }
    
    if error_type not in error_configs:
        logger.warning(f"Unknown error type requested: {error_type}")
        return jsonify({
            'error': 'unknown_error_type',
            'message': f'Error type "{error_type}" not supported',
            'supported_types': list(error_configs.keys()),
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    config = error_configs[error_type]
    logger.error(f"CUSTOM_ERROR_{error_type.upper()}: {config['message']}")
    
    return jsonify({
        'error': error_type,
        'message': config['message'],
        'timestamp': datetime.utcnow().isoformat()
    }), config['code']

@application.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify deployments"""
    return jsonify({
        'message': 'Test endpoint working!',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    }), 200

@application.route('/status', methods=['GET'])
def status():
    """Detailed status endpoint"""
    return jsonify({
        'service': 'sevvy-test-server',
        'version': '2.0.0',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.environ.get('FLASK_ENV', 'production'),
        'available_endpoints': [
            'GET /',
            'GET /health',
            'GET /status',
            'GET /test',
            'POST /error/null-pointer',
            'POST /error/server-error',
            'POST /error/division-zero',
            'POST /error/custom/<error_type>'
        ]
    }), 200

@application.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404_ERROR: {request.url} not found")
    return jsonify({
        'error': 'not_found',
        'message': 'Endpoint not found',
        'timestamp': datetime.utcnow().isoformat()
    }), 404

@application.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500_ERROR: Internal server error - {str(error)}")
    return jsonify({
        'error': 'internal_server_error',
        'message': 'Internal server error occurred',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8000))
    application.run(debug=True, host='0.0.0.0', port=port)

# Log registered routes when application starts
logger.info("Registered routes:")
for rule in application.url_map.iter_rules():
    logger.info(f"Route: {rule.rule} -> {rule.endpoint}")
