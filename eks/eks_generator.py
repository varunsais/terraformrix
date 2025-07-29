import yaml
import openai
import os
import json
from utils.common import validate_yaml, create_prompt, extract_json_content

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set")

def generate_eks_json(yaml_path: str, output_path: str):
    with open(yaml_path, "r") as f:
        yaml_dict = yaml.safe_load(f)

    validate_yaml(yaml_dict)

    prompt = create_prompt(yaml_dict, service="eks")
    prompt += "\n\n" + "If 'cluster_iam_role.create' is true in the YAML, generate an aws_iam_role resource named using 'cluster_iam_role.name', with sts:AssumeRole trust policy. Also attach all policies listed using aws_iam_role_policy_attachment."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert DevOps engineer who writes clean, valid Terraform JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    content = response.choices[0].message["content"]
    json_text = extract_json_content(content)
    terraform_json = json.loads(json_text)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(terraform_json, f, indent=2)
    print(f"✅ EKS Terraform JSON written to {output_path}")

