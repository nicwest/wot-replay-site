from flask.ext.wtf import Form
from flask.ext.uploads import UploadSet
from wtforms import TextField, BooleanField, PasswordField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Required


class LoginForm(Form):
    openid = TextField('openid', validators=[Required()])
    server = SelectField('server', choices=[
        ('http://eu.wargaming.net/id/', 'EU'),
        ('http://ru.wargaming.net/id/', 'RU'),
        ('http://na.wargaming.net/id/', 'NA'),
        ('http://kr.wargaming.net/id/', 'KR'),
        ('http://asia.wargaming.net/id/', 'SEA')])
    remember_me = BooleanField('remember_me', default=False)

