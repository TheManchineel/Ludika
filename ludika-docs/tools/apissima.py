# apissima: an OpenAPI (Swagger) to TeX documentation converter
# v.0.1.0: initial release
# by Manchineel

from fastapi.openapi.utils import get_openapi
from ludika_backend.api import app
import json
import os

openapi_schema = get_openapi(
    title="Ludika API",
    version="1.0.0",
    description="Ludika API",
    routes=app.routes,
)

colors = {
    "get": "violettissimo",
    "post": "verde",
    "put": "orange",
    "delete": "red",
    "patch": "purple"
}

TEX_SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "../paper/includes/api_schema.tex")

def escape_latex(text: str) -> str:
    """Escape special LaTeX characters in the given text."""
    if not text:
        return ""
    return text.replace("{", "\\string{").replace("}", "\\string}").replace("_", "\\_")

def get_request_body_type(request_body: dict) -> str:
    """Extract the request body content type."""
    if "requestBody" not in request_body or "content" not in request_body["requestBody"]:
        return ""
    
    content_keys = list(request_body["requestBody"]["content"].keys())
    if content_keys:
        return content_keys[0]
    return ""

def get_response_type(responses: dict) -> str:
    """Extract the first response type that starts with '2'. Some endpoints have a 201 response code for creation."""
    if "responses" not in responses:
        return ""
    
    success_codes = [code for code in responses["responses"].keys() if code.startswith("2")]
    if not success_codes:
        return ""
    
    first_success_code = success_codes[0]
    response_content = responses["responses"][first_success_code].get("content", {})
    
    if response_content:
        content_type = next(iter(response_content.keys()))
        return f"{content_type} ({content_type.split('/')[-1]})"
    
    return ""

def build_endpoint_text(path: str, methods: dict) -> str:
    escaped_path = escape_latex(path)
    
    text = f"""
\\textbullet\\ \\texttt{{{escaped_path}}}:"""
    for method, method_attrs in methods.items():
        print(f"Now building {method} {path}")
        
        request_body_type = get_request_body_type(method_attrs)
        response_type = get_response_type(method_attrs)
        
        escaped_summary = escape_latex(method_attrs["summary"]) if "summary" in method_attrs else ""
        escaped_description = escape_latex(method_attrs["description"]) if "description" in method_attrs else ""
        escaped_request_body = escape_latex(request_body_type) if request_body_type else ""
        escaped_response = escape_latex(response_type) if response_type else ""
        is_protected = "security" in method_attrs
        protection_symbol = "\\faLock{} " if is_protected else ""
        
        text += (f"""\\begin{{tcolorbox}}[colback={colors[method]}!10!white, colframe={colors[method]}, title=\\textbf{{{protection_symbol}{method.upper()} {escaped_path}}} --- {escaped_summary}, fonttitle=\\bfseries, sharp corners=south, boxrule=0.8pt, left=2mm, right=2mm, top=1mm, bottom=1mm]""")
        lines = []
        if escaped_description:
            lines.append(f"\\textbf{{Description:}} {escaped_description}")
        if escaped_request_body:
            lines.append(f"\\textbf{{Request Body:}} \\texttt{{{escaped_request_body}}}")
        if escaped_response:
            lines.append(f"\\textbf{{Response:}} \\texttt{{{escaped_response}}}")
        text += "\\\\\n".join(lines)
        text += "\\end{tcolorbox}\n"
    return text

with open(TEX_SCHEMA_FILE, "w") as f:
    for path, methods in openapi_schema["paths"].items():
        f.write(build_endpoint_text(path, methods))
        f.write("\n")