ROOT="$(cd "$(dirname "$0")/.."; pwd)"
cd "$ROOT"

export PROFILE=throughput

locust -f locustfile.py \
  --host http://localhost:8080 \
  -u 200 \
  -r 20 \
  -t 5m \
  --csv results/throughput_run 