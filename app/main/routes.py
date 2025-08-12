from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import main
from ..models import db, Competency, Module, Progress, User
from ..utils import get_learning_objective
import json
import json
from ..utils import user_has_prereqs
from ..models import LearningObjective

# app/main/routes.py

LEVELS = ["Apprentice", "Practitioner", "Competent", ]


role_display_names = {
    "ai_specialist": "HPC AI Specialist",
    "comp_chem_specialist": "HPC Computational Chemistry Specialist"
}

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/role_select', methods=['GET', 'POST'])
@login_required
def role_select():
    if request.method == 'POST':
        role = request.form['role']
        if role in ['ai_specialist', 'comp_chem_specialist']:
            current_user.role = role
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid role selected.", "danger")
    return render_template('main/role_select.html', role_display_names=role_display_names)

# Map each role to its allowed competencies and modules
ROLE_COMPETENCY_MAP = {
    "ai_specialist": ["A", "B", "C", "D"],  # e.g., only these keys for AI path
    "comp_chem_specialist": ["A", "B", "C", "D"],  # customize as needed
}

ROLE_MODULE_KEYS = {
    "ai_specialist": [
        "A1", "A2",
        "B1", "B2", "B3", "B4", "B5", "B6",
        "C1", "D1", "D2", "D3", 
    ],
    "comp_chem_specialist": [
        "A1", "A2",
        "B1", "B3", "B4", "B5", "B6",
        "C1", "D1", "D2", "D3", 
    ],
}


def get_user_modules(user):
    # Only include modules relevant to the user's role
    allowed_keys = set(ROLE_MODULE_KEYS.get(user.role, []))
    competencies = Competency.query.all()
    data = []
    for comp in competencies:
        # Only include competency if it has at least one relevant module
        modules = Module.query.filter(
            Module.competency_id == comp.id,
            Module.key.in_(allowed_keys)
        ).order_by(Module.order).all()
        if not modules:
            continue
        mod_data = []
        for m in modules:
            prog = Progress.query.filter_by(user_id=user.id, module_id=m.id).first()
            status = prog.status if prog else 'incomplete'
            if prog and prog.learning_level:
                learning_level = prog.learning_level
            else:
                learning_level = get_learning_objective(
                    user.role, m.key, user.current_level
                )
            # Determine the relevant learning level
            if prog and prog.learning_level:
                learning_level = prog.learning_level
            else:
                learning_level = get_learning_objective(user.role, m.key, user.current_level)

            # Quiz is considered passed only if:
            # 1. The quiz was passed (boolean)
            # 2. The level matches the expected level
            quiz_passed = (
                prog.quiz_passed and
                learning_level.lower() == get_learning_objective(user.role, m.key, user.current_level).lower()
            ) if prog else False
            
            mod_data.append({
                "id": m.id,
                "key": m.key,
                "name": m.name,
                "status": status,
                "quiz_passed": quiz_passed,
                "learning_level": learning_level,
            })
        data.append({
            "competency": comp,
            "modules": mod_data
        })
    return data

def get_user_modules_for_level(user, level):
    allowed_keys = set(ROLE_MODULE_KEYS.get(user.role, []))
    competencies = Competency.query.all()
    data = []

    for comp in competencies:
        modules = Module.query.filter(
            Module.competency_id == comp.id,
            Module.key.in_(allowed_keys)
        ).order_by(Module.order).all()

        mod_data = []
        for m in modules:
            expected_skill = get_learning_objective(user.role, m.key, level).lower()

            # Skip if no skill is defined for this level
            if expected_skill in ["", "n/a"]:
                continue

            prog = Progress.query.filter_by(user_id=user.id, module_id=m.id).first()

            # A module is only "completed" for this level if the skill matches
            if prog and prog.status == "completed":
                # Get the actual skill used when they passed it
                user_skill = (prog.learning_level or "").lower()
                completed = user_skill == expected_skill
            else:
                completed = False

            mod_data.append({
                "id": m.id,
                "key": m.key,
                "name": m.name,
                "status": "completed" if completed else "incomplete",
                "quiz_passed": prog.quiz_passed if prog else False,
                "learning_level": expected_skill
            })

        if mod_data:
            data.append({
                "competency": comp,
                "modules": mod_data
            })

    return data




# def get_user_modules(user):
#     # Get modules, progress for user, grouped by competency
#     competencies = Competency.query.all()
#     data = []
#     for comp in competencies:
#         modules = Module.query.filter_by(competency_id=comp.id).order_by(Module.order).all()
#         mod_data = []
#         for m in modules:
#             prog = Progress.query.filter_by(user_id=user.id, module_id=m.id).first()
#             status = prog.status if prog else 'incomplete'
            
#             if prog and prog.learning_level:
#                 learning_level = prog.learning_level
#             else:
#                 # Compute learning_level for this user/module based on their role and current_level
#                 learning_level = get_learning_objective(
#                     user.role, m.key, user.current_level
#                 )
            
#             quiz_passed = prog.quiz_passed if prog else False
#             mod_data.append({
#                 "id": m.id,
#                 "key": m.key,
#                 "name": m.name,
#                 "status": status,
#                 "quiz_passed": quiz_passed,
#                 "learning_level": learning_level,
#             })
#         data.append({
#             "competency": comp,
#             "modules": mod_data
#         })
#     return data
@main.route('/dashboard')
@login_required
def dashboard():
    
    

    LEVELS = ["Apprentice", "Practitioner", "Competent"]
    #current_user.current_level="Apprentice"
    curr_level = current_user.current_level
    modules_data  = get_user_modules_for_level(current_user, current_user.current_level)
    print(modules_data)
    
    role = current_user.role
    #curr_level="Apprentice"
    #print(curr_level)
    if curr_level in LEVELS:
        idx = LEVELS.index(curr_level)
        if idx < len(LEVELS) - 1:
            completed_modules = 0
            total_modules = 0

            for comp in modules_data:
                for module in comp["modules"]:
                    expected_skill = get_learning_objective(current_user.role, module["key"], current_user.current_level)
                    if module["learning_level"] == expected_skill:
                        total_modules += 1
                        if module["status"] == "completed":
                            completed_modules += 1
                #print("check",total_modules_at_level,completed_modules_at_level)

            if total_modules > 0 and total_modules == completed_modules:
                next_level = LEVELS[idx + 1]
                current_user.current_level = next_level
                db.session.commit()
                flash(f"🎉 You've advanced to the **{next_level}** level!", "success")
                return redirect(url_for('main.dashboard'))

    total_modules = sum(len(comp["modules"]) for comp in modules_data)
    completed_modules = sum(
        1 for comp in modules_data for module in comp["modules"] if module["status"] == "completed"
    )
    percent_complete = int((completed_modules / total_modules) * 100) if total_modules else 0
    role_name = role_display_names.get(current_user.role, current_user.role)
    active_sessions = 2  # placeholder

    flat_modules = {module["key"]: module for comp in modules_data for module in comp["modules"]}
    for comp in modules_data:
        for module in comp["modules"]:
            lvl = (module.get("learning_level") or "").lower()
            if module["key"] == "A1" and lvl == "apply":
                module["locked"] = flat_modules.get("B5", {}).get("status") != "completed"
            elif module["key"] == "A2" and lvl == "remember":
                b1 = flat_modules.get("B1", {})
                b4 = flat_modules.get("B4", {})
                module["locked"] = not (
                    b1.get("learning_level", "").lower() == "apply"
                    and b1.get("status") == "completed"
                    and b4.get("learning_level", "").lower() == "apply"
                    and b4.get("status") == "completed"
                )
            else:
                module["locked"] = False

    return render_template(
        'main/dashboard.html',
        modules_data=modules_data,
        completed_modules=completed_modules,
        total_modules=total_modules,
        percent_complete=percent_complete,
        role_name=role_name,
        current_level=current_user.current_level,
        active_sessions=active_sessions
    )




# @main.route('/mark_complete/<int:module_id>', methods=['POST'])
# @login_required
# def mark_complete(module_id):
#     progress = Progress.query.filter_by(
#         user_id=current_user.id, module_id=module_id
#     ).first()

#     if not (progress and progress.quiz_passed):
#         return '', 400

#     module_key = progress.module.key
#     learning_level = get_learning_objective(current_user.role, module_key, current_user.current_level)

#     progress.status = "completed"
#     progress.learning_level = learning_level.capitalize()
#     progress.user_level = current_user.current_level  # <-- Explicitly track user level
#     db.session.commit()

#     return '', 204





from app.models import LearningObjective


@main.route('/module/<int:module_id>')
@login_required
def module(module_id):
    module = Module.query.get_or_404(module_id)
    # Fetch the learning objective and its prereqs
    lo = LearningObjective.query.filter_by(
        module_key=module.key,
        level=current_user.current_level.lower()
    ).first()
    prerequisites = json.loads(lo.prerequisites) if lo and lo.prerequisites else []

    # Check if user meets all prereqs
    prereqs_satisfied = user_has_prereqs(current_user, prerequisites)

    progress = Progress.query.filter_by(
        user_id=current_user.id, module_id=module.id
    ).first() or Progress(user_id=current_user.id, module_id=module.id)

    return render_template(
        'main/module.html',
        module=module,
        progress=progress,
        learning_objective=lo,
        prerequisites=prerequisites,
        prereqs_satisfied=prereqs_satisfied
    )

@main.route('/mark_complete/<int:module_id>', methods=['POST'])
@login_required
def mark_complete(module_id):
    progress = Progress.query.filter_by(user_id=current_user.id, module_id=module_id).first()
    if not progress or not progress.quiz_passed:
        return '', 400

    # Save the SKILL for this module at the user's current level
    skill = get_learning_objective(current_user.role, progress.module.key, current_user.current_level)
    progress.learning_level = skill              # e.g., "apply", "remember"
    progress.user_level = current_user.current_level  # e.g., "Apprentice"
    progress.status = "completed"
    db.session.commit()
    return '', 204






