import json
from datetime import datetime

from fastapi import APIRouter, Depends, Path, Body, Query
from fastapi import status as http_status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from jotform import JotformAPIClient
from api import models
from api import schemas
from api.db.session import get_db
from api.repositories.financials import get_links_by_user_id, get_regime_by_user_id
from api.repositories.fiscal import (
    validate_submitted_anual_declaration,
    user_declaration,
)
from api.repositories.plans import get_products, product_by_id
from api.repositories.users import get_link_form, user_form_submission
from api.utils.anual_declaration import (
    done_declaration,
    to_do_declaration,
    anual_retool,
)

router = APIRouter()


@router.get("/{milestone_id}/status/{status_id}")
def description_status_milestone(
    milestone_id: int = Path(...),
    status_id: int = Path(...),
    db: Session = Depends(get_db),
):
    status = db.query(models.StatusDeclaration).filter_by(id=milestone_id).first()
    if status is None:
        return JSONResponse(
            status_code=http_status.HTTP_404_NOT_FOUND,
            content={"message": "Milestone not found"},
        )

    status_description = status.done
    if status_id == 1:
        status_description = status.unmade
    elif status_id == 2:
        status_description = status.progress
    else:
        status_id = 3

    milestone = db.query(models.Milestones).filter_by(id=milestone_id).first()
    milestone.description = status_description
    milestone.priority = status_id

    return milestone


@router.get("/user/{user_id}")
def validator_anual_declaration(
    user_id: int = Path(...),
):
    # si el usuario adquirio alguno de los productos de declaracion entra al flujo de milestones de declaracion
    product_list = [
        "declaración_anual_basica",
        "declaración_anual_compleja",
        "declaración_anualbasica_regubasica",
        "decla_anualcomp_regubasica",
        "decla_anualcomp_regucomp",
    ]

    response = {"validator": False, "products": []}
    products = get_products(user_id)

    if products:
        for item in products:
            if "product" in item:
                if "slug" in item["product"]:
                    if item["product"]["slug"] in product_list:
                        information = {"info": item, "slug": item["product"]["slug"]}
                        response["validator"] = True
                        if "additional_information" in item:
                            if "year" in item["additional_information"]:
                                information["year"] = item["additional_information"][
                                    "year"
                                ]
                                information["name"] = "Declaración anual " + str(
                                    information["year"]
                                )

                            if "regimes" in item["additional_information"]:
                                information["regimes"] = item["additional_information"][
                                    "regimes"
                                ]

                            for index, regime in enumerate(information["regimes"]):
                                information["regimes"][index] = regime.upper()

                            year_found = list(
                                filter(
                                    lambda x: x["year"] == information["year"],
                                    response["products"],
                                )
                            )
                            if year_found and year_found[0]:
                                for regime in information["regimes"]:
                                    if regime not in year_found[0]["regimes"]:
                                        year_found[0]["regimes"].append(regime)
                            else:
                                response["products"].append(information)

    return response


@router.get("/steps/user/{user_id}")
async def milestones_declaration(
    user_id: int = Path(...),
    home: bool = Query(False),
    db: Session = Depends(get_db),
):
    anual_declaration_steps = []

    years_to_declare = validator_anual_declaration(user_id)
    if "products" in years_to_declare:
        for information in years_to_declare["products"]:
            result = await declarations_steps(
                years_to_declare["validator"], user_id, information, home, db
            )
            anual_declaration_steps.append(result)

    anual_declaration_steps = sorted(anual_declaration_steps, key=lambda x: x["year"])

    return anual_declaration_steps


async def declarations_steps(
    validator,
    user_id,
    information,
    home,
    db: Session = Depends(get_db),
):
    period = information["year"] if "year" in information else None
    regime = information["regimes"] if "regimes" in information else None
    steps = []
    result = {
        "name": "Declaración anual " + str(period),
        "regimes": regime,
        "year": period,
        "acquisition": information["info"],
    }

    # contratar declaracion
    status = description_status_milestone(1, 1, db)
    check = False
    show = True
    if validator:
        status = description_status_milestone(1, 3, db)
        check = True

    information = {
        "id": status.id,
        "description": status.description,
        "slug": status.slug,
        "status": status.priority,
        "check": check,
        "show": show,
    }
    steps.append(information)

    # si el usuario no ha adquirido ningun producto de declaracion
    if home is False and validator is False and period == (datetime.now().year - 1):
        count = 0
        for item in steps:
            if item["check"]:
                count += 1

        result["tasks"] = steps
        result["done"] = count
        result["to_do"] = len(steps)
        result["milestone_finished"] = True if count == len(steps) else False
        return result

    # vincular rfc
    status = description_status_milestone(2, 1, db)
    check = False
    show = True

    rfc = await get_links_by_user_id(user_id)

    if rfc:
        if rfc[0] == "ACTIVE" or rfc[0] == "active":
            if rfc[1]:
                status = description_status_milestone(2, 3, db)
                check = True
        else:
            rfc = get_link_form(user_id)
            if rfc:
                status = description_status_milestone(2, 2, db)

    information = {
        "id": status.id,
        "description": status.description,
        "slug": status.slug,
        "status": status.priority,
        "check": check,
        "show": show,
    }
    steps.append(information)

    # declaraciones atrasadas
    status = description_status_milestone(3, 1, db)
    check = False
    show = False

    regime_user = await get_regime_by_user_id(user_id)

    if regime_user:
        for regime in regime_user:
            if (
                regime["name"]
                == "Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas"
            ):
                show = True
                regularization_status = await declaration_status(user_id, period)
                if regularization_status:
                    done = done_declaration(regularization_status)
                    if done:
                        status = description_status_milestone(3, 3, db)
                        check = True
                    else:
                        to_do = to_do_declaration(regularization_status)
                        if to_do:
                            status = description_status_milestone(3, 2, db)

    information = {
        "id": status.id,
        "description": status.description,
        "slug": status.slug,
        "status": status.priority,
        "check": check,
        "show": show,
    }
    steps.append(information)

    '''"""logic hpal"""
    regularization = (
        db.query(models.Regularizations).filter_by(user_id=user_id, year=period).all()
    )
    if regularization:
        regularization_pendents = all(
            resultant.status == 2 for resultant in regularization
        )
        if regularization_pendents:
            status = description_status_milestone(3, 2, db)
        regularization_done = all(resultant.status == 3 for resultant in regularization)
        if regularization_done:
            status = description_status_milestone(3, 3, db)
            check = True
            if slug and slug in [
                "declaración_anual_basica",
                "declaración_anual_compleja",
            ]:
                show = False

    information = {
        "id": status.id,
        "description": status.description,
        "slug": status.slug,
        "status": status.priority,
        "check": check,
        "show": show,
    }
    steps.append(information)'''

    """# pago de impuestos (pendiente)
    status = description_status_milestone(4, 1, db)
    check = False
    show = True

    information = {
        "id": status.id,
        "description": status.description,
        "slug": status.slug,
        "status": status.priority,
        "check": check,
        "show": show,
    }
    steps.append(information)"""

    # preferencia de saldo a favor
    status = description_status_milestone(5, 1, db)
    check = False
    show = True

    form = user_form_submission(user_id, "f98c5c8b-adb7-4cbc-a0de-cb60f9a062d4")
    if form:
        if "user_submission" in form and form["user_submission"]:
            status = description_status_milestone(5, 3, db)
            check = True

    jotform_api = JotformAPIClient("58f134157b0f1ffdb99aef836912810d")
    submission_filter = {"form_id": "230466647088061"}
    submission = jotform_api.get_submissions(0, 0, submission_filter, "")

    for request in submission:
        if request["answers"]["3"]["answer"] == str(user_id):
            status = description_status_milestone(5, 3, db)
            check = True

    information = {
        "id": status.id,
        "description": status.description,
        "slug": status.slug,
        "status": status.priority,
        "check": check,
        "show": show,
    }
    steps.append(information)

    # count task done
    count = 0
    for item in steps:
        if item["check"]:
            count += 1

    # presentar declaracion
    status = description_status_milestone(6, 2, db)
    check = False
    show = True

    steps_validator = 3
    if "PLATAFORMAS TECNOLÓGICAS" in regime:
        steps_validator = 4

    if count == steps_validator:
        # en marzo y abril se muestran descripciones especificas
        if datetime.now().month == 3:
            status.description = "Todo listo para presentar tu declaración en Abril"
        if datetime.now().month == 4:
            status.description = (
                "Estamos trabajando en tu declaración anual" + " " + str(period)
            )
    else:
        if datetime.now().month == 3:
            status.description = "Completa los pasos pendientes antes de abril"
        if datetime.now().month == 4:
            status.description = "Completa los pasos pendientes antes del 20 abril"

    submitted = await validate_submitted_anual_declaration(user_id, period)
    if submitted and "declaration_submitted" in submitted:
        if submitted["declaration_submitted"]:
            status = description_status_milestone(6, 3, db)
            check = True

    submitted = await anual_retool(user_id, period)
    if submitted == 12:
        status = description_status_milestone(6, 3, db)
        check = True

    information = {
        "id": status.id,
        "description": status.description,
        "slug": status.slug,
        "status": status.priority,
        "check": check,
        "show": show,
    }
    steps.append(information)

    for step in steps:
        if step["slug"] == "presentar_declaracion":
            if step["check"] is True:
                for aux in steps:
                    if aux["slug"] != "preferencia_saldo":
                        info = description_status_milestone(aux["id"], 3, db)
                        aux["check"] = True
                        aux["description"] = info.description

    # count task done
    count = 0
    for item in steps:
        if item["check"]:
            count += 1

    result["tasks"] = steps
    result["done"] = count
    result["to_do"] = len(steps)
    result["milestone_finished"] = True if count == len(steps) else False

    result["message"] = "Todo listo para presentar tu declaración anual"
    result["message_description"] = "Todo listo para presentar tu declaración anual"
    if datetime.now().month == 3:
        result["message"] = "Todo listo para presentar en abril" + " " + str(period)
    if datetime.now().month == 4:
        result["message"] = "Trabajando en tu declaración"
    if result["milestone_finished"] is False:
        result["message"] = "Tienes acciones pendientes"
        result["message_description"] = "Completa y presenta tu declaración anual"

    return result


@router.post("/regularizations")
def regularizations_hpal(
    payload: schemas.declaration.Regularizations = Body(...),
    db: Session = Depends(get_db),
):
    regularization = (
        db.query(models.Regularizations)
        .filter_by(
            user_id=payload.user_id,
            regimes=payload.regimes,
            year=payload.year,
            periodicity=payload.periodicity,
        )
        .first()
    )
    if not regularization:
        payload.additional_information = (
            json.dumps(payload.additional_information)
            if payload.additional_information
            else None
        )
        regularization = models.Regularizations(**payload.dict())
    else:
        regularization.status = payload.status
        regularization.pending = payload.pending
        regularization.paid = payload.paid

    if regularization.paid == [
        "ene",
        "feb",
        "mar",
        "abr",
        "mayo",
        "jun",
        "jul",
        "ago",
        "sept",
        "oct",
        "nov",
        "dic",
    ]:
        regularization.status = 3
    if regularization.paid == ["trim1", "trim2", "trim3", "trim4"]:
        regularization.status = 3

    db.add(regularization)
    db.commit()

    information = {
        "id": regularization.id,
        "user_id": regularization.user_id,
        "year": regularization.year,
        "status": regularization.status,
        "regimes": regularization.regimes,
        "pending": regularization.pending,
        "paid": regularization.paid,
        "periodicity": regularization.periodicity,
        "additional_information": regularization.additional_information,
    }

    return information


@router.get("/regularizations/user/{user_id}")
def regularizations_hpal(
    regime: str = Query(None),
    year: int = Query(None),
    user_id: int = Path(...),
    db: Session = Depends(get_db),
):
    response = []
    regularization = (
        db.query(models.Regularizations)
        .filter_by(user_id=user_id, regimes=regime, year=year)
        .first()
    )
    if regularization:
        information = {
            "year": regularization.year,
            "regimes": regularization.regimes,
            "periodicity": regularization.periodicity,
            "pending": regularization.pending,
            "paid": regularization.paid,
        }
        response.append(information)
        return response
    else:
        return {"message": "No hay información para este usuario"}


@router.get("/status/user/{user_id}/period/{year}")
async def declaration_status(
    user_id: int = Path(...),
    year: int = Path(...),
):
    declaration = await user_declaration(user_id)
    if declaration:
        regularization_period = list(
            filter(lambda x: x["year"] == year, declaration["periods"])
        )
        regularization_period.sort(key=lambda x: (x["month"]))
        return regularization_period
    return None


@router.get("/discount_milestone/product/{product_id}/quantity/{quantity}")
def discount_regularization(
    product_id: int = Path(...),
    quantity: int = Path(...),
):
    base_price = product_by_id(product_id)
    if base_price:
        base_price = base_price["product_versions"][0]["price"]

    if quantity <= 0:
        return 0
    elif quantity <= 4:
        discount = 0.05
    elif quantity <= 9:
        discount = 0.1
    elif quantity <= 14:
        discount = 0.15
    elif quantity <= 23:
        discount = 0.25
    elif quantity <= 36:
        discount = 0.35
    else:
        discount = 0.4

    precio_total = quantity * base_price
    descuento_total = precio_total * discount
    precio_con_descuento = precio_total - descuento_total

    return {
        "base_price": precio_total,
        "discount": int((discount * 100)),
        "total_price": precio_con_descuento,
    }
