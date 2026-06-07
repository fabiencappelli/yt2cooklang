import argparse
import json
from pathlib import Path

from youtube import fetch_metadata, fetch_transcript
from ollama_client import call_ollama_structured
from schemas import RecipeExtraction
from cooklang import recipe_to_cooklang
from validators import validate_cooklang


SYSTEM_PROMPT = """
/no_think

Retourne uniquement du JSON valide.
N'écris aucun raisonnement.
N'écris aucun commentaire.
N'écris aucun texte avant ou après le JSON.

Tu es un extracteur de recettes YouTube.

Ta mission est de transformer les informations suivantes :

* titre de la vidéo
* description de la vidéo
* transcript de la vidéo

en une recette structurée au format JSON.

Règles générales :

1. N'invente jamais un ingrédient.
2. N'invente jamais une quantité.
3. N'invente jamais un temps de cuisson.
4. Si une information n'est pas présente, utilise null.
5. La description YouTube est prioritaire pour les ingrédients et les quantités.
6. Le transcript est prioritaire pour l'ordre des étapes.
7. Ignore :

   * les introductions
   * les blagues
   * les appels à s'abonner
   * les sponsors
   * les commentaires personnels
8. Conserve l'ordre réel de préparation.

IMPORTANT : les étapes doivent être écrites en Cooklang.

Chaque étape possède un champ :

cooklang_text

Ce champ doit contenir du vrai Cooklang.

Exemples :

Mauvais :

"Couper 200 g de porc."

Bon :

"Couper @porc{200%g} en morceaux."

Mauvais :

"Faire chauffer une poêle."

Bon :

"Faire chauffer #poêle à feu vif."

Mauvais :

"Cuire pendant 5 minutes."

Bon :

"Cuire ~{5%minutes}."

Mauvais :

"Ajouter l'ail."

Bon :

"Ajouter @ail{3%gousses}."

Les ingrédients doivent être annotés avec :

@ingredient{quantité%unité}

Exemples :

@porc{200%g}
@ail{3%gousses}
@huile de tournesol{2%c.à.c.}

Les ustensiles doivent être annotés avec :

#ustensile

Exemples :

#poêle
#cocotte
#mixeur

Les temps doivent être annotés avec :

~{quantité%unité}

Exemples :

~{30%secondes}
~{5%minutes}
~{1%heure}

IMPORTANT :

Chaque étape doit contenir les annotations Cooklang lorsqu'elles sont connues.

Un champ cooklang_text qui ne contient aucun symbole @, # ou ~ est probablement incorrect.

Retourne uniquement un JSON valide.

Ne retourne jamais :

* Markdown
* YAML
* texte explicatif
* commentaire
* bloc de code

Structure attendue :

{
"title": "...",
"description": "...",
"author": "...",
"servings": "...",
"cuisine": "...",
"course": "...",
"prep_time": "...",
"cook_time": "...",
"time_required": "...",
"ingredients": [
{
"name": "...",
"quantity": ...,
"unit": "..."
}
],
"steps": [
{
"order": 1,
"cooklang_text": "..."
}
],
"notes": [],
"uncertainties": []
}

"""

def trim_text(text: str | None, max_chars: int) -> str:
    if not text:
        return ""

    text = text.strip()

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n\n[TRONQUÉ]"

def build_user_prompt(metadata: dict, transcript: str) -> str:
    return f"""
Titre YouTube :
{metadata.get("title")}

Chaîne :
{metadata.get("channel")}

URL :
{metadata.get("webpage_url")}

Description YouTube :
{trim_text(metadata.get("description"), 6000)}

Transcript :
{trim_text(transcript, 20000)}
"""


def safe_filename(title: str) -> str:
    cleaned = "".join(
        char.lower() if char.isalnum() else "-"
        for char in title
    )
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "recette"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL de la vidéo YouTube")
    parser.add_argument("--model", default="qwen3:4b")
    parser.add_argument("--out", default="recipes")
    parser.add_argument("--debug-json", action="store_true")

    args = parser.parse_args()

    metadata = fetch_metadata(args.url)
    transcript = fetch_transcript(args.url)

    user_prompt = build_user_prompt(metadata, transcript)
    print(f"Longueur du prompt : {len(user_prompt):,} caractères", flush=True)

    raw_recipe = call_ollama_structured(
        model=args.model,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema_model=RecipeExtraction,
    )

    recipe = RecipeExtraction.model_validate(raw_recipe)

    if not recipe.source:
        recipe.source = metadata.get("webpage_url")

    recipe.author = metadata.get("channel")

    cooklang = recipe_to_cooklang(recipe)
    validate_cooklang(cooklang)

    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = safe_filename(recipe.title)
    cook_path = output_dir / f"{filename}.cook"

    cook_path.write_text(cooklang, encoding="utf-8")

    if args.debug_json:
        json_path = output_dir / f"{filename}.json"
        json_path.write_text(
            json.dumps(recipe.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"Recette écrite : {cook_path}")


if __name__ == "__main__":
    main()