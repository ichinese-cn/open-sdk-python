"""Lists the members of an institution that installed your app (tenant token, paged).

    APP_ID=… APP_SECRET=… TENANT_KEY=cn.… [OPEN_API_BASE=http://open.localhost:4380] python examples/tenant_members.py
"""
import os

from ichinese_open import Client, OpenApiError

client = Client(
    os.environ["APP_ID"],
    os.environ["APP_SECRET"],
    base_url=os.environ.get("OPEN_API_BASE"),  # default: the release's address
)
tenant_key = os.environ["TENANT_KEY"]

try:
    tenant = client.get_tenant(tenant_key=tenant_key)
    print(f"{tenant.get('name')} ({tenant.get('rating')})")
    for m in client.iter_list_tenant_members(tenant_key=tenant_key):
        print(f"{m['open_id']}  {m.get('name')}  {','.join(m.get('roles') or [])}")
except OpenApiError as e:
    # The institution's admin may have refused this scope: do without the member list.
    if e.is_scope_error:
        print(f"not allowed ({e.reason} {e.scope or ''})")
    else:
        raise
