"""Full-stack connector plane and revenue spine."""
from typing import Any, Dict, Optional

def make_full_stack_tools(world, PRODUCTS, SKUS, Authority, Tool):
    tools = []
    def hubspot_note(text, contact=None):
        rec = {"text": text, "contact": contact, "status": "prepared"}
        world.hubspot_notes.append(rec)
        world.crm.append(rec)
        return rec
    def notion_page(title, content=""):
        rec = {"title": title, "content": content, "status": "prepared"}
        if not hasattr(world, "notion_pages"): world.notion_pages = []
        world.notion_pages.append(rec)
        return rec
    def linear_issue(title, description=""):
        rec = {"title": title, "description": description, "status": "prepared"}
        if not hasattr(world, "linear_issues"): world.linear_issues = []
        world.linear_issues.append(rec)
        return rec
    def revenue_spine_step(step, payload=None):
        rec = {"step": step, "payload": payload or {}, "status": "planned"}
        if not hasattr(world, "spine"): world.spine = []
        world.spine.append(rec)
        return rec
    tools.append(Tool("hubspot_note", hubspot_note, Authority.REVERSIBLE, ("text",)))
    tools.append(Tool("notion_page", notion_page, Authority.REVERSIBLE, ("title",)))
    tools.append(Tool("linear_issue", linear_issue, Authority.REVERSIBLE, ("title",)))
    tools.append(Tool("revenue_spine", revenue_spine_step, Authority.REVERSIBLE, ("step",)))
    return tools

SPINE_HOPS = ["lead_intake", "enrich", "outreach", "proposal", "checkout", "crm_sync", "fulfill", "report"]
