"""Top-level entry for the full Garcar Enablement project."""
import argparse, json

def main():
    p = argparse.ArgumentParser(description="Garcar Enablement Full Project")
    p.add_argument("cmd", choices=["status", "enable", "agent", "revenue", "sales-help"], default="status", nargs="?")
    p.add_argument("--task", default="full")
    p.add_argument("--role", default="governance")
    p.add_argument("--sku", default="LLA-47")
    p.add_argument("--proof", default="pending")
    args = p.parse_args()
    if args.cmd == "status":
        from enablement import EnablementKernel
        from agents.layer import AgentLayer
        from revenue.layer import RevenueLayer
        print(json.dumps({"enablement": EnablementKernel().status(), "agents": AgentLayer().status(), "revenue": RevenueLayer().coverage_report()}, indent=2))
    elif args.cmd == "enable":
        from enablement import run_enablement
        print(json.dumps(run_enablement(args.task), indent=2, default=str))
    elif args.cmd == "agent":
        from agents.layer import run_agent
        print(json.dumps(run_agent(args.task, role=args.role), indent=2, default=str))
    elif args.cmd == "revenue":
        from revenue.layer import run_revenue
        print(json.dumps(run_revenue(args.sku, args.proof), indent=2, default=str))
    elif args.cmd == "sales-help":
        print("cd garcar-autonomous-sales && python bootstrap.py")

if __name__ == "__main__":
    main()
