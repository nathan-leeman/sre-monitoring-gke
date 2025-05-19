import random
import time
from datetime import datetime
from flask import Flask, jsonify, send_from_directory
from prometheus_client import Counter, Histogram, generate_latest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__, static_folder='static')

# Initialize OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask
FlaskInstrumentor().instrument_app(app)

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

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/prices')
def get_prices():
    with tracer.start_as_current_span("get_prices") as span:
        REQUEST_COUNT.inc()
        start_time = time.time()
        
        # Simulate random latency
        time.sleep(random.uniform(0.1, 0.5))
        
        # Simulate random errors (5% chance)
        if random.random() < 0.05:
            ERROR_COUNT.inc()
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            return jsonify({'error': 'Internal server error'}), 500
        
        prices = [generate_price(symbol) for symbol in SYMBOLS]
        
        # Record latency
        REQUEST_LATENCY.observe(time.time() - start_time)
        
        return jsonify(prices)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 