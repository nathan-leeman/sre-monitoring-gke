import random
import time
import json
import logging
import os
from datetime import datetime
from flask import Flask, jsonify, send_from_directory
from prometheus_client import Counter, Histogram, generate_latest
# OpenTelemetry imports (commented for future use)
# from opentelemetry import trace
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# from opentelemetry.instrumentation.flask import FlaskInstrumentor
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import MetricServiceClient

app = Flask(__name__, static_folder='static')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_structured(message, **kwargs):
    """Helper function for structured logging"""
    log_entry = {
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    logger.info(json.dumps(log_entry))

# Initialize Google Cloud Monitoring
try:
    client = monitoring_v3.MetricServiceClient()
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'default-project')
    project_name = f"projects/{project_id}"
except Exception as e:
    log_structured("Failed to initialize Google Cloud Monitoring", error=str(e))
    client = None

# OpenTelemetry initialization (commented for future use)
# trace.set_tracer_provider(TracerProvider())
# tracer = trace.get_tracer(__name__)
# otlp_exporter = OTLPSpanExporter()
# span_processor = BatchSpanProcessor(otlp_exporter)
# trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask (commented for future use)
# FlaskInstrumentor().instrument_app(app)

# Prometheus metrics
REQUEST_COUNT = Counter('market_data_requests_total', 'Total number of requests')
REQUEST_LATENCY = Histogram('market_data_request_latency_seconds', 'Request latency in seconds')
ERROR_COUNT = Counter('market_data_errors_total', 'Total number of errors')

SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

def generate_price(symbol):
    base_price = {
        'AAPL': 180.0,
        'MSFT': 380.0,
        'GOOGL': 140.0,
        'AMZN': 170.0,
        'TSLA': 180.0
    }
    price = base_price[symbol] * (1 + random.uniform(-0.02, 0.02))
    spread = price * random.uniform(0.0001, 0.0005)
    return {
        'symbol': symbol,
        'price': round(price, 2),
        'bid': round(price - spread/2, 2),
        'ask': round(price + spread/2, 2),
        'timestamp': datetime.utcnow().isoformat()
    }

def write_custom_metric(metric_name, value, labels=None):
    """Write a custom metric to Google Cloud Monitoring"""
    if not client:
        return

    try:
        series = monitoring_v3.TimeSeries()
        series.metric.type = f'custom.googleapis.com/{metric_name}'
        series.resource.type = 'global'
        series.resource.labels['project_id'] = project_id

        if labels:
            series.metric.labels.update(labels)

        point = monitoring_v3.Point()
        point.value.double_value = value
        now = time.time()
        point.interval.end_time.seconds = int(now)
        series.points = [point]

        client.create_time_series(name=project_name, time_series=[series])
    except Exception as e:
        log_structured("Failed to write custom metric", 
                      metric_name=metric_name, 
                      error=str(e))

@app.route('/')
def index():
    log_structured("Serving index page")
    return send_from_directory('static', 'index.html')

@app.route('/prices')
def get_prices():
    # OpenTelemetry tracing (commented for future use)
    # with tracer.start_as_current_span("get_prices") as span:
    REQUEST_COUNT.inc()
    start_time = time.time()
    
    # Simulate random latency
    time.sleep(random.uniform(0.1, 0.5))
    
    # Simulate random errors (5% chance)
    if random.random() < 0.05:
        ERROR_COUNT.inc()
        # OpenTelemetry error status (commented for future use)
        # span.set_status(trace.Status(trace.StatusCode.ERROR))
        log_structured("Error occurred in get_prices", 
                     error="Internal server error",
                     status_code=500)
        return jsonify({'error': 'Internal server error'}), 500
    
    prices = [generate_price(symbol) for symbol in SYMBOLS]
    
    # Record latency
    latency = time.time() - start_time
    REQUEST_LATENCY.observe(latency)
    
    # Write custom metrics
    write_custom_metric('market_data/latency', latency)
    write_custom_metric('market_data/price_count', len(prices))
    
    log_structured("Successfully retrieved prices", 
                  price_count=len(prices),
                  latency=latency)
    
    return jsonify(prices)

@app.route('/health')
def health_check():
    log_structured("Health check requested")
    return jsonify({'status': 'healthy'}), 200

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    log_structured("Starting market data service")
    app.run(host='0.0.0.0', port=5000) 