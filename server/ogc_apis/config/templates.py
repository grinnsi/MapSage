from fastapi.templating import Jinja2Templates
import jinja2
import orjson

ENVIRONMENT = jinja2.Environment(
    loader=jinja2.PackageLoader("server", "jinja_templates"),
    autoescape=jinja2.select_autoescape(),
)
RESPONSE = Jinja2Templates(env=ENVIRONMENT)
RESPONSE.env.filters["to_json"] = lambda value: orjson.dumps(value).decode("utf-8")

def get(template_name: str) -> jinja2.Template:
    try:
        return ENVIRONMENT.get_template(template_name)
    except jinja2.exceptions.TemplateNotFound:
        raise KeyError(f"Template '{template_name}' not found")
    
def render(template_name: str, **args) -> str:
    template = get(template_name)
    html = template.render(**args)
    return html

def response(template_name: str, request, context: dict, headers: dict) -> str:
    return RESPONSE.TemplateResponse(  
        name=template_name,
        request=request,
        context=context,
        headers=headers
    )