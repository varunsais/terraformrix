import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rds.rds_generator import generate_rds_json
from eks.eks_generator import generate_eks_json
from vpc.vpc_generator import generate_vpc_json

def main():
    if len(sys.argv) != 2:
        print("Usage: python gen.py [rds|eks|vpc]")
        sys.exit(1)

    service = sys.argv[1].lower()

    try:
        if service == "rds":
            generate_rds_json("rds/config.d/rds.yml", "rds/rds_terraform.tf.json")
        elif service == "eks":
            generate_eks_json("eks/config.d/eks.yml", "eks/eks_terraform.tf.json")
        elif service == "vpc":
            generate_vpc_json("vpc/config.d/vpc.yml", "vpc/vpc_terraform.tf.json")
        else:
            print(f"❌ Unknown service: {service}")
            sys.exit(1)

        print(f"✅ {service.upper()} Terraform JSON generated successfully.")
    except Exception as e:
        print(f"❌ Failed to generate {service.upper()} Terraform JSON: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()