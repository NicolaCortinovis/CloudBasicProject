ROOT="$(cd "$(dirname "$0")/.."; pwd)"
cd "$ROOT"

export PROFILE=easy

locust -f locustfile.py \
  --host http://localhost:8080 \
  -u 100 \
  -r 10 \
  -t 5m \
  --csv results/easy_run