import json
import os
import yaml
import openai
from utils.common import validate_yaml, create_prompt, extract_json_content, inject_null_route_fields

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set")

def generate_vpc_json(yaml_path: str, output_path: str):
    try:
        with open(yaml_path, "r") as f:
            yaml_dict = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Failed to read YAML: {e}")
        return

    validate_yaml(yaml_dict)
    prompt = create_prompt(yaml_dict, service="vpc")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert DevOps engineer who writes clean, valid Terraform JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
    except Exception as e:
        print(f"❌ OpenAI API call failed: {e}")
        return

    content = response.choices[0].message["content"]
    json_text = extract_json_content(content)

    try:
        terraform_json = json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print("🔍 Raw content:")
        print(json_text)
        return

    if not isinstance(terraform_json.get("resource"), dict):
        print("❌ 'resource' is not a valid dictionary. Raw resource:")
        print(terraform_json.get("resource"))
        return

    inject_null_route_fields(terraform_json["resource"])

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(terraform_json, f, indent=2)
        print(f"✅ VPC Terraform JSON written to {output_path}")
    except Exception as e:
        print(f"❌ Failed to write JSON file: {e}")

