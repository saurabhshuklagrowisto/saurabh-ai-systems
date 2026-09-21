# An MCP server for email infrastructure provisioning

Standing up cold email infrastructure means buying domains, creating mailboxes, pointing DNS, setting up forwarding, pulling credentials, rotating two factor codes and managing subscriptions. The vendor exposes all of it over a REST API. Doing it by hand means a browser, a dashboard and an afternoon.

This is an MCP server that puts the whole API in front of an agent, so provisioning becomes something you ask for in a sentence. 18 tools over stdio.

The vendor is not named here and neither is the base URL. The pattern is the point, and it transfers to any REST API you want an agent to drive.

## What it covers

| Area | Tools |
|---|---|
| Orders | bulk create, single create, list active, list pending, reupload |
| Domains | update forwarding, read DNS records, add, update and delete DNS records |
| Users | update username, generate credentials CSV, fetch TOTP codes |
| Subscriptions | cancel, verify a cancellation revert, revert |
| Payments | charge card |
| Health | unauthenticated availability check |

## The design decisions

**Every write tool takes a `dryRun` flag.** It sets an `x-dry-run: true` header, and the vendor runs validation without touching anything downstream: no records written, no cards charged. An agent holding a create-order and a charge-card tool is exactly the situation where you want a rehearsal mode, and the cost of wiring it was one optional zod field reused across every tool.

```js
const dryRunField = z
  .boolean()
  .optional()
  .describe("Simulate the request without making real changes (sets x-dry-run header).");
```

**One transport function, eighteen thin tools.** All HTTP goes through a single helper that assembles the URL, attaches the API key, sets the dry-run header when asked, and normalises the response. Each tool is then a schema and a one-line call. Auth, error shape and dry-run behaviour are defined once, so a tool cannot get any of them wrong.

```js
async function callVendorApi(method, path, { body, query, dryRun } = {}) {
  const url = new URL(BASE_URL + path);
  if (query) for (const [k, v] of Object.entries(query))
    if (v !== undefined && v !== null) url.searchParams.set(k, v);

  const headers = { "Content-Type": "application/json" };
  if (API_KEY) headers["x-api-key"] = API_KEY;
  if (dryRun) headers["x-dry-run"] = "true";

  const res = await fetch(url, { method, headers,
    body: body !== undefined ? JSON.stringify(body) : undefined });

  const contentType = res.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await res.json() : await res.text();

  return { status: res.status, data };
}
```

**The HTTP status is returned to the model, not swallowed.** Results come back as `HTTP 422` followed by the body, with `isError` set on anything at 400 or above. An agent that gets "something went wrong" retries blindly. An agent that gets the status and the validation body fixes the payload and moves on.

**Tool descriptions name the endpoint and the scope.** Each one reads like `GET /domains/:domain/dns-records: retrieves custom DNS records for a domain. Requires domains:read.` The model picks the right tool from the description alone, and when a call fails on permissions the reason is already in front of it.

**The key comes from the environment.** `API_KEY` is read once from an environment variable at startup and never appears in a tool argument, so it cannot end up in a transcript or a log line.

## Stack

Node, `@modelcontextprotocol/sdk` with `McpServer` and `StdioServerTransport`, zod for the input schemas, native `fetch`. No other dependencies.

## Where this transfers

Any vendor API you find yourself clicking through a dashboard for. The parts worth copying: one transport function so auth and errors are defined in a single place, a dry-run flag on every write, real HTTP statuses returned to the model, and tool descriptions that name the endpoint and the permission it needs.
