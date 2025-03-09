from fastapi.templating import Jinja2Templates
import jinja2

RESPONSE = Jinja2Templates(directory="./../jinja_templates")
ENVIRONMENT = jinja2.Environment(
    loader=jinja2.PackageLoader("server", "jinja_templates"),
    autoescape=jinja2.select_autoescape(),
)

def get(template_name: str) -> Jinja2Templates:
    try:
        return ENVIRONMENT.get_template(template_name)
    except jinja2.exceptions.TemplateNotFound:
        raise KeyError(f"Template {template_name} not found")
    
def render(template_name: str, **args) -> str:
    template = get(template_name)
    html = template.render(**args)
    return html