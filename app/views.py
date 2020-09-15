# from https://computableverse.com/blog/flask-admin-using-basicauth

from flask import redirect
from flask_admin.contrib import sqla
from app import basic_auth

from .exceptions import AuthException

class UserView(sqla.ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())

    can_create = False
    column_exclude_list = ['password', ]
    column_searchable_list = ['email_address']
    column_filters = ['email_address', 'registered_on', 'verified']
    column_editable_list = ['approved']
    form_excluded_columns = ['password', 'registered_on', 'email_verification_token', 'password_reset_token']
