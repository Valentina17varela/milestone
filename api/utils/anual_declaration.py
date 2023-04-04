from fastapi import Depends
from sqlalchemy.orm import Session
from itertools import groupby
from api import models
from api.db.session import get_db
from api.repositories.fiscal import user_declaration, validate_acuse_retool


def to_do_declaration(regularization_status: list):
    # order list for year y month
    regularization_status.sort(key=lambda x: (x["year"], x["month"]))
    # removes repeated items by month and year
    regularization_status = [
        next(value)
        for key, value in groupby(
            regularization_status, lambda x: (x["year"], x["month"])
        )
    ]
    # only show the elements of the year
    regularization_status = [
        acuse for acuse in regularization_status if acuse["obligation_existed"] is True
    ]

    regularization_acquired = all(
        resultant["acquired"] is True for resultant in regularization_status
    )

    if all(
        [
            regularization_acquired,
        ]
    ):
        return True
    else:
        return False


def done_declaration(regularization_status: list):
    regularization_presented = all(
        resultant["presented"] is True for resultant in regularization_status
    )

    if regularization_presented:
        return True
    else:
        return False


async def anual_retool(user_id: int, year: int):
    acuses = await validate_acuse_retool(user_id)
    if acuses:
        # ordena la lista por user_id, year y month
        acuses.sort(key=lambda x: (x["user_id"], x["year"], x["month"]))

        # removes repeated items by user_id , month and year
        acuses = [
            next(value)
            for key, value in groupby(
                acuses, lambda x: (x["user_id"], x["year"], x["month"])
            )
        ]

        # only show the elements of the year
        acuses = [acuse for acuse in acuses if acuse["year"] == year]

        month_declared = len(acuses)

        return month_declared
    else:
        return None
