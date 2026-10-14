"""Full-stack CLI: status, run, spine, products, skus."""
import argparse, json
from enablement import run_enablement, EnablementKernel, PRODUCTS, SKUS
from connectors.full_stack import SPINE_HOPS

def main():
    p = argparse.ArgumentParser(description="Garcar Enablement Full Stack")
    p.add_argument("cmd", choices=["status", "run", "spine", "products", "skus"], default="status", nargs="?")
    p.add_argument("--task", default="full-stack")
    p.add_argument("--approve", nargs="*", default=[])
    p.add_argument("--max-cost", type=float, default=1.0)
    p.add_argument("--ledger", default=":memory:")
    args = p.parse_args()
    if args.cmd == "products":
        print(json.dumps(PRODUCTS, indent=2))
    elif args.cmd == "skus":
        print(json.dumps(SKUS, indent=2))
    elif args.cmd == "spine":
        print(json.dumps({"hops": SPINE_HOPS}, indent=2))
    elif args.cmd == "run":
        r = run_enablement(args.task, set(args.approve), args.max_cost, args.ledger)
        print(json.dumps(r, indent=2, default=str))
    else:
        print(json.dumps(EnablementKernel(ledger_path=args.ledger).status(), indent=2))

if __name__ == "__main__":
    main()
