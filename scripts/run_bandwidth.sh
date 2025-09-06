ROOT="$(cd "$(dirname "$0")/.."; pwd)"
cd "$ROOT"

export PROFILE=bandwidth

locust -f locustfile.py \
  --host http://localhost:8080 \
  --headless \
  -u 20 \
  -r 5 \
  -t 5m \
  --csv results/bandwith_run