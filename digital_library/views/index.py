from flask import Blueprint, render_template, current_app, request, abort
from digital_library.db import *

index_router = Blueprint('index', __name__, template_folder='templates')


@index_router.route('/')
def index():
    try:
        page = int(request.args.get('page', 0))
        if page < 0:
            abort(400, description="The page can't be less than 0")
    except ValueError:
        abort(404, description='Page is not found')

    materials = (
        MATERIAL
        .select()
        .paginate(page, current_app.config['MATERIALS_PER_PAGE'])
        .prefetch(MATERIAL.tags.get_through_model(),
                  MATERIAL.authors.get_through_model())
    )

    return render_template('index.html', materials=materials, page=page)


@index_router.errorhandler(404)
def page_not_found(message):
    return render_template('handler404.html', data=message), 404


@index_router.route('/material/<int:material_id>')
def material_overview(material_id=None):
    try:
        page = int(request.args.get('page', 0))
        if page < 0:
            abort(400, description="The page can't be less than 0")
    except ValueError:
        abort(404, description='Page is not found')

    if material_id is None:
        abort(404, "No such material exists!")

    try:
        # Retrieve the material from DB
        material = (MATERIAL
                    .select()
                    .where(MATERIAL.id == material_id)
                    .prefetch(COMMENT,
                              ATTACHMENT,
                              MATERIAL.tags.get_through_model(),
                              MATERIAL.authors.get_through_model(),
                              REVIEW
                              )
                    )[0]
        # This object can be used in templates as material.<attribute_name>
    except (MATERIAL.DoesNotExist, IndexError):
        abort(404, "No such material exists!")

    return render_template('material.html', material=material, page=page,
                           comments_per_page=current_app.config["COMMENTS_PER_PAGE"])
