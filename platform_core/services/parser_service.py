"""
Specification parsing service for OpenAPI (JSON/YAML) and Postman Collections.
Extracts endpoints, parameters, request bodies, response schemas, and authentication specs.
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
import httpx
import yaml


class ParserService:
    """Parses API specifications and collections into normalized endpoint dictionaries."""

    @staticmethod
    def parse_openapi(spec_content: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parses OpenAPI 2.0 / 3.0 / 3.1 specification (JSON or YAML format).
        Returns metadata (title, base_url, version) and list of normalized endpoints.
        """
        # Parse content as JSON or YAML
        try:
            spec = json.loads(spec_content)
        except Exception:
            try:
                spec = yaml.safe_load(spec_content)
            except Exception as err:
                raise ValueError(f"Failed to parse OpenAPI specification as JSON or YAML: {err}")

        if not isinstance(spec, dict):
            raise ValueError("Invalid OpenAPI specification: root must be a dictionary.")

        info = spec.get("info", {})
        title = info.get("title", "Imported API Project")
        version = info.get("version", "1.0.0")
        description = info.get("description", "")

        # Infer base URL
        base_url = "http://127.0.0.1:8000"
        servers = spec.get("servers", [])
        if servers and isinstance(servers, list) and len(servers) > 0:
            server_url = servers[0].get("url", "")
            if server_url and not server_url.startswith("/"):
                base_url = server_url.rstrip("/")
        elif "host" in spec:
            scheme = "https" if "https" in spec.get("schemes", ["http"]) else "http"
            base_path = spec.get("basePath", "").rstrip("/")
            base_url = f"{scheme}://{spec['host']}{base_path}"

        endpoints: List[Dict[str, Any]] = []
        paths = spec.get("paths", {})

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for method_name in ["get", "post", "put", "patch", "delete", "options", "head"]:
                if method_name not in path_item:
                    continue

                operation = path_item[method_name]
                if not isinstance(operation, dict):
                    continue

                method = method_name.upper()
                summary = operation.get("summary") or operation.get("operationId") or f"{method} {path}"
                op_desc = operation.get("description") or ""

                # Extract parameters
                parameters = []
                # Common path-level parameters
                all_params = list(path_item.get("parameters", [])) + list(operation.get("parameters", []))
                for p in all_params:
                    if isinstance(p, dict):
                        parameters.append({
                            "name": p.get("name", ""),
                            "in": p.get("in", "query"),  # query, path, header
                            "required": p.get("required", False),
                            "type": p.get("schema", {}).get("type", "string") if "schema" in p else p.get("type", "string"),
                            "description": p.get("description", "")
                        })

                # Extract request body template
                request_body = None
                req_body_obj = operation.get("requestBody", {})
                if req_body_obj and isinstance(req_body_obj, dict):
                    content = req_body_obj.get("content", {})
                    json_content = content.get("application/json", {})
                    schema = json_content.get("schema", {})
                    request_body = ParserService._generate_sample_from_schema(schema, spec)

                # Expected status
                responses = operation.get("responses", {})
                expected_status = 200
                for code_str in ["200", "201", "204"]:
                    if code_str in responses:
                        expected_status = int(code_str)
                        break

                # Auth required check
                auth_required = bool(operation.get("security") or spec.get("security"))

                endpoints.append({
                    "path": path,
                    "method": method,
                    "summary": summary,
                    "description": op_desc,
                    "parameters": parameters,
                    "request_body": request_body,
                    "expected_status": expected_status,
                    "auth_required": auth_required
                })

        meta = {
            "title": title,
            "version": version,
            "description": description,
            "base_url": base_url
        }
        return meta, endpoints

    @staticmethod
    def _generate_sample_from_schema(schema: Dict[str, Any], root_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate sample JSON request payload based on JSON Schema properties."""
        if not schema or not isinstance(schema, dict):
            return None

        # Resolve $ref if present
        ref = schema.get("$ref")
        if ref and isinstance(ref, str) and ref.startswith("#/"):
            parts = ref.lstrip("#/").split("/")
            resolved = root_spec
            for part in parts:
                resolved = resolved.get(part, {})
            if resolved:
                return ParserService._generate_sample_from_schema(resolved, root_spec)

        props = schema.get("properties", {})
        if not props:
            return None

        sample: Dict[str, Any] = {}
        for prop_name, prop_def in props.items():
            if not isinstance(prop_def, dict):
                sample[prop_name] = "value"
                continue

            ptype = prop_def.get("type", "string")
            pformat = prop_def.get("format", "")

            if ptype == "integer":
                sample[prop_name] = prop_def.get("example", 1)
            elif ptype == "number":
                sample[prop_name] = prop_def.get("example", 1.0)
            elif ptype == "boolean":
                sample[prop_name] = prop_def.get("example", True)
            elif ptype == "array":
                sample[prop_name] = []
            elif ptype == "string":
                if pformat == "email":
                    sample[prop_name] = "testuser@example.com"
                elif "example" in prop_def:
                    sample[prop_name] = prop_def["example"]
                else:
                    sample[prop_name] = f"sample_{prop_name}"
            else:
                sample[prop_name] = "sample_value"

        return sample

    @staticmethod
    def parse_postman_collection(collection_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parses Postman Collection v2.0 / v2.1.
        Extracts collection metadata, folder structure, requests, and payloads.
        """
        info = collection_dict.get("info", {})
        title = info.get("name", "Postman Imported API")
        description = info.get("description", "")
        base_url = "http://127.0.0.1:8000"

        # Check collection variables for base_url
        variables = collection_dict.get("variable", [])
        for var in variables:
            if isinstance(var, dict) and var.get("key") in ["base_url", "baseUrl", "host", "url"]:
                val = var.get("value", "")
                if val:
                    base_url = val.rstrip("/")

        endpoints: List[Dict[str, Any]] = []

        def _traverse_items(items_list: List[Dict[str, Any]], folder_name: str = ""):
            for item in items_list:
                if not isinstance(item, dict):
                    continue

                if "item" in item:
                    # It's a folder
                    sub_folder = item.get("name", "")
                    new_folder = f"{folder_name}/{sub_folder}" if folder_name else sub_folder
                    _traverse_items(item["item"], new_folder)
                elif "request" in item:
                    # It's a request
                    req = item["request"]
                    name = item.get("name", "API Request")
                    method = req.get("method", "GET").upper()

                    # Extract URL
                    url_obj = req.get("url", "")
                    path = "/"
                    parameters = []

                    if isinstance(url_obj, str):
                        parsed = urlparse(url_obj)
                        path = parsed.path or "/"
                    elif isinstance(url_obj, dict):
                        raw_path = url_obj.get("path", [])
                        if isinstance(raw_path, list):
                            path = "/" + "/".join(str(p).lstrip("/") for p in raw_path)
                        elif isinstance(raw_path, str):
                            path = "/" + raw_path.lstrip("/")

                        # Extract query parameters
                        for q in url_obj.get("query", []):
                            if isinstance(q, dict):
                                parameters.append({
                                    "name": q.get("key", ""),
                                    "in": "query",
                                    "required": False,
                                    "type": "string",
                                    "description": q.get("description", "")
                                })

                    # Extract body
                    request_body = None
                    body_obj = req.get("body", {})
                    if isinstance(body_obj, dict) and body_obj.get("mode") == "raw":
                        raw_text = body_obj.get("raw", "")
                        try:
                            request_body = json.loads(raw_text)
                        except Exception:
                            request_body = None

                    # Check headers for auth
                    auth_required = False
                    if "auth" in req or "auth" in collection_dict:
                        auth_required = True
                    for h in req.get("header", []):
                        if isinstance(h, dict) and h.get("key", "").lower() == "authorization":
                            auth_required = True

                    expected_status = 201 if method == "POST" else (204 if method == "DELETE" else 200)

                    endpoints.append({
                        "path": path,
                        "method": method,
                        "summary": name,
                        "description": f"Imported from folder: {folder_name}" if folder_name else "",
                        "parameters": parameters,
                        "request_body": request_body,
                        "expected_status": expected_status,
                        "auth_required": auth_required
                    })

        _traverse_items(collection_dict.get("item", []))

        meta = {
            "title": title,
            "description": description,
            "base_url": base_url
        }
        return meta, endpoints

    @staticmethod
    async def auto_discover_from_base_url(base_url: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Attempts to discover OpenAPI / Swagger JSON from a live target base URL.
        Checks /openapi.json, /api/openapi.json, /swagger.json, /api/v1/openapi.json.
        """
        clean_base = base_url.rstrip("/")
        candidates = [
            f"{clean_base}/openapi.json",
            f"{clean_base}/swagger.json",
            f"{clean_base}/api/openapi.json",
            f"{clean_base}/api/v1/openapi.json"
        ]

        async with httpx.AsyncClient(timeout=4.0) as client:
            for url in candidates:
                try:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        text = resp.text
                        meta, endpoints = ParserService.parse_openapi(text)
                        meta["base_url"] = clean_base
                        return meta, endpoints
                except Exception:
                    continue

        # If no openapi spec is found, check /health or root
        meta = {
            "title": f"API at {urlparse(clean_base).netloc or clean_base}",
            "description": "Auto-discovered target API",
            "base_url": clean_base
        }
        # Provide base root endpoint
        endpoints = [
            {
                "path": "/health",
                "method": "GET",
                "summary": "Health Check",
                "description": "Probe service availability",
                "parameters": [],
                "request_body": None,
                "expected_status": 200,
                "auth_required": False
            }
        ]
        return meta, endpoints
