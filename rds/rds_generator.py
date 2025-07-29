import json
import os
import yaml
import openai
from utils.common import validate_yaml, create_prompt, extract_json_content, patch_rds_fields

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set")

def generate_rds_json(yaml_path: str, output_path: str):
    with open(yaml_path, "r") as f:
        yaml_dict = yaml.safe_load(f)

    validate_yaml(yaml_dict)
    prompt = create_prompt(yaml_dict, service="rds")

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
        raise RuntimeError(f"❌ OpenAI API call failed: {e}")

    content = response.choices[0].message["content"]
    print("🔍 Full GPT response content:")
    print(content)

    json_text = extract_json_content(content)
    print("\n🔍 Extracted JSON text (pre-parsing):")
    print(json_text)

    if not json_text.strip():
        raise ValueError("❌ OpenAI returned an empty or invalid response")

    try:
        terraform_json = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ JSON parsing failed: {e}")

    patch_rds_fields(terraform_json["resource"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(terraform_json, f, indent=2)

    print(f"✅ RDS Terraform JSON written to {output_path}")

