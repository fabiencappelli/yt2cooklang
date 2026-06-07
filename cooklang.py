import yaml
from schemas import RecipeExtraction


def clean_scalar(value):
    if value is None:
        return None
    return str(value).strip()


def build_frontmatter(recipe: RecipeExtraction) -> str:
    data = {
        "title": recipe.title,
        "description": recipe.description,
        "source": recipe.source,
        "servings": recipe.servings,
        "course": recipe.course,
        "prep time": recipe.prep_time,
        "cook time": recipe.cook_time,
        "time required": recipe.time_required,
        "cuisine": recipe.cuisine,
        "author": recipe.author,
    }

    data = {k: clean_scalar(v) for k, v in data.items() if v}

    return "---\n" + yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
    ) + "---\n\n"


def ingredient_to_cook(name: str, quantity=None, unit=None) -> str:
    name = name.strip()

    if quantity is None:
        return f"@{name}"

    if unit:
        return f"@{name}{{{quantity}%{unit}}}"

    return f"@{name}{{{quantity}}}"


def cookware_to_cook(name: str) -> str:
    return f"#{name.strip()}"


def timer_to_cook(quantity, unit) -> str:
    if quantity is None:
        return ""

    if unit:
        return f"~{{{quantity}%{unit}}}"

    return f"~{{{quantity}}}"


def render_step(step, recipe: RecipeExtraction) -> str:
    return step.cooklang_text.strip()


def recipe_to_cooklang(recipe: RecipeExtraction) -> str:
    content = build_frontmatter(recipe)

    for step in recipe.steps:
        content += render_step(step, recipe)
        content += "\n\n"

    if recipe.notes:
        content += "## Notes\n\n"
        for note in recipe.notes:
            content += f"- {note}\n"

    if recipe.uncertainties:
        content += "\n## Incertitudes\n\n"
        for uncertainty in recipe.uncertainties:
            content += f"- {uncertainty}\n"

    return content.strip() + "\n"