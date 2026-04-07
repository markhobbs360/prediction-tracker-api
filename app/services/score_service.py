from app.models.intake_brief import IntakeBrief
from app.models.feature import Feature


def compute_data_readiness(
    intake: IntakeBrief,
    client_features: list[Feature],
) -> dict:
    """Compute a data readiness score (0-100) for an intake brief.

    Returns a dict with 'score' and 'detail' keys.
    """
    detail: dict = {}
    total_weight = 0
    total_earned = 0

    # 1. Feature availability (weight: 30)
    weight_features = 30
    total_weight += weight_features
    available_features = [f for f in client_features if f.status == "available"]
    feature_ratio = len(available_features) / max(len(client_features), 1)
    feature_score = round(feature_ratio * weight_features)
    total_earned += feature_score
    detail["feature_availability"] = {
        "weight": weight_features,
        "score": feature_score,
        "total_features": len(client_features),
        "available_features": len(available_features),
    }

    # 2. Training data alignment completeness (weight: 25)
    weight_training = 25
    total_weight += weight_training
    alignment = intake.training_data_alignment or {}
    alignment_fields = ["dataset_description", "date_range", "outcome_variable"]
    filled = sum(1 for f in alignment_fields if alignment.get(f))
    training_ratio = filled / len(alignment_fields)
    training_score = round(training_ratio * weight_training)
    total_earned += training_score
    detail["training_data_alignment"] = {
        "weight": weight_training,
        "score": training_score,
        "fields_filled": filled,
        "fields_total": len(alignment_fields),
    }

    # 3. Feature checklist completeness (weight: 20)
    weight_checklist = 20
    total_weight += weight_checklist
    checklist = intake.feature_checklist or {}
    checklist_items = checklist.get("items", [])
    checked = sum(1 for item in checklist_items if item.get("confirmed"))
    checklist_ratio = checked / max(len(checklist_items), 1)
    checklist_score = round(checklist_ratio * weight_checklist)
    total_earned += checklist_score
    detail["feature_checklist"] = {
        "weight": weight_checklist,
        "score": checklist_score,
        "items_confirmed": checked,
        "items_total": len(checklist_items),
    }

    # 4. Segmentation requirements (weight: 15)
    weight_seg = 15
    total_weight += weight_seg
    seg = intake.segmentation_requirements or {}
    has_seg = bool(seg.get("segments") or seg.get("criteria"))
    seg_score = weight_seg if has_seg else 0
    total_earned += seg_score
    detail["segmentation_requirements"] = {
        "weight": weight_seg,
        "score": seg_score,
        "defined": has_seg,
    }

    # 5. Objective defined (weight: 10)
    weight_obj = 10
    total_weight += weight_obj
    has_obj = bool(intake.objective and len(intake.objective.strip()) > 10)
    obj_score = weight_obj if has_obj else 0
    total_earned += obj_score
    detail["objective"] = {
        "weight": weight_obj,
        "score": obj_score,
        "defined": has_obj,
    }

    final_score = round((total_earned / max(total_weight, 1)) * 100)
    return {"score": final_score, "detail": detail}
