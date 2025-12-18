"""
Module de génération d'ordonnances médicales.

Génère des ordonnances formatées pour les examens d'imagerie
recommandés par le système d'évaluation des céphalées.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from .models import HeadacheCase, ImagingRecommendation
from .logging_config import get_logger, log_error_with_context


class PrescriptionError(Exception):
    """Erreur lors de la génération d'ordonnance."""
    pass


def generate_prescription(
    case: HeadacheCase,
    recommendation: ImagingRecommendation,
    doctor_name: str = "Dr. [NOM]",
    output_dir: Optional[Path] = None
) -> Path:
    """Génère une ordonnance médicale formatée.

    Args:
        case: Cas clinique du patient
        recommendation: Recommandation d'imagerie
        doctor_name: Nom du médecin prescripteur
        output_dir: Répertoire de sortie (défaut: ordonnances/)

    Returns:
        Path vers le fichier d'ordonnance généré

    Raises:
        PrescriptionError: Si la génération échoue
        ValueError: Si les paramètres sont invalides
    """
    logger = get_logger()

    # Validation des entrées
    if not case:
        raise ValueError("Le cas clinique (case) est requis")
    if not recommendation:
        raise ValueError("La recommandation (recommendation) est requise")
    if not doctor_name or not doctor_name.strip():
        raise ValueError("Le nom du médecin est requis")

    # Sanitization basique du nom du médecin (éviter injection)
    doctor_name = doctor_name.strip()[:100]  # Limite raisonnable

    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "ordonnances"

    output_dir = Path(output_dir)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        log_error_with_context(e, "création répertoire ordonnances", {"output_dir": str(output_dir)})
        raise PrescriptionError(f"Impossible de créer le répertoire {output_dir}: permission refusée") from e
    except OSError as e:
        log_error_with_context(e, "création répertoire ordonnances", {"output_dir": str(output_dir)})
        raise PrescriptionError(f"Erreur système lors de la création de {output_dir}") from e

    # Nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ordonnance_{timestamp}.txt"
    filepath = output_dir / filename

    # Générer le contenu
    try:
        content = _format_prescription(case, recommendation, doctor_name)
    except Exception as e:
        log_error_with_context(e, "formatage ordonnance", {"doctor": doctor_name})
        raise PrescriptionError(f"Erreur lors du formatage de l'ordonnance: {e}") from e

    # Écrire le fichier
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Ordonnance générée: {filepath}")
    except PermissionError as e:
        log_error_with_context(e, "écriture ordonnance", {"filepath": str(filepath)})
        raise PrescriptionError(f"Permission refusée pour écrire {filepath}") from e
    except OSError as e:
        log_error_with_context(e, "écriture ordonnance", {"filepath": str(filepath)})
        raise PrescriptionError(f"Erreur système lors de l'écriture: {e}") from e

    return filepath


def _format_prescription(
    case: HeadacheCase,
    recommendation: ImagingRecommendation,
    doctor_name: str
) -> str:
    """Formate le contenu de l'ordonnance au format français officiel.

    Args:
        case: Cas clinique
        recommendation: Recommandation d'imagerie
        doctor_name: Nom du prescripteur

    Returns:
        Contenu formaté de l'ordonnance
    """
    date_str = datetime.now().strftime("%d/%m/%Y")
    age_str = f"{case.age} ans" if case.age is not None else "Non renseigné"
    sex_str = _format_sex(case.sex)

    # Largeur de l'ordonnance (simulant A5/ordonnancier)
    width = 60

    lines = []

    # ══════════════════════════════════════════════════════════════════════
    # EN-TÊTE MÉDECIN (coin supérieur gauche)
    # ══════════════════════════════════════════════════════════════════════
    lines.extend([
        "┌" + "─" * (width - 2) + "┐",
        "│" + " " * (width - 2) + "│",
        "│" + f"  {doctor_name}".ljust(width - 2) + "│",
        "│" + "  Médecin".ljust(width - 2) + "│",
        "│" + "  N° RPPS : _______________".ljust(width - 2) + "│",
        "│" + "  ".ljust(width - 2) + "│",
        "│" + "  Adresse du cabinet :".ljust(width - 2) + "│",
        "│" + "  ______________________________".ljust(width - 2) + "│",
        "│" + "  ______________________________".ljust(width - 2) + "│",
        "│" + "  Tél : ____________________".ljust(width - 2) + "│",
        "│" + " " * (width - 2) + "│",
        "├" + "─" * (width - 2) + "┤",
    ])

    # ══════════════════════════════════════════════════════════════════════
    # DATE ET LIEU
    # ══════════════════════════════════════════════════════════════════════
    lines.extend([
        "│" + " " * (width - 2) + "│",
        "│" + f"  Le {date_str}".ljust(width - 2) + "│",
        "│" + " " * (width - 2) + "│",
    ])

    # ══════════════════════════════════════════════════════════════════════
    # INFORMATIONS PATIENT
    # ══════════════════════════════════════════════════════════════════════
    lines.extend([
        "│" + "  PATIENT :".ljust(width - 2) + "│",
        "│" + "  Nom : ____________________".ljust(width - 2) + "│",
        "│" + "  Prénom : _________________".ljust(width - 2) + "│",
        "│" + f"  Âge : {age_str}".ljust(width - 2) + "│",
        "│" + f"  Sexe : {sex_str}".ljust(width - 2) + "│",
    ])

    # Contexte grossesse si applicable
    if case.pregnancy_postpartum:
        trimester_str = f"T{case.pregnancy_trimester}" if case.pregnancy_trimester else ""
        lines.append("│" + f"  Grossesse : Oui {trimester_str}".ljust(width - 2) + "│")

    lines.extend([
        "│" + " " * (width - 2) + "│",
        "├" + "─" * (width - 2) + "┤",
    ])

    # ══════════════════════════════════════════════════════════════════════
    # CORPS DE L'ORDONNANCE
    # ══════════════════════════════════════════════════════════════════════
    lines.extend([
        "│" + " " * (width - 2) + "│",
        "│" + "           ORDONNANCE".center(width - 2) + "│",
        "│" + " " * (width - 2) + "│",
    ])

    # Examens prescrits
    if recommendation.imaging and "aucun" not in recommendation.imaging:
        for exam in recommendation.imaging:
            exam_name = _format_exam_name(exam)
            lines.append("│" + f"  • {exam_name}".ljust(width - 2) + "│")
        lines.append("│" + " " * (width - 2) + "│")

        # Degré d'urgence
        urgency_text = {
            "immediate": "EN URGENCE (dans les heures)",
            "urgent": "URGENT (sous 24h)",
            "delayed": "Sous 7 jours",
            "none": "Non urgent"
        }
        urgency = urgency_text.get(recommendation.urgency, "")
        if urgency:
            lines.append("│" + f"  Délai : {urgency}".ljust(width - 2) + "│")
            lines.append("│" + " " * (width - 2) + "│")
    else:
        lines.extend([
            "│" + "  Pas d'examen d'imagerie requis.".ljust(width - 2) + "│",
            "│" + " " * (width - 2) + "│",
        ])

    # ══════════════════════════════════════════════════════════════════════
    # RENSEIGNEMENTS CLINIQUES
    # ══════════════════════════════════════════════════════════════════════
    lines.append("│" + "  Renseignements cliniques :".ljust(width - 2) + "│")

    clinical_info = _format_clinical_indication(case)
    # Découper en lignes de max 54 caractères
    for line in _wrap_text(clinical_info, width - 6):
        lines.append("│" + f"  {line}".ljust(width - 2) + "│")

    lines.append("│" + " " * (width - 2) + "│")

    # ══════════════════════════════════════════════════════════════════════
    # PRÉCAUTIONS SPÉCIALES
    # ══════════════════════════════════════════════════════════════════════
    precautions = []

    if case.pregnancy_postpartum:
        precautions.append("⚠ Grossesse : éviter gadolinium")
        if recommendation.urgency != "immediate":
            precautions.append("  Privilégier IRM sans injection")

    if case.sex == "F" and case.age is not None and case.age < 50 and not case.pregnancy_postpartum:
        # Vérifier si scanner prescrit
        has_scanner = any("scanner" in exam.lower() for exam in (recommendation.imaging or []))
        if has_scanner:
            precautions.append("⚠ Femme en âge de procréer :")
            precautions.append("  Test de grossesse avant scanner")

    if case.age is not None and case.age > 60:
        has_injection = any("injection" in exam.lower() or "gadolinium" in exam.lower()
                           for exam in (recommendation.imaging or []))
        if has_injection:
            precautions.append("⚠ Patient > 60 ans :")
            precautions.append("  Vérifier fonction rénale")

    if precautions:
        lines.append("│" + "  Précautions :".ljust(width - 2) + "│")
        for p in precautions:
            lines.append("│" + f"  {p}".ljust(width - 2) + "│")
        lines.append("│" + " " * (width - 2) + "│")

    # ══════════════════════════════════════════════════════════════════════
    # SIGNATURE
    # ══════════════════════════════════════════════════════════════════════
    lines.extend([
        "│" + " " * (width - 2) + "│",
        "│" + " " * (width - 2) + "│",
        "│" + "  Signature et cachet :".ljust(width - 2) + "│",
        "│" + " " * (width - 2) + "│",
        "│" + " " * (width - 2) + "│",
        "│" + " " * (width - 2) + "│",
        "│" + " " * (width - 2) + "│",
        "└" + "─" * (width - 2) + "┘",
    ])

    return "\n".join(lines)


def _wrap_text(text: str, max_width: int) -> list:
    """Découpe un texte en lignes de largeur maximale."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_width:
            current_line += (" " if current_line else "") + word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines if lines else [""]


def _format_sex(sex: str) -> str:
    """Formate le sexe pour l'affichage."""
    mapping = {"M": "Masculin", "F": "Féminin", "Other": "Autre"}
    return mapping.get(sex, sex)


def _format_clinical_indication(case: HeadacheCase) -> str:
    """Génère l'indication clinique."""
    indications = []
    
    # Profil
    if case.profile == "acute":
        indications.append("Céphalée aiguë")
    elif case.profile == "subacute":
        indications.append("Céphalée subaiguë")
    elif case.profile == "chronic":
        indications.append("Céphalée chronique")
    
    # Onset
    if case.onset == "thunderclap":
        indications.append("Début brutal en coup de tonnerre")
    elif case.onset == "progressive":
        indications.append("Début progressif")
    
    # Red flags
    if case.fever:
        indications.append("Fièvre associée")
    if case.meningeal_signs:
        indications.append("Signes méningés")
    if case.neuro_deficit:
        indications.append("Déficit neurologique")
    if case.seizure:
        indications.append("Crise comitiale")
    if case.htic_pattern:
        indications.append("Signes d'HTIC")
    
    # Contextes
    if case.trauma:
        indications.append("Contexte traumatique")
    if case.immunosuppression:
        indications.append("Patient immunodéprimé")
    
    if indications:
        return "Céphalée. " + ". ".join(indications) + "."
    return "Céphalée à explorer."


def _format_exam_name(exam: str) -> str:
    """Formate le nom de l'examen pour l'ordonnance."""
    exam_names = {
        "scanner_cerebral_sans_injection": "Scanner cérébral sans injection",
        "scanner_cerebral_avec_injection": "Scanner cérébral avec injection",
        "irm_cerebrale": "IRM cérébrale",
        "IRM_cerebrale": "IRM cérébrale",
        "IRM_cerebrale_avec_gadolinium": "IRM cérébrale avec gadolinium",
        "angio_irm_veineuse": "Angio-IRM veineuse",
        "angio_irm": "Angio-IRM",
        "ARM_cerebrale": "Angio-IRM artérielle cérébrale",
        "venographie_IRM": "Vénographie IRM",
        "angioscanner_cerebral": "Angioscanner cérébral",
        "angioscanner": "Angioscanner",
        "ponction_lombaire": "Ponction lombaire",
        "irm_rachis": "IRM du rachis",
        "doppler_TSA": "Doppler des troncs supra-aortiques",
        "angioscanner_TSA": "Angioscanner des troncs supra-aortiques",
        "echographie_arteres_temporales": "Échographie des artères temporales",
        "biopsie_artere_temporale": "Biopsie de l'artère temporale",
        "fond_oeil": "Fond d'œil",
    }
    
    return exam_names.get(exam, exam.replace("_", " ").title())
