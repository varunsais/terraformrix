# Terraformrix

**AI-Powered YAML to Terraform JSON Generator**

Terraformrix is an AI-augmented tool that converts YAML infrastructure specifications into valid Terraform JSON using GPT-4. It simplifies infrastructure provisioning by turning human-readable YAML into machine-executable Terraform code. The system is modular, extensible, and cloud-provider-agnostic.

---

## 🔧 Features

- 🧠 GPT-4-based YAML to Terraform JSON conversion
- 📦 Supports AWS services
- ⚙️ Modular code structure with dynamic prompt generation
- ✅ Post-processing for validation and formatting
- 💾 Generates `.tf.json` files ready for `terraform init` and `terraform plan`

---

## 🗂️ Project Structure

terraformrix/
├── gen/ # Service-specific generators
│ ├── eks_generator.py
│ ├── rds_generator.py
│ ├── vpc_generator.py
│ └── gen.py
├── inputs/ # YAML inputs for infrastructure
│ ├── eks.yaml
│ ├── rds.yaml
│ └── vpc.yaml
├── output/terraform/ # Generated Terraform JSON
├── utils/ # Shared helpers
│ └── common.py
├── .env # Your OpenAI API key (not committed)
└── README.md

⚙️ How It Works

1. **Clone the repo**  
   ```bash
   git clone https://github.com/varunsais/terraformrix.git
   cd terraformrix
   
2. Install dependencies
    It's recommended to use a virtual environment:
    
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    Set your OpenAI API key
    Create a .env file:
    ```
    ```
    OPENAI_API_KEY=your-openai-key-here
    ```
3. Usage
  Run generation for a specific service:
  ```
  python gen/gen.py vpc      # Generates VPC Terraform JSON
  python gen/gen.py eks      # Generates EKS Terraform JSON
  python gen/gen.py rds      # Generates RDS Terraform JSON
  ```
Output will be written to:
```
output/terraform/{service}.tf.json
```
You can then run:
```
cd output/terraform
terraform init && terraform plan && terraform apply
```
4. How It Works
   
  - Reads YAML from inputs/{service}.yaml
  
  - Sends a structured prompt to GPT-4 via OpenAI API
  
  - Extracts the valid terraform.tf.json structure from the response
  
  - Outputs clean Terraform JSON

📦 Currently Supported

✅ VPC: aws_vpc, aws_subnet, aws_route_table, aws_internet_gateway, aws_nat_gateway

✅ EKS: aws_eks_cluster, aws_eks_node_group, IAM roles

✅ RDS: aws_db_instance, aws_db_subnet_group

YAML

```
eks:
  cluster_name: demo-eks-cluster-2025
  version: 1.29
```

➡️ generates Terraform like:

```
{
  "resource": {
    "aws_eks_cluster": {
      ...
    }
  }
}
```

🧩 Extensibility
Want to support GCP, Azure, or Kubernetes CRDs?
Just add a new generator in gen/ and customize the prompt in utils/common.py.
