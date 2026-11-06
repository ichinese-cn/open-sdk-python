# ichinese-open-sdk (Python)

> **Prerelease 1.0.0-rc.3.** 这是预发布版，开放平台还没有正式开放，SDK 的默认地址可能连不上。This is a prerelease: the open platform is not open to the public yet, so the SDK's default address may not answer.

开放平台的 Python 服务端 SDK：开放接口（`/open-apis/v1`）的每个接口都是一个方法（由契约生成），另外帮你取应用令牌和机构令牌并在过期前续期、限流和服务端错误时退避重试、翻页、给出带类型的错误、在后端换网页免登码，以及事件推送的验签和解密。只用标准库，没有必需依赖。

The server SDK for the open platform's open API: every operation as a method (generated from the contract), plus token handling (app and tenant tokens, cached and renewed before they expire), retries with backoff after rate limits and server errors, paging, typed errors, the web login's code exchange, and verifying / decrypting event pushes. Standard library only; no required dependencies.

- Python 3.9+
- Synchronous and thread-safe: one `Client` per app, shared by every thread.
- Typed (`py.typed`); answers are plain `dict`s.

## Install

```sh
pip install ichinese-open-sdk
# decrypting encrypted event pushes needs the optional "cryptography" package:
pip install "ichinese-open-sdk[crypto]"
```

## Quick start

### List an institution's members (tenant token)

```python
import os
from ichinese_open import Client

client = Client(os.environ["APP_ID"], os.environ["APP_SECRET"])
tenant_key = "cn.…"  # from the app.installed event, or the developer console

tenant = client.get_tenant(tenant_key=tenant_key)
for m in client.iter_list_tenant_members(tenant_key=tenant_key):
    print(m["open_id"], m["name"])
```

Every method takes the path parameters by position, then `query` (a dict) and `body` (a dict) when the
operation has them, then keyword options that choose the token:

| option | token used |
|---|---|
| `access_token="…"` | that token, as is |
| `user_access_token="…"` | a user token (from `exchange_auth_code` / `refresh_user_token`) |
| `tenant_key="cn.…"` | the institution's tenant token (fetched, cached and renewed for you) |
| none | the app token, when the operation accepts one; otherwise `OpenApiError` with code `TOKEN_REQUIRED` |

`headers={...}` adds request headers. `client.request(method, path, query, body, ...)` calls any path the
generated methods do not cover.

### Web login (免登) on your backend

The page calls the JS SDK's `requestAuthCode()` and posts the code to your backend, which exchanges it
(the App Secret never goes to the page):

```python
user = client.exchange_auth_code(code)  # plain-browser fallback: also redirect_uri=…, code_verifier=…
me = client.get_user_info(user_access_token=user["access_token"])
assert me["open_id"] == user["open_id"]

# later
user = client.refresh_user_token(user["refresh_token"])
client.revoke_token(user["access_token"])  # on sign-out
```

A code works once: a second exchange fails with status 400 and `reason == "code_used"`
(`code_expired` / `code_invalid` similarly); ask the page for a new code. `exchange_auth_code` is never
retried.

### Event pushes and card callbacks

```python
from ichinese_open import OpenApiError, challenge_response, is_url_verification, parse_event

# raw_body: the request body bytes exactly as received; headers: any mapping (case-insensitive)
try:
    push = parse_event(headers, raw_body, SIGNING_SECRET, encrypt_key=ENCRYPT_KEY)
except OpenApiError:  # code INVALID_SIGNATURE (or INVALID_PAYLOAD)
    ...  # answer 401
if is_url_verification(push):
    answer = challenge_response(push)  # {"challenge": "…"} as JSON
else:
    ...  # answer 2xx within 5 seconds; dedupe by push["header"]["event_id"]
```

`verify_signature(headers, raw_body, secret, tolerance_seconds=300)`, `decrypt(encrypt, encrypt_key)`,
`sign(...)` and `parse_card_action(...)` are there too. The signature is
`v1=hex(HMAC-SHA256(secret, timestamp + "." + nonce + "." + body))`; encrypted bodies are AES-256-GCM
with the key `SHA-256(encrypt key)`.

### Posting in a person's name

With a user token that has the `community:post` scope, four methods do the uploads and the waiting:

| method | |
|---|---|
| `upload_image(user_token, data, content_type)` | gets an upload slot, PUTs the image there, returns its `key` |
| `upload_video(user_token, data, filename, content_type)` | gets a slot, PUTs the video (bytes, a path or a binary file, streamed), starts transcoding; returns the video (`asset_id`) |
| `wait_video_ready(user_token, asset_id, timeout=1800, interval=2)` | polls until the video is `ready`; raises `OpenApiError` with reason `video_failed`, or code `TIMEOUT` |
| `create_post(user_token, post)` | posts; adds a `uuid` when you give none, so retries never post twice |

```python
try:
    # A post with an image…
    with open("photo.jpg", "rb") as f:
        key = client.upload_image(user_token, f.read(), "image/jpeg")
    post = client.create_post(user_token, {"body": "今天学了新词 #HSK3", "images": [{"key": key}]})
    print(post["url"], post["status"])

    # …or with a video, once it is transcoded.
    video = client.upload_video(user_token, "lesson.mp4", "lesson.mp4", "video/mp4")
    client.wait_video_ready(user_token, video["asset_id"])
    client.create_post(user_token, {"title": "第一课", "video": {"asset_id": video["asset_id"]}})
except OpenApiError as e:
    if e.reason != "consent_required":
        raise
    print(e.consent_url)  # only the person can agree to show their name on posts, at this address
```

A post has either images (up to 9) or one video. Errors keep the server's `reason`: `consent_required`,
`video_not_ready`, `post_rate_limited`, `app_user_daily_limit`, `daily_quota_exceeded`,
`minor_not_allowed`, `app_post_stopped`, …. `create_post` and completing a video upload are retried after
server errors like a GET (the server makes them idempotent).

### Posting as the institution (机构号)

With the institution's tenant key the same helpers post as its community account (its name and logo, the
post says it came from your app): `upload_image_as_org`, `upload_video_as_org`, `wait_video_ready_as_org`,
`create_post_as_org`. The institution must have installed the app and granted `community:post`; before its
homepage was first published there is no account yet (409 `no_org_account`). Limits and review are the same.

```python
key = client.upload_image_as_org(tenant_key, data, "image/png")
client.create_post_as_org(tenant_key, {"body": "秋季班开始报名", "images": [{"key": key}]})
```

### The institution's dashboard

`get_all_insights` reads every page of the institution's dashboard the API offers (`GET /insights`, scope
`insights:readonly`, tenant token): the default page first, then each other tab it lists, with the same
query. It returns tab → page. Fewer than five people come back as null with `withheld: true`; money is
per currency, never converted.

```python
pages = client.get_all_insights(tenant_key, {"range": "30d"})
```

## The address

The default address is built into the release (`ichinese_open.DEFAULT_BASE_URL`). Override it for a
local or private deployment:

```python
client = Client(app_id, app_secret, base_url="http://open.localhost:4380")
```

One address serves every region: tokens carry their region and the gateway routes by it. A trailing
`/open-apis/v1` is accepted and stripped.

Other options: `max_retries=3`, `timeout=30.0` (seconds), `refresh_before_seconds=300`,
`user_agent="my-app/1.2"` (appended), and `transport=` to send requests through your own HTTP stack (see
`ichinese_open.types.Transport`).

## Errors

Every failure is an `OpenApiError`:

| attribute | |
|---|---|
| `status` | HTTP status (0: no answer — `NETWORK`, `TIMEOUT`, `TOKEN_REQUIRED`) |
| `code` | `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `VALIDATION_FAILED`, `RATE_LIMITED`, … (`HTTP_<status>` without a JSON error) |
| `reason` | `details.reason`: `scope_denied`, `token_expired`, `code_used`, … (`ichinese_open.ERROR_REASONS`) |
| `request_id` | quote it when asking for support |
| `details`, `retry_after`, `message` | |

A user or institution may refuse a scope. Degrade instead of failing:

```python
try:
    interests = client.get_user_interests(user_access_token=token)
except OpenApiError as e:
    if not e.is_scope_error:  # 403 with scope_denied / scope_pending / scope_not_declared / gold_only
        raise
    interests = None
    if e.reason == "scope_denied" and not e.never_ask:
        ...  # you may explain why the app wants e.scope and ask again later
```

Retries: 429 waits for `Retry-After` (then `X-RateLimit-Reset`, then backoff), except
`daily_quota_exceeded`; 500/502/503/504 and network errors are retried for GET/PUT/DELETE and the token
requests only; backoff is `min(30 s, 0.5 s · 2^attempt + jitter)`. A 401 `token_expired` / `invalid_token`
on a cached app or tenant token drops it, fetches a new one and tries once more.

## Paging

Every paged list has an `iter_…` generator that follows `has_more` / `page_token` (default
`page_size` 100):

```python
for c in client.iter_list_classes({"page_size": 50}, tenant_key=tenant_key):
    print(c["name"])

page = client.list_classes({"page_size": 20}, tenant_key=tenant_key)  # one page
page["items"], page["has_more"], page.get("page_token")
```

## Constants

`VERSION`, `DEFAULT_BASE_URL`, `SCOPES`, `EVENT_TYPES`, `ERROR_REASONS`, and `OPERATION_TOKENS` (the token
types each method accepts) come from the contract.

## Examples

- [`examples/tenant_members.py`](examples/tenant_members.py): tenant token, paged member list, scope fallback
- [`examples/web_login_backend.py`](examples/web_login_backend.py): the web login's backend (`http.server`)
- [`examples/events_server.py`](examples/events_server.py): receiving events (verify, decrypt, challenge)

## Development

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -t .
PYTHONPATH=src uv run --no-project --with cryptography python -m unittest discover -s tests -t .
uv build   # dist/*.whl and dist/*.tar.gz
```

`_operations.py` and `_meta.py` are generated from `docs/api/open-api.yaml` (`pnpm sdk:gen`); do not edit
them. The integration test runs when `ICH_OPEN_IT` holds the fixture JSON (or its file path).

## License

MIT, see [LICENSE](LICENSE).
