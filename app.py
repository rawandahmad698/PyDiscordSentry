# Flask
from flask import Flask, request
from flask import Response

# Local
import sample_webhook as webhook
from Classes import SentryParser as Sn

# Built-in
import json
import gzip

app = Flask(__name__)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def all_paths(path):
    raw_trace = gzip.decompress(request.get_data()).decode('utf-8')
    if len(raw_trace) == 0:
        return Response("Listening..", status=200)
    try:
        raw_trace_json = json.loads(raw_trace)
        sentry_trace = Sn.sentry_trace_from_dict(raw_trace_json)
        if sentry_trace is None:
            webhook.error_handler("Cannot parse sentry trace", f"```{raw_trace}```")
            return Response("Failed to parse sentry trace", status=400)

        # I like webhooks, but you can use your own method of sending messages.
        webhook.prepare_webhook(sentry_trace)
    except Exception as e:
        webhook.error_handler("Cannot parse sentry trace", f"```{raw_trace}```")
        return Response("Failed to parse sentry trace", status=400)
    finally:
        return Response('{"status":"received"}', status=200, mimetype='application/json')


# Run app
if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=False)
