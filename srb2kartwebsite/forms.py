from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, IntegerField, SelectField
from wtforms.fields.core import RadioField
from wtforms.validators import DataRequired, Length

class SkinShopForm(FlaskForm):
    """Form that lets users donate points to a skin."""
    pointsDonating = IntegerField('Points to donate', [DataRequired()])
    chosenServer = SelectField('Server to deduct points from', [DataRequired()])
    skinsRadio =RadioField('Skins', choices=[])

    #recaptcha = RecaptchaField()
    submit = SubmitField('Donate')