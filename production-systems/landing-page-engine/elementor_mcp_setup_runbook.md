# Elementor MCP Setup Runbook — Live Site

**Goal:** Connect Claude Code to WordPress/Elementor via MCP so it can build pages programmatically. Tested and confirmed working on staging on July 7, 2026.

This is the infrastructure that lets the [Landing Page & Collateral Engine](./README.md) publish directly into WordPress/Elementor instead of hand-copying layouts.

---

## ⚠️ Before You Start (Live Site Safety)

- Take a full site + database backup before touching anything on live (Hostinger hPanel usually has a one-click backup/snapshot option).
- Do this during low-traffic hours if possible.
- Have this checklist open on a separate screen/device so you're not toggling tabs mid-process.

## Step 1: Check WordPress Core Version

- Go to **Dashboard → Updates** (or **Tools → Site Health → Info**).
- Confirm WordPress is **6.8 or higher**. If not, update WordPress core first (this plugin requires 6.8+).
- After updating, do a quick sanity check: confirm Elementor, Elementor Pro, and other active plugins still show no compatibility errors on the Plugins page.

## Step 2: Check Elementor Version

- Go to **Plugins → Installed Plugins**. Confirm:
  - **Elementor (free): 3.20 or higher** (required for container support)
  - **Elementor Pro:** note the version (informational)
- ⚠️ Do **NOT** update Elementor to a new major version during this process unless already validated — check the compatibility banner on the Plugins page first (it flags addon compatibility issues).

## Step 3: Install WordPress MCP Adapter Plugin

- Go to: `github.com/WordPress/mcp-adapter/releases`
- Find the latest release (not "Download ZIP" from the Code button — use the **Assets** section).
- Download the packaged plugin asset (e.g. `mcp-adapter.zip`) — **NOT** "Source code (zip)".
- **WP Admin → Plugins → Add New → Upload Plugin** → upload the zip → **Install Now → Activate**.
- Confirm it appears in your Plugins list as "MCP Adapter".

## Step 4: Install Elementor MCP Plugin (EMCP Tools)

- Go to: `github.com/msrbuilds/elementor-mcp/releases`
- Find the latest release at the top of the list.
- Under **Assets**, download the free build (e.g. `emcp-tools-X.X.X.zip`) — **NOT** "Source code (zip)".
- **WP Admin → Plugins → Add New → Upload Plugin** → upload the zip → **Install Now → Activate**.
- Confirm a new **EMCP Tools** menu appears in the WP sidebar.

## Step 5: ⭐ Enable Elementor "Container" Experiment (CRITICAL — this was the actual fix)

This is the step that fixed the "success but nothing saves" bug on staging.

- Go to **Elementor → Settings → Experiments** (or `/wp-admin/admin.php?page=elementor-settings#tab-experiments`).
- Scroll to **Stable Features**.
- Find **Container** and set it to **Active** (if not already).
- Click **Save Changes** at the bottom of the page.

> Without this, `add-container` calls return a fake "success" response but never actually write to `_elementor_data` — pages stay empty.

## Step 6: Trim EMCP Tools Permissions (Optional but Recommended)

- Go to **EMCP Tools → Tools**.
- Review the **WordPress** tab (broader than Elementor) — disable anything not needed for page building:
  - Plugin/theme install-update-delete
  - User management
  - Site-wide settings changes
- Consider disabling the **Gutenberg** tab entirely if only using Elementor.
- Click **Save Changes**.

## Step 7: Create a Scoped Test/Service User

- **Users → Add New**
- Username: e.g. `claude-mcp-service` (pick something clear, not tied to a person).
- Role: **Editor** (do **NOT** use Administrator for day-to-day use).
- Create the user.

## Step 8: Generate an Application Password

- Go to that user's profile: **Users → [username] → Edit**.
- Scroll to **Application Passwords**.
- Enter a name (e.g. "Elementor MCP — Claude Code").
- Click **Add New Application Password**.
- Copy the password immediately — it's shown once only.

> **Do not paste this password into any chat conversation.** Store it in a password manager or a local note.

## Step 9: Confirm the Endpoint Responds (curl test)

Run this locally in a terminal — replace the placeholders with your real values:

```bash
curl -s -i -u "claude-mcp-service:YOUR_APP_PASSWORD" \
  https://YOUR-LIVE-SITE.com/wp-json/mcp/emcp-tools-server \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

Expect an HTTP 200 with a JSON response containing `serverInfo`. If you get a 401, double-check the username/password and that the Application Password wasn't mistyped.

## Step 10: Connect Claude Code

Base64-encode the credentials locally:

```bash
echo -n "claude-mcp-service:YOUR_APP_PASSWORD" | base64
```

Create a project folder (e.g. `~/projects/growisto-live-pages`). Inside it, create `.mcp.json`:

```json
{
    "mcpServers": {
        "elementor-mcp": {
            "type": "http",
            "url": "https://YOUR-LIVE-SITE.com/wp-json/mcp/emcp-tools-server",
            "headers": {
                "Authorization": "Basic YOUR_BASE64_STRING"
            }
        }
    }
}
```

Open Claude Code in that folder, run `/mcp` — confirm `elementor-mcp` shows as connected with tools listed.

## Step 11: Confirm Figma MCP Is Connected (if using Figma-to-page workflow)

- Run `/mcp` in Claude Code and confirm `figma` is also listed as connected.
- If not, connect via: `claude mcp add --transport http figma "https://mcp.figma.com/mcp"`

## Step 12: Pilot Test — Build One Page End-to-End

- Open the target Figma frame/design, select it.
- In Claude Code, prompt something like:

> "Read the currently selected Figma frame using the Figma MCP tools. Then use the elementor-mcp tools to build this as a new WordPress page called '[Page Name] - Test'. First call list-widgets and get-global-settings so you match the site's brand. Summarize the Figma structure before building. Build section by section and confirm when done with a link to the page."

- After it reports done, open the page in the real Elementor editor and visually confirm content actually rendered (don't just trust the "success" message).
- If it worked — repeat for the next real page.

## Post-Setup Cleanup Checklist

- Confirm no test/dummy pages are left published or indexed.
- Consider rotating the Application Password once initial testing is done, and store the final one securely.
- Document which user account (`claude-mcp-service`) has this access, for future audit/offboarding.
- If anything was pasted into a chat session during setup, rotate that credential too.

## Known Gotchas (from staging test)

| Symptom | Cause | Fix |
|---|---|---|
| `add-container` returns success but page stays empty in Elementor editor | Container experiment not enabled | Elementor → Settings → Experiments → Container → Active |
| HTTP 401 on connection | Base64 encoding issue or wrong app password | Re-verify with `base64 --decode` round-trip test |
| "Missing Mcp-Session-Id header" | Direct HTTP transport session handling issue | Use the plugin's bundled Node.js proxy as fallback (see EMCP Tools → Connection tab → Generate Configs) |
| Plugin won't install ("requires WP 6.8") | WordPress core out of date | Update WP core first |
