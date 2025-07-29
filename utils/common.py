import yaml
import re

def validate_yaml(yaml_dict):
    if not yaml_dict or not isinstance(yaml_dict, dict):
        raise ValueError("YAML is empty or not a valid dictionary")

def create_prompt(yaml_dict, service="rds"):
    base_prompt = "You are an expert in Terraform and JSON. Convert the following YAML into valid Terraform JSON. Respond ONLY with the JSON inside a ```json block.\n"
    
    if service == "rds":
        base_prompt += """
For RDS:
- Use aws_db_instance with:
  - identifier (not instance_identifier)
  - db_name (not name)
  - allocated_storage
  - storage_type
  - engine
  - engine_version
  - instance_class
  - username
  - password (use the string directly from the YAML, not a variable)  
  - parameter_group_name
  - vpc_security_group_ids
  - db_subnet_group_name
  - publicly_accessible
  - timeouts block (create = 30m, delete = 15m)
  - tags
- Include aws_db_subnet_group if defined.
"""
    elif service == "eks":
        base_prompt += """
For EKS:
- Include aws_eks_cluster with role_arn, vpc_config (subnet_ids, security_group_ids), enabled_cluster_log_types, and timeouts.
- Include aws_eks_node_group with instance_types, scaling_config, disk_size, remote_access, and timeouts.
"""
    elif service == "vpc":
        base_prompt += """
For VPC:
- Include aws_vpc, aws_subnet (public/private), aws_internet_gateway, aws_route_table, aws_nat_gateway, aws_eip.
- In aws_route_table.route, include all optional attributes set to null if not used:
  carrier_gateway_id, core_network_arn, destination_prefix_list_id, egress_only_gateway_id,
  gateway_id, ipv6_cidr_block, local_gateway_id, nat_gateway_id, network_interface_id,
  transit_gateway_id, vpc_endpoint_id, vpc_peering_connection_id.
- For aws_eip, use only "domain": "vpc", not "vpc": true.
"""

    return base_prompt + f"\nYAML:\n{yaml.dump(yaml_dict, sort_keys=False)}"

def extract_json_content(content: str) -> str:
    """
    Extracts the JSON code block from OpenAI response.
    Falls back to full content if no code block is found.
    """
    match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    print("⚠️ No ```json block found, using raw content")
    return content.strip()

def patch_rds_fields(resource):
    if "aws_db_instance" in resource:
        for _, rds in resource["aws_db_instance"].items():
            if "instance_identifier" in rds:
                rds["identifier"] = rds.pop("instance_identifier")
            rds.pop("name", None)
def inject_null_route_fields(resource):
    null_fields = [
        "carrier_gateway_id", "core_network_arn", "destination_prefix_list_id",
        "egress_only_gateway_id", "gateway_id", "ipv6_cidr_block", "local_gateway_id",
        "nat_gateway_id", "network_interface_id", "transit_gateway_id", "vpc_endpoint_id",
        "vpc_peering_connection_id"
    ]

    if not isinstance(resource, dict):
        print("⚠️ 'resource' is not a dict, skipping injection.")
        return

    route_tables = resource.get("aws_route_table", {})
    if not isinstance(route_tables, dict):
        print("⚠️ 'aws_route_table' is not a dict, skipping injection.")
        return

    for _, block in route_tables.items():
        routes = block.get("route", [])
        if isinstance(routes, list):
            for route in routes:
                if isinstance(route, dict):
                    for key in null_fields:
                        route.setdefault(key, None)
                else:
                    print(f"⚠️ Skipping non-dict route: {route}")

