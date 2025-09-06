import os, random, time
from locust import HttpUser, task, between
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

# -------- Profiles --------
PROFILE = os.getenv("PROFILE", "easy").lower()

PROFILE_DEFAULTS = {
    # relatively long wait time, small files.
    "easy": {
        "WAIT_MIN": 3.0,  "WAIT_MAX": 6.0,  "UPLOAD_MB": 1.0, "USER_START" : 0, "USER_END" : 99,
    },
    #  quick ops, small files -> high RPS
    "throughput": {
        "WAIT_MIN": 1,  "WAIT_MAX": 1.5,  "UPLOAD_MB": 1.0, "USER_START" : 0, "USER_END" : 99,
    },
    # larger files -> bandwidth/disk stress
    "bandwidth": {
        "WAIT_MIN": 3.0,  "WAIT_MAX": 6.0,  "UPLOAD_MB": 500.0, "USER_START" : 0, "USER_END" : 99,
    }
}

def _getf(name, default): return float(os.getenv(name, default))
def _geti(name, default): return int(os.getenv(name, default))

p = PROFILE_DEFAULTS.get(PROFILE, PROFILE_DEFAULTS["easy"])
WAIT_MIN  = _getf("WAIT_MIN",  p["WAIT_MIN"])
WAIT_MAX  = _getf("WAIT_MAX",  p["WAIT_MAX"])
UPLOAD_MB = _getf("UPLOAD_MB", p["UPLOAD_MB"])
START     = _geti("USER_START", p["USER_START"])  # inclusive
END       = _geti("USER_END",   p["USER_END"])    # inclusive (e.g., 0..29)
PASSWORD  = os.getenv("OC_PASS", "supersecretpassword!123")
RETRY_STATUSES = {423, 429}

def payload_mb(mb: float) -> bytes:  # generate random binary payload of size mb
    return os.urandom(int(mb * 1024 * 1024))

class NextcloudUser(HttpUser):
    wait_time = between(WAIT_MIN, WAIT_MAX)

    # Each Locust virtual user (VU) picks a random Nextcloud account from the pool. 
    # Multiple VUs may share the same account, which simulates a more active account.
    def on_start(self):
        # pick random test account
        self.user_name = f"locust_user{random.randint(START, END)}"
        self.auth = HTTPBasicAuth(self.user_name, PASSWORD)
        self.base = f"/remote.php/dav/files/{self.user_name}"

    # It can be the case that we have error 423 Locked when the file has not been released yet because it is still in use
    # and we try to access it  to do some other operation or error 429 Too Many Requests due to NextCloud 
    # limiting requests for safety. Those are error that disappear if we just wait a bit, and this does just that by
    # retrying up to 5 times. It also handles 404s which can happen during delete or download when no file is present. We
    # do not want to track that as a failure since it just means that our VUs have not yet uploaded a file.
    def _req_with_retry(self, method, path, name, **kw):
        # No delays, up to 5 quick retries for 423/429
        for _ in range(5):  # no backoff, your current style
            with self.client.request(method, path, auth=self.auth, name=name,
                                     catch_response=True, **kw) as resp:
                if resp.status_code in (423, 429):
                    continue  # retry
                if resp.status_code == 404 and method in ("GET", "DELETE"):
                    resp.success()  # nothing to act on is fine
                return resp
        return resp  # last attempt result

    # -------- Tasks --------

    # File Metadata access task
    @task(2)
    def list_root(self):
        self.client.request(
            "PROPFIND", f"{self.base}/",
            headers={"Depth": "1"}, auth=self.auth,
            name="PROPFIND /files/[user]/"
        )

    # Upload task so Disk write I/O
    @task(6)
    def upload_file(self):
        name = f"locust_{random.randint(0,1_000_000)}_{UPLOAD_MB}mb.bin"
        path = f"{self.base}/{name}"
        self._req_with_retry("PUT", path, f"PUT /files/[user]/{UPLOAD_MB}MB", data=payload_mb(UPLOAD_MB))

    # Download task so Disk read I/O
    @task(4)
    def download_file(self):
        # Try a likely filename; 404 is treated as OK by _req_with_retry
        name = f"locust_{random.randint(0,1_000_000)}_{UPLOAD_MB}mb.bin"
        self._req_with_retry("GET", f"{self.base}/{name}", f"GET /files/[user]/{UPLOAD_MB}MB")

    # Delete task so metadata update
    @task(3)
    def delete_file(self):
        # Try a likely filename; 404 is treated as OK by _req_with_retry
        name = f"locust_{random.randint(0,1_000_000)}_{UPLOAD_MB}mb.bin"
        self._req_with_retry("DELETE", f"{self.base}/{name}", f"DELETE /files/[user]/{UPLOAD_MB}MB")
