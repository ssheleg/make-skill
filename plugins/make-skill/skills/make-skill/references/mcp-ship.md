# Shipping an MCP server — mount, debug, publish

**Load this when:** the server is written and now has to reach someone —
mounting it inside an existing web app, fixing a client that cannot connect, or
publishing it to the official MCP Registry.

`references/mcp.md` is the author's model of the protocol: primitives,
lifecycle, transports, security. This file starts where that one stops. If you
are still designing tools and their schemas, Anthropic's `mcp-builder` skill
covers authoring and evaluation in depth and this file deliberately does not
repeat it — **it has nothing on the registry, on mounting, or on why a client
sees 404, which is exactly what is here.**

Registry schema URL and CLI flags move. Read them from
<https://modelcontextprotocol.io/registry/> and the
[registry repo](https://github.com/modelcontextprotocol/registry) rather than
from a copy — the pinned example below was current on **2026-08-06** and the
schema is dated by design.

## Contents

- [Mounting into an existing web app](#mounting-into-an-existing-web-app)
- [Auth middleware and a health endpoint](#auth-middleware-and-a-health-endpoint)
- [Client configuration](#client-configuration)
- [Debugging a client that will not connect](#debugging-a-client-that-will-not-connect)
- [Publishing to the MCP Registry](#publishing-to-the-mcp-registry)
- [Registry name formats and who may claim them](#registry-name-formats-and-who-may-claim-them)
- [Automating publication](#automating-publication)
- [Versioning](#versioning)

---

## Mounting into an existing web app

The common production shape: you already run a FastAPI/Starlette app, and the
MCP server should live at `/mcp` on the same host. It is also where the single
most common bug lives.

**The double-path pitfall.** FastMCP defaults its internal
`streamable_http_path` to `/mcp/`. Mount that app at `/mcp` and the real
endpoint becomes `/mcp/mcp` — so every client pointed at `/mcp` gets 404, and
the SSE fallback 404s too, which reads like the server is down.

```python
mcp = FastMCP(
    "my_server",
    streamable_http_path="/",   # REQUIRED when mounting as a sub-app
    stateless_http=True,
    json_response=True,
)

app.mount("/mcp", mcp.streamable_http_app())
```

Set `streamable_http_path="/"` whenever the app is mounted rather than served
standalone. Standalone servers keep the default.

---

## Auth middleware and a health endpoint

Wrap the mounted ASGI app rather than adding auth inside tool handlers — the
transport handshake happens before any tool runs, so handler-level auth leaves
the protocol surface open.

```python
class MCPAuthMiddleware:
    _PUBLIC_PATHS = {"/health"}

    def __init__(self, app, *, store):
        self._app, self._store = app, store

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            return await self._app(scope, receive, send)
        if scope.get("path", "") in self._PUBLIC_PATHS:
            return await self._app(scope, receive, send)

        headers = dict(scope.get("headers", []))
        auth = headers.get(b"authorization", b"").decode()
        if not auth.startswith("Bearer "):
            return await self._send_401(send, "Missing Bearer token")
        if not await self._store.validate_api_key(auth[7:]):
            return await self._send_401(send, "Invalid API key")
        return await self._app(scope, receive, send)

app.mount("/mcp", MCPAuthMiddleware(mcp.streamable_http_app(), store=key_store))
```

Keep a health endpoint **outside** the mount and exempt from auth. It is what
tells you "the app is up, the MCP path is wrong" apart from "the app is down" —
the two produce identical client errors.

```python
@app.get("/mcp/health")
async def mcp_health():
    return {"status": "ok", "server": "my_server", "transport": "streamable-http"}
```

---

## Client configuration

Remote (streamable HTTP):

```json
{
  "mcpServers": {
    "my-server": {
      "url": "https://example.com/mcp",
      "headers": { "Authorization": "Bearer ${MY_SERVER_KEY}" }
    }
  }
}
```

Local (stdio):

```json
{
  "mcpServers": {
    "my-server": {
      "command": "uv",
      "args": ["--directory", "/path/to/project", "run", "python", "-m", "my_server"],
      "env": { "API_KEY": "..." }
    }
  }
}
```

Ship both forms in your README. A user who has to derive the config from prose
files an issue instead.

---

## Debugging a client that will not connect

**404 — by far the most common.** Symptom: `Error POSTing to endpoint: Not
Found`, then the SSE fallback 404s as well. Bisect the path directly:

```bash
curl -X POST https://your-host/mcp/     -H 'Content-Type: application/json' -d '{}'
curl -X POST https://your-host/mcp      -H 'Content-Type: application/json' -d '{}'
curl -X POST https://your-host/mcp/mcp  -H 'Content-Type: application/json' -d '{}'
```

If `/mcp/mcp` answers (even 401) while `/mcp/` 404s, it is the double path.
A 401 is a **success** for this test: it proves routing reached the server.

**307.** Starlette redirects `/mcp` → `/mcp/`. Most clients follow it on POST;
some do not, and the failure looks like a hang. Either document the trailing
slash or add an explicit no-slash route.

**401.** Check the Bearer prefix and the key, then check that the client is
actually sending headers — several clients drop custom headers on the SSE
fallback specifically, so the initial POST authenticates and the stream does not.

---

## Publishing to the MCP Registry

The registry stores **metadata pointing at your server**, not the server. You
publish a `server.json`.

Remote server:

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "com.example/my-mcp",
  "title": "My MCP Server",
  "description": "What it does (max 100 chars).",
  "version": "1.0.0",
  "remotes": [
    {
      "type": "streamable-http",
      "url": "https://example.com/mcp",
      "headers": [
        { "name": "Authorization", "description": "Bearer API key",
          "isRequired": true, "isSecret": true }
      ]
    }
  ]
}
```

Local package (npm shown; `pypi` takes the same shape with `registryType`
changed):

```json
{
  "packages": [
    {
      "registryType": "npm",
      "identifier": "@username/my-mcp-server",
      "version": "1.0.0",
      "transport": { "type": "stdio" }
    }
  ]
}
```

PyPI additionally requires `<!-- mcp-name: your-server-name -->` in the package
README, as proof the package and the registry entry belong to the same author.

Validate before you publish — `description` is capped at **100 characters** and
a version may be published only once:

```bash
mcp-publisher validate
mcp-publisher publish
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=my-mcp"
```

---

## Registry name formats and who may claim them

The name is not free-form: it encodes how you proved ownership.

| Auth method | Name format | Example |
|---|---|---|
| GitHub | `io.github.<user>/*` | `io.github.alice/weather` |
| DNS | reverse-DNS of the domain | `com.example/my-server` |
| HTTP | reverse-DNS of the domain | `com.example/my-server` |

**GitHub** is the shortest path — `mcp-publisher login github`, OAuth device
flow, done. The name must start with your username.

**DNS** and **HTTP** claim a domain with an Ed25519 key. DNS puts the public key
in a TXT record; HTTP serves it at
`https://<domain>/.well-known/mcp-registry-auth`. Use HTTP when you control the
web root but not the zone.

```bash
openssl genpkey -algorithm Ed25519 -out mcp-registry-key.pem
PUBLIC_KEY="$(openssl pkey -in mcp-registry-key.pem -pubout -outform DER | tail -c 32 | base64)"
# DNS:  <domain>. IN TXT "v=MCPv1; k=ed25519; p=${PUBLIC_KEY}"
# HTTP: echo "v=MCPv1; k=ed25519; p=${PUBLIC_KEY}" > mcp-registry-auth
```

Treat `mcp-registry-key.pem` as a publishing credential: it is the thing that
lets someone replace your server entry. It belongs in a secret store, not the
repository, and the CI job that uses it should be the only consumer.

---

## Automating publication

Same shape as the skill releases in `references/distribution.md`: a `v*` tag
triggers validate → publish. Two rules carry over unchanged.

- **Gate the publish on the validator**, in the same job. A registry entry
  pointing at a broken build is worse than no entry, because clients cache it.
- **Fail on a version already published** rather than skipping quietly. A silent
  skip is how a tag ends up green while the registry still serves the previous
  version.

Install the CLI in CI from the released binary:

```bash
curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher
```

---

## Versioning

The registry version is the **server's** version, and it is what clients compare
against. Keep it equal to the package version — an npm package at 1.2.0 whose
registry entry says 1.0.0 makes every bug report unactionable.

The `$schema` date and your version are unrelated: the schema is the registry's
contract and moves on the registry's schedule, so re-read it before each publish
rather than carrying the pinned URL forward on faith.
