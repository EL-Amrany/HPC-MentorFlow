import os
import re
import json
from app import create_app, db
from app.models import LearningObjective

def parse_md_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Extract module and level from filename, e.g. "A1 apply.md"
    basename = os.path.basename(filepath).replace('.md', '')
    match = re.match(r'([A-Z0-9]+)\s+(\w+)', basename)
    module_key, level = match.groups() if match else (None, None)

    # Find fields in markdown (crude parser, adjust if your files use different structure)
    def extract(field):
        m = re.search(rf'{field}:(.*?)\n(?:[A-Za-z]|$)', content, re.S)
        return m.group(1).strip() if m else ""

    # If your markdown uses "---" for fields, consider using a YAML parser instead.

    # Improved regex to handle lists (prerequisites)
    prereq_match = re.search(r'prerequisite:\n((?:- .*\n?)+)', content)
    if prereq_match:
        prereqs = [line.strip('- ').strip() for line in prereq_match.group(1).strip().split('\n') if line.strip()]
        prereq_json = json.dumps(prereqs)
    else:
        prereq_json = "[]"

    knowledge = extract('knowledge')
    course = extract('course')
    external = extract('external')
    description = extract('description') or content.strip().split('\n')[0]  # fallback: first line

    return {
        "module_key": module_key,
        "level": level,
        "description": description,
        "prerequisites": prereq_json,
        "knowledge": knowledge,
        "course": course,
        "external": external
    }

def import_objectives_from_folder(folder):
    app = create_app()
    with app.app_context():
        for fname in os.listdir(folder):
            if fname.endswith('.md'):
                obj = parse_md_file(os.path.join(folder, fname))
                if not obj["module_key"] or not obj["level"]:
                    print(f"Skipping {fname}, can't parse module/level")
                    continue
                # Upsert by module_key and level
                lo = LearningObjective.query.filter_by(
                    module_key=obj["module_key"], level=obj["level"]
                ).first()
                if not lo:
                    lo = LearningObjective(**obj)
                    db.session.add(lo)
                else:
                    for k, v in obj.items():
                        setattr(lo, k, v)
                db.session.commit()
                print(f"Imported: {obj['module_key']} {obj['level']}")

if __name__ == '__main__':
    import_objectives_from_folder('/Users/samir.el-amrany/Downloads/competency 2/Competency')
