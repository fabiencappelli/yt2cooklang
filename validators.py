def validate_cooklang(text: str) -> None:
    if not text.startswith("---\n"):
        raise ValueError("Le fichier doit commencer par un frontmatter YAML.")

    if ">>" in text:
        raise ValueError("Ancien format metadata Cooklang interdit : >> trouvé.")

    if "@" not in text:
        raise ValueError("Aucun ingrédient Cooklang détecté : @ manquant.")

    if "~" not in text:
        print("Warning: aucun timer Cooklang détecté.")

    if "#" not in text:
        print("Warning: aucun ustensile Cooklang détecté.")